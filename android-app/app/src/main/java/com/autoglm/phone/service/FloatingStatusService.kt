package com.autoglm.phone.service

import android.annotation.SuppressLint
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.TextView
import kotlinx.coroutines.*

/**
 * Floating overlay service that shows current automation status at the bottom of screen.
 */
class FloatingStatusService : Service() {
    
    companion object {
        const val ACTION_UPDATE_STATUS = "com.autoglm.phone.UPDATE_STATUS"
        const val ACTION_HIDE = "com.autoglm.phone.HIDE_STATUS"
        const val EXTRA_STATUS = "status"
        
        private var instance: FloatingStatusService? = null
        fun getInstance(): FloatingStatusService? = instance
        
        fun updateStatus(context: Context, status: String) {
            val intent = Intent(context, FloatingStatusService::class.java).apply {
                action = ACTION_UPDATE_STATUS
                putExtra(EXTRA_STATUS, status)
            }
            context.startService(intent)
        }
        
        fun hide(context: Context) {
            val intent = Intent(context, FloatingStatusService::class.java).apply {
                action = ACTION_HIDE
            }
            context.startService(intent)
        }
    }
    
    private var windowManager: WindowManager? = null
    private var floatingView: View? = null
    private var statusText: TextView? = null
    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var hideJob: Job? = null
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_UPDATE_STATUS -> {
                val status = intent.getStringExtra(EXTRA_STATUS) ?: return START_NOT_STICKY
                showStatus(status)
            }
            ACTION_HIDE -> {
                hideStatus()
            }
        }
        return START_NOT_STICKY
    }
    
    override fun onDestroy() {
        super.onDestroy()
        instance = null
        hideStatus()
        serviceScope.cancel()
    }
    
    @SuppressLint("InflateParams")
    private fun showStatus(status: String) {
        hideJob?.cancel()
        
        if (floatingView == null) {
            createFloatingView()
        }
        
        statusText?.text = "🤖 $status"
        
        // Auto-hide after 5 seconds if not updated
        hideJob = serviceScope.launch {
            delay(5000)
            hideStatus()
        }
    }
    
    @SuppressLint("InflateParams")
    private fun createFloatingView() {
        try {
            // Create TextView programmatically
            val textView = TextView(this).apply {
                setBackgroundColor(0xCC1A1A2E.toInt())
                setTextColor(0xFFFFFFFF.toInt())
                textSize = 14f
                setPadding(32, 16, 32, 16)
                gravity = Gravity.CENTER
                maxLines = 1
            }
            statusText = textView
            floatingView = textView
            
            val layoutParams = WindowManager.LayoutParams().apply {
                width = WindowManager.LayoutParams.MATCH_PARENT
                height = WindowManager.LayoutParams.WRAP_CONTENT
                type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                } else {
                    @Suppress("DEPRECATION")
                    WindowManager.LayoutParams.TYPE_PHONE
                }
                flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                        WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or
                        WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                format = PixelFormat.TRANSLUCENT
                gravity = Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL
                y = 80 // Offset from bottom
            }
            
            windowManager?.addView(floatingView, layoutParams)
        } catch (e: Exception) {
            android.util.Log.e("FloatingStatus", "Failed to create floating view: ${e.message}")
        }
    }
    
    private fun hideStatus() {
        try {
            floatingView?.let {
                windowManager?.removeView(it)
            }
        } catch (e: Exception) {
            // View might not be attached
        }
        floatingView = null
        statusText = null
    }
}
