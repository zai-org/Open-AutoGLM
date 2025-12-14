package com.autoglm.phone.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.historyDataStore: DataStore<Preferences> by preferencesDataStore(name = "task_history")

/**
 * Repository for task execution history.
 * Uses DataStore + JSON for simplicity (no Room dependency needed).
 */
class TaskHistoryRepository(private val context: Context) {
    
    companion object {
        private val HISTORY_KEY = stringPreferencesKey("history")
        private const val MAX_HISTORY_SIZE = 50
    }
    
    private val gson = Gson()
    
    val history: Flow<List<TaskHistoryEntry>> = context.historyDataStore.data.map { preferences ->
        val json = preferences[HISTORY_KEY] ?: "[]"
        try {
            val type = object : TypeToken<List<TaskHistoryEntry>>() {}.type
            gson.fromJson<List<TaskHistoryEntry>>(json, type) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }
    
    suspend fun saveTask(
        task: String,
        result: String,
        durationMs: Long,
        success: Boolean
    ) {
        context.historyDataStore.edit { preferences ->
            val json = preferences[HISTORY_KEY] ?: "[]"
            val currentList = try {
                val type = object : TypeToken<MutableList<TaskHistoryEntry>>() {}.type
                gson.fromJson<MutableList<TaskHistoryEntry>>(json, type) ?: mutableListOf()
            } catch (e: Exception) {
                mutableListOf()
            }
            
            val entry = TaskHistoryEntry(
                id = System.currentTimeMillis(),
                task = task,
                result = result,
                timestamp = System.currentTimeMillis(),
                durationMs = durationMs,
                success = success
            )
            
            // Add to front, limit size
            currentList.add(0, entry)
            while (currentList.size > MAX_HISTORY_SIZE) {
                currentList.removeAt(currentList.size - 1)
            }
            
            preferences[HISTORY_KEY] = gson.toJson(currentList)
        }
    }
    
    suspend fun clearHistory() {
        context.historyDataStore.edit { preferences ->
            preferences[HISTORY_KEY] = "[]"
        }
    }
}

/**
 * A task execution history entry.
 */
data class TaskHistoryEntry(
    val id: Long,
    val task: String,
    val result: String,
    val timestamp: Long,
    val durationMs: Long,
    val success: Boolean
)
