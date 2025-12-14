package com.autoglm.phone.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Path
import android.os.Build
import android.util.Base64
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import kotlinx.coroutines.*
import java.io.ByteArrayOutputStream
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine

/**
 * Accessibility Service for controlling the phone.
 * Provides screenshot, tap, swipe, type, and navigation operations.
 */
class AutoGLMAccessibilityService : AccessibilityService() {
    
    companion object {
        private var instance: AutoGLMAccessibilityService? = null
        
        fun getInstance(): AutoGLMAccessibilityService? = instance
        
        fun isServiceEnabled(): Boolean = instance != null
    }
    
    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        android.util.Log.d("AutoGLM", "Accessibility Service connected")
    }
    
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // We don't need to process accessibility events for now
    }
    
    override fun onInterrupt() {
        android.util.Log.d("AutoGLM", "Accessibility Service interrupted")
    }
    
    override fun onDestroy() {
        super.onDestroy()
        instance = null
        serviceScope.cancel()
        android.util.Log.d("AutoGLM", "Accessibility Service destroyed")
    }
    
    // ==================== Screenshot ====================
    
    /**
     * Take a screenshot and return as Base64 encoded string.
     * Requires Android 11+ (API 30).
     */
    suspend fun takeScreenshot(): String? {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) {
            android.util.Log.e("AutoGLM", "Screenshot requires Android 11+")
            return null
        }
        
        return suspendCoroutine { continuation ->
            takeScreenshot(
                android.view.Display.DEFAULT_DISPLAY,
                mainExecutor,
                object : TakeScreenshotCallback {
                    override fun onSuccess(screenshot: ScreenshotResult) {
                        val bitmap = Bitmap.wrapHardwareBuffer(
                            screenshot.hardwareBuffer,
                            screenshot.colorSpace
                        )
                        screenshot.hardwareBuffer.close()
                        
                        if (bitmap != null) {
                            val base64 = bitmapToBase64(bitmap)
                            bitmap.recycle()
                            continuation.resume(base64)
                        } else {
                            continuation.resume(null)
                        }
                    }
                    
                    override fun onFailure(errorCode: Int) {
                        android.util.Log.e("AutoGLM", "Screenshot failed: $errorCode")
                        continuation.resume(null)
                    }
                }
            )
        }
    }
    
    private fun bitmapToBase64(bitmap: Bitmap): String {
        val outputStream = ByteArrayOutputStream()
        // Convert hardware bitmap to software bitmap for compression
        val softwareBitmap = bitmap.copy(Bitmap.Config.ARGB_8888, false)
        softwareBitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
        softwareBitmap.recycle()
        return Base64.encodeToString(outputStream.toByteArray(), Base64.NO_WRAP)
    }
    
    // ==================== Gestures ====================
    
    /**
     * Perform a tap at the given coordinates.
     * @param x X coordinate (0-screen width)
     * @param y Y coordinate (0-screen height)
     * @return true if gesture was dispatched successfully
     */
    suspend fun tap(x: Float, y: Float): Boolean {
        return performGesture(
            createTapGesture(x, y)
        )
    }
    
    /**
     * Perform a swipe from start to end coordinates.
     * @param startX Starting X coordinate
     * @param startY Starting Y coordinate  
     * @param endX Ending X coordinate
     * @param endY Ending Y coordinate
     * @param durationMs Duration of swipe in milliseconds
     * @return true if gesture was dispatched successfully
     */
    suspend fun swipe(
        startX: Float, startY: Float,
        endX: Float, endY: Float,
        durationMs: Long = 500
    ): Boolean {
        return performGesture(
            createSwipeGesture(startX, startY, endX, endY, durationMs)
        )
    }
    
    /**
     * Perform a long press at the given coordinates.
     */
    suspend fun longPress(x: Float, y: Float, durationMs: Long = 1000): Boolean {
        return performGesture(
            createLongPressGesture(x, y, durationMs)
        )
    }
    
    /**
     * Perform a double tap at the given coordinates.
     */
    suspend fun doubleTap(x: Float, y: Float): Boolean {
        tap(x, y)
        delay(100)
        return tap(x, y)
    }
    
    private fun createTapGesture(x: Float, y: Float): GestureDescription {
        val path = Path().apply {
            moveTo(x, y)
        }
        val stroke = GestureDescription.StrokeDescription(path, 0, 50)
        return GestureDescription.Builder()
            .addStroke(stroke)
            .build()
    }
    
    private fun createSwipeGesture(
        startX: Float, startY: Float,
        endX: Float, endY: Float,
        durationMs: Long
    ): GestureDescription {
        val path = Path().apply {
            moveTo(startX, startY)
            lineTo(endX, endY)
        }
        val stroke = GestureDescription.StrokeDescription(path, 0, durationMs)
        return GestureDescription.Builder()
            .addStroke(stroke)
            .build()
    }
    
    private fun createLongPressGesture(x: Float, y: Float, durationMs: Long): GestureDescription {
        val path = Path().apply {
            moveTo(x, y)
        }
        val stroke = GestureDescription.StrokeDescription(path, 0, durationMs)
        return GestureDescription.Builder()
            .addStroke(stroke)
            .build()
    }
    
    private suspend fun performGesture(gesture: GestureDescription): Boolean {
        return suspendCoroutine { continuation ->
            val result = dispatchGesture(
                gesture,
                object : GestureResultCallback() {
                    override fun onCompleted(gestureDescription: GestureDescription?) {
                        continuation.resume(true)
                    }
                    
                    override fun onCancelled(gestureDescription: GestureDescription?) {
                        continuation.resume(false)
                    }
                },
                null
            )
            if (!result) {
                continuation.resume(false)
            }
        }
    }
    
    // ==================== Navigation ====================
    
    /**
     * Press the back button.
     */
    fun pressBack(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_BACK)
    }
    
    /**
     * Press the home button.
     */
    fun pressHome(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_HOME)
    }
    
    /**
     * Open the recent apps.
     */
    fun openRecents(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_RECENTS)
    }
    
    /**
     * Open the notification shade.
     */
    fun openNotifications(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS)
    }
    
    // ==================== Text Input ====================
    
    /**
     * Type text into the currently focused input field.
     * @param text Text to type
     * @return true if text was successfully set
     */
    fun typeText(text: String): Boolean {
        val focusedNode = findFocusedEditableNode() ?: return false
        
        val arguments = android.os.Bundle().apply {
            putCharSequence(
                AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                text
            )
        }
        
        val result = focusedNode.performAction(
            AccessibilityNodeInfo.ACTION_SET_TEXT, 
            arguments
        )
        focusedNode.recycle()
        return result
    }
    
    /**
     * Clear text in the currently focused input field.
     */
    fun clearText(): Boolean {
        return typeText("")
    }
    
    private fun findFocusedEditableNode(): AccessibilityNodeInfo? {
        val root = rootInActiveWindow ?: return null
        
        // First try to find the focused node
        var focused = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
        if (focused != null && focused.isEditable) {
            return focused
        }
        focused?.recycle()
        
        // Fall back to finding any editable node that is focused
        return findEditableNode(root)
    }
    
    private fun findEditableNode(node: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        if (node.isEditable && node.isFocused) {
            return node
        }
        
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            val result = findEditableNode(child)
            if (result != null) {
                return result
            }
            child.recycle()
        }
        
        return null
    }
    
    // ==================== App Launching ====================
    
    /**
     * Launch an app by package name.
     */
    fun launchApp(packageName: String): Boolean {
        return try {
            val intent = packageManager.getLaunchIntentForPackage(packageName)
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                startActivity(intent)
                true
            } else {
                android.util.Log.e("AutoGLM", "App not found: $packageName")
                false
            }
        } catch (e: Exception) {
            android.util.Log.e("AutoGLM", "Failed to launch app: $e")
            false
        }
    }
    
    /**
     * Get screen dimensions.
     */
    fun getScreenSize(): Pair<Int, Int> {
        val displayMetrics = resources.displayMetrics
        return Pair(displayMetrics.widthPixels, displayMetrics.heightPixels)
    }
    
    /**
     * Get the current foreground app package name.
     */
    fun getCurrentApp(): String? {
        val root = rootInActiveWindow ?: return null
        val packageName = root.packageName?.toString()
        root.recycle()
        return packageName
    }
}
