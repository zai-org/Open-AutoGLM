package com.autoglm.phone.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.autoglm.phone.AutoGLMApplication
import com.autoglm.phone.agent.PhoneAgent
import com.autoglm.phone.api.ModelConfig
import com.autoglm.phone.data.SettingsRepository
import com.autoglm.phone.service.AutoGLMAccessibilityService
import com.autoglm.phone.service.ScreenshotHelper
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

data class UiState(
    val taskInput: String = "",
    val isRunning: Boolean = false,
    val currentStep: Int = 0,
    val statusMessage: String = "等待任务"
)

data class SettingsState(
    val baseUrl: String = SettingsRepository.DEFAULT_BASE_URL,
    val apiKey: String = SettingsRepository.DEFAULT_API_KEY,
    val modelName: String = SettingsRepository.DEFAULT_MODEL_NAME
)

class MainViewModel(application: Application) : AndroidViewModel(application) {
    
    private val settingsRepository = (application as AutoGLMApplication).settingsRepository
    
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    private val _logs = MutableStateFlow<List<String>>(emptyList())
    val logs: StateFlow<List<String>> = _logs.asStateFlow()
    
    private val _settings = MutableStateFlow(SettingsState())
    val settings: StateFlow<SettingsState> = _settings.asStateFlow()
    
    private var currentAgent: PhoneAgent? = null
    
    init {
        loadSettings()
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
    
    fun updateTaskInput(text: String) {
        _uiState.update { it.copy(taskInput = text) }
    }
    
    fun startTask() {
        val service = AutoGLMAccessibilityService.getInstance() ?: run {
            addLog("❌ 无障碍服务未启用")
            return
        }
        
        val currentSettings = _settings.value
        if (currentSettings.apiKey.isBlank()) {
            addLog("❌ 请先配置 API Key")
            return
        }
        
        val task = _uiState.value.taskInput
        if (task.isBlank()) {
            addLog("❌ 请输入任务描述")
            return
        }
        
        _uiState.update { it.copy(isRunning = true) }
        _logs.value = emptyList()
        
        val config = ModelConfig(
            baseUrl = currentSettings.baseUrl,
            apiKey = currentSettings.apiKey,
            modelName = currentSettings.modelName
        )
        
        val screenshotHelper = ScreenshotHelper(getApplication())
        
        val agent = PhoneAgent(
            config = config,
            accessibilityService = service,
            screenshotHelper = screenshotHelper,
            onLog = { log -> addLog(log) },
            onStep = { step, status -> 
                _uiState.update { it.copy(currentStep = step, statusMessage = status) }
            }
        )
        currentAgent = agent
        
        viewModelScope.launch(Dispatchers.Default) {
            try {
                val result = agent.run(task)
                addLog("📋 最终结果: $result")
            } catch (e: Exception) {
                addLog("❌ 执行错误: ${e.message}")
            } finally {
                _uiState.update { it.copy(isRunning = false) }
                currentAgent = null
            }
        }
    }
    
    fun stopTask() {
        currentAgent?.stop()
        _uiState.update { it.copy(isRunning = false) }
    }
    
    fun saveSettings(baseUrl: String, apiKey: String, modelName: String) {
        viewModelScope.launch {
            settingsRepository.saveSettings(baseUrl, apiKey, modelName)
            addLog("✅ 设置已保存")
        }
    }
    
    private fun addLog(message: String) {
        val timestamp = java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
            .format(java.util.Date())
        _logs.update { it + "[$timestamp] $message" }
    }
}
