package com.autoglm.phone.service

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.util.Base64
import android.util.DisplayMetrics
import android.view.WindowManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream

/**
 * Screenshot helper that works on Android 9+.
 * Uses MediaProjection API for Android 9-10, AccessibilityService for Android 11+.
 */
class ScreenshotHelper(private val context: Context) {
    
    companion object {
        const val REQUEST_MEDIA_PROJECTION = 1001
        
        @Volatile
        private var mediaProjection: MediaProjection? = null
        
        @Volatile
        private var resultCode: Int = 0
        
        @Volatile
        private var resultData: Intent? = null
        
        /**
         * Store MediaProjection permission result.
         */
        fun setMediaProjectionResult(code: Int, data: Intent?) {
            resultCode = code
            resultData = data?.clone() as? Intent
            android.util.Log.d("ScreenshotHelper", "MediaProjection result set: code=$code, data=$data")
        }
        
        fun hasMediaProjectionPermission(): Boolean {
            val has = resultCode == Activity.RESULT_OK && resultData != null
            android.util.Log.d("ScreenshotHelper", "hasMediaProjectionPermission: $has (code=$resultCode)")
            return has
        }
        
        fun clearMediaProjection() {
            try {
                mediaProjection?.stop()
            } catch (e: Exception) {
                // Ignore
            }
            mediaProjection = null
        }
    }
    
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    private val handler = Handler(Looper.getMainLooper())
    
    /**
     * Take screenshot using the best available method.
     */
    suspend fun takeScreenshot(): String? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // Android 11+ - use Accessibility Service
            takeScreenshotViaAccessibility()
        } else {
            // Android 9-10 - use MediaProjection with retry
            takeScreenshotViaMediaProjectionWithRetry()
        }
    }
    
    private suspend fun takeScreenshotViaAccessibility(): String? {
        val service = AutoGLMAccessibilityService.getInstance()
        return service?.takeScreenshot()
    }
    
    /**
     * Take screenshot with retry logic for Android 9-10.
     */
    private suspend fun takeScreenshotViaMediaProjectionWithRetry(): String? {
        // First attempt
        var result = takeScreenshotViaMediaProjection()
        
        // If failed, try recreating MediaProjection
        if (result == null) {
            android.util.Log.w("ScreenshotHelper", "First attempt failed, recreating MediaProjection...")
            clearMediaProjection()
            delay(100)
            result = takeScreenshotViaMediaProjection()
        }
        
        return result
    }
    
    /**
     * Take screenshot via MediaProjection (Android 9-10).
     */
    private suspend fun takeScreenshotViaMediaProjection(): String? = withContext(Dispatchers.Main) {
        if (!hasMediaProjectionPermission()) {
            android.util.Log.e("ScreenshotHelper", "No MediaProjection permission")
            return@withContext null
        }
        
        try {
            // Always cleanup previous resources first
            cleanupResources()
            
            val projectionManager = context.getSystemService(Context.MEDIA_PROJECTION_SERVICE) 
                as MediaProjectionManager
            
            // Create fresh MediaProjection if needed
            if (mediaProjection == null) {
                android.util.Log.d("ScreenshotHelper", "Creating new MediaProjection...")
                mediaProjection = projectionManager.getMediaProjection(resultCode, resultData!!)
                
                mediaProjection?.registerCallback(object : MediaProjection.Callback() {
                    override fun onStop() {
                        android.util.Log.d("ScreenshotHelper", "MediaProjection stopped")
                        mediaProjection = null
                    }
                }, handler)
            }
            
            val projection = mediaProjection
            if (projection == null) {
                android.util.Log.e("ScreenshotHelper", "Failed to create MediaProjection")
                return@withContext null
            }
            
            // Get screen metrics
            val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
            val metrics = DisplayMetrics()
            @Suppress("DEPRECATION")
            windowManager.defaultDisplay.getRealMetrics(metrics)
            
            val width = metrics.widthPixels
            val height = metrics.heightPixels
            val density = metrics.densityDpi
            
            android.util.Log.d("ScreenshotHelper", "Screen: ${width}x${height} @ $density dpi")
            
            // Create ImageReader
            imageReader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 2)
            val reader = imageReader!!
            
            // Create VirtualDisplay
            virtualDisplay = projection.createVirtualDisplay(
                "AutoGLM_ScreenCapture_${System.currentTimeMillis()}",
                width, height, density,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                reader.surface, 
                null, 
                handler
            )
            
            if (virtualDisplay == null) {
                android.util.Log.e("ScreenshotHelper", "Failed to create VirtualDisplay")
                return@withContext null
            }
            
            // Wait for image to be available
            delay(300)
            
            // Get image
            val image = reader.acquireLatestImage()
            if (image == null) {
                android.util.Log.e("ScreenshotHelper", "Failed to acquire image, trying again...")
                delay(200)
                val retryImage = reader.acquireLatestImage()
                if (retryImage == null) {
                    android.util.Log.e("ScreenshotHelper", "Second attempt also failed")
                    cleanupResources()
                    return@withContext null
                }
                return@withContext processImage(retryImage, width, height)
            }
            
            val result = processImage(image, width, height)
            
            // Cleanup after successful capture
            cleanupResources()
            
            result
            
        } catch (e: Exception) {
            android.util.Log.e("ScreenshotHelper", "Screenshot failed: ${e.message}", e)
            cleanupResources()
            null
        }
    }
    
    private fun processImage(image: android.media.Image, width: Int, height: Int): String? {
        return try {
            val planes = image.planes
            val buffer = planes[0].buffer
            val pixelStride = planes[0].pixelStride
            val rowStride = planes[0].rowStride
            val rowPadding = rowStride - pixelStride * width
            
            val bitmap = Bitmap.createBitmap(
                width + rowPadding / pixelStride, 
                height, 
                Bitmap.Config.ARGB_8888
            )
            bitmap.copyPixelsFromBuffer(buffer)
            image.close()
            
            // Crop to actual screen size if needed
            val croppedBitmap = if (rowPadding > 0) {
                Bitmap.createBitmap(bitmap, 0, 0, width, height).also {
                    bitmap.recycle()
                }
            } else {
                bitmap
            }
            
            // Convert to Base64
            val outputStream = ByteArrayOutputStream()
            croppedBitmap.compress(Bitmap.CompressFormat.JPEG, 80, outputStream)
            val base64 = Base64.encodeToString(outputStream.toByteArray(), Base64.NO_WRAP)
            
            croppedBitmap.recycle()
            
            android.util.Log.d("ScreenshotHelper", "Screenshot successful, size: ${base64.length}")
            base64
            
        } catch (e: Exception) {
            android.util.Log.e("ScreenshotHelper", "processImage failed: ${e.message}")
            image.close()
            null
        }
    }
    
    private fun cleanupResources() {
        try {
            virtualDisplay?.release()
            virtualDisplay = null
        } catch (e: Exception) {
            android.util.Log.w("ScreenshotHelper", "Error releasing VirtualDisplay: ${e.message}")
        }
        
        try {
            imageReader?.close()
            imageReader = null
        } catch (e: Exception) {
            android.util.Log.w("ScreenshotHelper", "Error closing ImageReader: ${e.message}")
        }
    }
    
    fun release() {
        cleanupResources()
    }
}
