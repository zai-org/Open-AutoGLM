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
import java.util.UUID

private val Context.scheduledTasksDataStore: DataStore<Preferences> by preferencesDataStore(name = "scheduled_tasks")

/**
 * Scheduled task data model.
 */
data class ScheduledTask(
    val id: String = UUID.randomUUID().toString(),
    val name: String,           // Task display name
    val prompt: String,         // Task prompt to execute
    val hour: Int,              // Execution hour (0-23)
    val minute: Int,            // Execution minute (0-59)
    val repeatDays: List<Int>,  // Days to repeat (1=Monday, 7=Sunday), empty = daily
    val isEnabled: Boolean = true,
    val lastRunTime: Long? = null,
    val lastResult: String? = null
)

/**
 * Repository for scheduled tasks.
 */
class ScheduledTaskRepository(private val context: Context) {
    
    companion object {
        private val SCHEDULED_TASKS_KEY = stringPreferencesKey("scheduled_tasks")
    }
    
    private val gson = Gson()
    
    val scheduledTasks: Flow<List<ScheduledTask>> = context.scheduledTasksDataStore.data.map { preferences ->
        val json = preferences[SCHEDULED_TASKS_KEY] ?: "[]"
        val type = object : TypeToken<List<ScheduledTask>>() {}.type
        gson.fromJson(json, type) ?: emptyList()
    }
    
    suspend fun addTask(task: ScheduledTask) {
        context.scheduledTasksDataStore.edit { preferences ->
            val currentJson = preferences[SCHEDULED_TASKS_KEY] ?: "[]"
            val type = object : TypeToken<List<ScheduledTask>>() {}.type
            val currentTasks: MutableList<ScheduledTask> = gson.fromJson(currentJson, type) ?: mutableListOf()
            currentTasks.add(task)
            preferences[SCHEDULED_TASKS_KEY] = gson.toJson(currentTasks)
        }
    }
    
    suspend fun updateTask(task: ScheduledTask) {
        context.scheduledTasksDataStore.edit { preferences ->
            val currentJson = preferences[SCHEDULED_TASKS_KEY] ?: "[]"
            val type = object : TypeToken<List<ScheduledTask>>() {}.type
            val currentTasks: MutableList<ScheduledTask> = gson.fromJson(currentJson, type) ?: mutableListOf()
            val index = currentTasks.indexOfFirst { it.id == task.id }
            if (index >= 0) {
                currentTasks[index] = task
            }
            preferences[SCHEDULED_TASKS_KEY] = gson.toJson(currentTasks)
        }
    }
    
    suspend fun deleteTask(taskId: String) {
        context.scheduledTasksDataStore.edit { preferences ->
            val currentJson = preferences[SCHEDULED_TASKS_KEY] ?: "[]"
            val type = object : TypeToken<List<ScheduledTask>>() {}.type
            val currentTasks: MutableList<ScheduledTask> = gson.fromJson(currentJson, type) ?: mutableListOf()
            currentTasks.removeAll { it.id == taskId }
            preferences[SCHEDULED_TASKS_KEY] = gson.toJson(currentTasks)
        }
    }
    
    suspend fun toggleTask(taskId: String, enabled: Boolean) {
        context.scheduledTasksDataStore.edit { preferences ->
            val currentJson = preferences[SCHEDULED_TASKS_KEY] ?: "[]"
            val type = object : TypeToken<List<ScheduledTask>>() {}.type
            val currentTasks: MutableList<ScheduledTask> = gson.fromJson(currentJson, type) ?: mutableListOf()
            val index = currentTasks.indexOfFirst { it.id == taskId }
            if (index >= 0) {
                currentTasks[index] = currentTasks[index].copy(isEnabled = enabled)
            }
            preferences[SCHEDULED_TASKS_KEY] = gson.toJson(currentTasks)
        }
    }
}
