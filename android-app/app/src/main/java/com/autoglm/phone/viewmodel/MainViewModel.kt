package com.autoglm.phone.viewmodel

import android.app.Application
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.IBinder
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.autoglm.phone.AutoGLMApplication
import com.autoglm.phone.data.SettingsRepository
import com.autoglm.phone.data.TaskHistoryEntry
import com.autoglm.phone.data.TaskHistoryRepository
import com.autoglm.phone.service.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class UiState(
    val taskInput: String = "",
    val isRunning: Boolean = false,
    val currentStep: Int = 0,
    val currentAction: String = "等待任务",
    val showHistory: Boolean = false
)

data class SettingsState(
    val baseUrl: String = SettingsRepository.DEFAULT_BASE_URL,
    val apiKey: String = SettingsRepository.DEFAULT_API_KEY,
    val modelName: String = SettingsRepository.DEFAULT_MODEL_NAME
)

class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val settingsRepository = (application as AutoGLMApplication).settingsRepository
    private val historyRepository = TaskHistoryRepository(application)
    
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    private val _logs = MutableStateFlow<List<LogEntry>>(emptyList())
    val logs: StateFlow<List<LogEntry>> = _logs.asStateFlow()
    
    private val _settings = MutableStateFlow(SettingsState())
    val settings: StateFlow<SettingsState> = _settings.asStateFlow()
    
    private val _history = MutableStateFlow<List<TaskHistoryEntry>>(emptyList())
    val history: StateFlow<List<TaskHistoryEntry>> = _history.asStateFlow()
    
    // Service binding
    private var taskService: TaskExecutionService? = null
    private var isBound = false
    
    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            val binder = service as TaskExecutionService.LocalBinder
            taskService = binder.getService()
            isBound = true
            
            // Observe service state
            observeServiceState()
        }
        
        override fun onServiceDisconnected(name: ComponentName?) {
            taskService = null
            isBound = false
        }
    }
    
    init {
        loadSettings()
        loadHistory()
        bindService()
    }
    
    private fun bindService() {
        val context = getApplication<Application>()
        val intent = Intent(context, TaskExecutionService::class.java)
        context.bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE)
    }
    
    private fun observeServiceState() {
        val service = taskService ?: return
        
        viewModelScope.launch {
            service.executionState.collect { state ->
                _uiState.update { 
                    it.copy(
                        isRunning = state.isRunning,
                        currentStep = state.currentStep,
                        currentAction = state.currentAction
                    )
                }
            }
        }
        
        viewModelScope.launch {
            service.logs.collect { logs ->
                _logs.value = logs
            }
        }
    }
    
    private fun loadSettings() {
        viewModelScope.launch {
            combine(
                settingsRepository.apiBaseUrl,
                settingsRepository.apiKey,
                settingsRepository.modelName
            ) { baseUrl, apiKey, modelName ->
                SettingsState(baseUrl, apiKey, modelName)
            }.collect { settings ->
                _settings.value = settings
            }
        }
    }
    
    private fun loadHistory() {
        viewModelScope.launch {
            historyRepository.history.collect { entries ->
                _history.value = entries
            }
        }
    }
    
    fun updateTaskInput(text: String) {
        _uiState.update { it.copy(taskInput = text) }
    }
    
    fun toggleHistory() {
        _uiState.update { it.copy(showHistory = !it.showHistory) }
    }
    
    fun startTask() {
        val task = _uiState.value.taskInput
        if (task.isBlank()) return
        
        val context = getApplication<Application>()
        val intent = Intent(context, TaskExecutionService::class.java).apply {
            action = TaskExecutionService.ACTION_START_TASK
            putExtra(TaskExecutionService.EXTRA_TASK, task)
        }
        context.startService(intent)
    }
    
    fun startTaskFromHistory(task: String) {
        _uiState.update { it.copy(taskInput = task, showHistory = false) }
        startTask()
    }
    
    fun stopTask() {
        val context = getApplication<Application>()
        val intent = Intent(context, TaskExecutionService::class.java).apply {
            action = TaskExecutionService.ACTION_STOP_TASK
        }
        context.startService(intent)
    }
    
    fun saveSettings(baseUrl: String, apiKey: String, modelName: String) {
        viewModelScope.launch {
            settingsRepository.saveSettings(baseUrl, apiKey, modelName)
        }
    }
    
    fun setReturnToApp(enabled: Boolean) {
        viewModelScope.launch {
            settingsRepository.setReturnToApp(enabled)
        }
    }
    
    fun clearHistory() {
        viewModelScope.launch {
            historyRepository.clearHistory()
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        if (isBound) {
            getApplication<Application>().unbindService(serviceConnection)
            isBound = false
        }
    }
}
