package com.autoglm.phone.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

/**
 * Repository for app settings stored in DataStore.
 */
class SettingsRepository(private val context: Context) {
    
    companion object {
        private val API_BASE_URL = stringPreferencesKey("api_base_url")
        private val API_KEY = stringPreferencesKey("api_key")
        private val MODEL_NAME = stringPreferencesKey("model_name")
        private val RETURN_TO_APP = booleanPreferencesKey("return_to_app")
        private val SHOW_LOGS = booleanPreferencesKey("show_logs")
        
        const val DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
        const val DEFAULT_API_KEY = "7af8f9b40693467fb7b454ff79bfa428.4rq2cgqTk6CB95w8"
        const val DEFAULT_MODEL_NAME = "autoglm-phone"
        const val DEFAULT_RETURN_TO_APP = true
        const val DEFAULT_SHOW_LOGS = true
    }
    
    val apiBaseUrl: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[API_BASE_URL] ?: DEFAULT_BASE_URL
    }
    
    val apiKey: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[API_KEY] ?: DEFAULT_API_KEY
    }
    
    val modelName: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[MODEL_NAME] ?: DEFAULT_MODEL_NAME
    }
    
    val returnToApp: Flow<Boolean> = context.dataStore.data.map { preferences ->
        preferences[RETURN_TO_APP] ?: DEFAULT_RETURN_TO_APP
    }
    
    val showLogs: Flow<Boolean> = context.dataStore.data.map { preferences ->
        preferences[SHOW_LOGS] ?: DEFAULT_SHOW_LOGS
    }
    
    suspend fun saveSettings(baseUrl: String, apiKey: String, modelName: String) {
        context.dataStore.edit { preferences ->
            preferences[API_BASE_URL] = baseUrl
            preferences[API_KEY] = apiKey
            preferences[MODEL_NAME] = modelName
        }
    }
    
    suspend fun setReturnToApp(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[RETURN_TO_APP] = enabled
        }
    }
    
    suspend fun setShowLogs(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[SHOW_LOGS] = enabled
        }
    }
}
