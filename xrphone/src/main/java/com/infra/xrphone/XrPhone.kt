package com.infra.xrphone

import android.app.Activity
import android.content.Context
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI
import java.util.concurrent.atomic.AtomicBoolean

/**
 * XrPhone central facade:
 * - Controls XR session lifecycle
 * - Bridges to native OpenXR/Vulkan via JNI
 * - Streams pose/state to InfraNet
 * - Exposes hooks for Unity / Compose XR
 */
class XrPhone(
    private val context: Context,
    private val infraEndpoint: String,
    private val deviceId: String,
    private val lifecycleOwner: LifecycleOwner
) {

    enum class SessionState { IDLE, INIT, RUNNING, ERROR, CLOSED }

    private val scope: CoroutineScope = lifecycleOwner.lifecycleScope
    @Volatile
    var state: SessionState = SessionState.IDLE
        private set

    private var wsClient: WebSocketClient? = null
    private val wsConnected = AtomicBoolean(false)
    private var poseJob: Job? = null

    init {
        // Map lifecycle to XR/OpenXR hooks
        lifecycleOwner.lifecycle.addObserver(XrLifecycleObserver(
            onResume = { onResume() },
            onPause = { onPause() },
            onDestroy = { shutdown() }
        ))
    }

    /** Public API: start full XR session (OpenXR + InfraNet). */
    fun startSession() {
        if (state == SessionState.RUNNING || state == SessionState.INIT) return
        state = SessionState.INIT

        // 1) init OpenXR + Vulkan via JNI
        val nativeOk = initOpenXrAndVulkanNative(context)
        if (!nativeOk) {
            state = SessionState.ERROR
            return
        }

        // 2) connect InfraNet
        connectInfraNet()

        // 3) start pose streaming once WS is ready
        poseJob = scope.launch(Dispatchers.Default) {
            waitForWs()
            startPoseLoop()
        }
    }

    /** Public API: stop XR session. */
    fun stopSession() {
        poseJob?.cancel()
        wsClient?.close()
        wsConnected.set(false)
        shutdownOpenXrNative()
        state = SessionState.CLOSED
    }

    /** Hook for Activity.onResume -> resumes OpenXR session. */
    fun onResume() {
        if (state == SessionState.RUNNING) {
            resumeOpenXrNative()
        }
    }

    /** Hook for Activity.onPause -> pauses OpenXR session. */
    fun onPause() {
        if (state == SessionState.RUNNING) {
            pauseOpenXrNative()
        }
    }

    /** Called when lifecycleOwner is destroyed. */
    fun shutdown() {
        stopSession()
    }

    /** DOM shift request: InfraNet + local XR scene router. */
    fun requestDomShift(targetSceneId: String, reason: String) {
        if (!wsConnected.get()) return
        val payload = """{
          "type":"domShiftRequest",
          "deviceId":"$deviceId",
          "targetScene":"$targetSceneId",
          "reason":"$reason"
        }""".trimIndent()
        wsClient?.send(payload)
        // TODO: route to local scene controller in native/Unity/Compose
    }

    // ---- InfraNet networking ----

    private fun connectInfraNet() {
        try {
            val uri = URI(infraEndpoint)
            wsClient = object : WebSocketClient(uri) {
                override fun onOpen(handshakedata: ServerHandshake) {
                    wsConnected.set(true)
                    state = SessionState.RUNNING
                    sendHello()
                }

                override fun onMessage(message: String?) {
                    if (message == null) return
                    handleInfraMessage(message)
                }

                override fun onClose(code: Int, reason: String?, remote: Boolean) {
                    wsConnected.set(false)
                    if (state != SessionState.CLOSED) state = SessionState.ERROR
                }

                override fun onError(ex: Exception?) {
                    state = SessionState.ERROR
                }
            }
            wsClient?.connect()
        } catch (e: Exception) {
            state = SessionState.ERROR
        }
    }

    private fun sendHello() {
        val payload = """{
          "type":"hello",
          "deviceId":"$deviceId",
          "capabilities":["openxr","vulkan","compose_xr","unity_bridge"]
        }""".trimIndent()
        if (wsConnected.get()) {
            wsClient?.send(payload)
        }
    }

    private fun handleInfraMessage(message: String) {
        // Minimal handling of remote DOM shift / config updates
        // e.g., {"type":"domShift","targetScene":"CITY_TWIN"}
        // TODO: JSON parse + delegate to scene router
    }

    private suspend fun waitForWs() {
        var count = 0
        while (!wsConnected.get() && count < 100) {
            kotlinx.coroutines.delay(50)
            count++
        }
    }

    private fun startPoseLoop() {
        // This should pull poses from native OpenXR every frame and send to InfraNet
        while (state == SessionState.RUNNING && wsConnected.get()) {
            val pose = getHeadPoseNative()
            val payload = """{
              "type":"pose",
              "deviceId":"$deviceId",
              "ts":${pose.timestampNs},
              "position":[${pose.px},${pose.py},${pose.pz}],
              "orientation":[${pose.qx},${pose.qy},${pose.qz},${pose.qw}]
            }""".trimIndent()
            wsClient?.send(payload)
            Thread.sleep(11) // ~90 Hz
        }
    }

    // ---- Unity integration entrypoints ----

    /**
     * Called from Unity Android plugin to bind this XR Phone to a Unity OpenXR scene.
     */
    fun attachUnitySession(activity: Activity) {
        // Unity provides its OpenXR session; use InfraNet + DOM shift from here.
        // Example: store ref to activity, configure callbacks for domShift events.
    }

    // ---- Native JNI bridges for OpenXR + Vulkan ----

    private external fun initOpenXrAndVulkanNative(context: Context): Boolean
    private external fun resumeOpenXrNative()
    private external fun pauseOpenXrNative()
    private external fun shutdownOpenXrNative()
    private external fun getHeadPoseNative(): HeadPose

    data class HeadPose(
        val timestampNs: Long,
        val px: Float,
        val py: Float,
        val pz: Float,
        val qx: Float,
        val qy: Float,
        val qz: Float,
        val qw: Float
    )

    companion object {
        init {
            System.loadLibrary("xrphone_native") // libxrphone_native.so
        }
    }
}
