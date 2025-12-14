package com.autoglm.phone

import android.app.Application
import com.autoglm.phone.data.SettingsRepository

/**
 * Application class for AutoGLM.
 * Provides app-wide singletons.
 */
class AutoGLMApplication : Application() {
    
    lateinit var settingsRepository: SettingsRepository
        private set
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        settingsRepository = SettingsRepository(this)
    }
    
    companion object {
        lateinit var instance: AutoGLMApplication
            private set
    }
}
