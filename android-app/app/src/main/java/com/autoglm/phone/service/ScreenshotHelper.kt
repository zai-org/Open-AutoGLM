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
import android.util.Base64
import android.util.DisplayMetrics
import android.view.WindowManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import kotlin.coroutines.resume

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
         * Call this from Activity.onActivityResult()
         */
        fun setMediaProjectionResult(resultCode: Int, data: Intent?) {
            this.resultCode = resultCode
            this.resultData = data
        }
        
        fun hasMediaProjectionPermission(): Boolean {
            return resultCode == Activity.RESULT_OK && resultData != null
        }
        
        fun clearMediaProjection() {
            mediaProjection?.stop()
            mediaProjection = null
        }
    }
    
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null
    
    /**
     * Take screenshot using the best available method.
     * @return Base64 encoded PNG, or null if failed
     */
    suspend fun takeScreenshot(): String? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // Android 11+ - use Accessibility Service
            takeScreenshotViaAccessibility()
        } else {
            // Android 9-10 - use MediaProjection
            takeScreenshotViaMediaProjection()
        }
    }
    
    /**
     * Take screenshot via AccessibilityService (Android 11+)
     */
    private suspend fun takeScreenshotViaAccessibility(): String? {
        val service = AutoGLMAccessibilityService.getInstance()
        return service?.takeScreenshot()
    }
    
    /**
     * Take screenshot via MediaProjection (Android 9+)
     */
    private suspend fun takeScreenshotViaMediaProjection(): String? = withContext(Dispatchers.Main) {
        if (!hasMediaProjectionPermission()) {
            android.util.Log.e("ScreenshotHelper", "No MediaProjection permission")
            return@withContext null
        }
        
        try {
            val projectionManager = context.getSystemService(Context.MEDIA_PROJECTION_SERVICE) 
                as MediaProjectionManager
            
            // Create MediaProjection if not exists
            if (mediaProjection == null) {
                mediaProjection = projectionManager.getMediaProjection(resultCode, resultData!!)
            }
            
            val projection = mediaProjection ?: return@withContext null
            
            // Get screen metrics
            val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
            val metrics = DisplayMetrics()
            @Suppress("DEPRECATION")
            windowManager.defaultDisplay.getMetrics(metrics)
            
            val width = metrics.widthPixels
            val height = metrics.heightPixels
            val density = metrics.densityDpi
            
            // Create ImageReader
            imageReader?.close()
            imageReader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 2)
            val reader = imageReader!!
            
            // Create VirtualDisplay
            virtualDisplay?.release()
            virtualDisplay = projection.createVirtualDisplay(
                "ScreenCapture",
                width, height, density,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                reader.surface, null, null
            )
            
            // Wait for image to be available
            delay(200)
            
            // Get image
            val image = reader.acquireLatestImage()
            if (image == null) {
                android.util.Log.e("ScreenshotHelper", "Failed to acquire image")
                return@withContext null
            }
            
            // Convert to Bitmap
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
                Bitmap.createBitmap(bitmap, 0, 0, width, height)
            } else {
                bitmap
            }
            
            // Convert to Base64
            val outputStream = ByteArrayOutputStream()
            croppedBitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
            val base64 = Base64.encodeToString(outputStream.toByteArray(), Base64.NO_WRAP)
            
            // Cleanup
            if (croppedBitmap !== bitmap) {
                bitmap.recycle()
            }
            croppedBitmap.recycle()
            
            base64
            
        } catch (e: Exception) {
            android.util.Log.e("ScreenshotHelper", "Screenshot failed: ${e.message}")
            null
        }
    }
    
    /**
     * Release resources
     */
    fun release() {
        virtualDisplay?.release()
        virtualDisplay = null
        imageReader?.close()
        imageReader = null
    }
}
