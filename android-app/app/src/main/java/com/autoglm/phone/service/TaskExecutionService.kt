package com.autoglm.phone.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Binder
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.autoglm.phone.MainActivity
import com.autoglm.phone.R
import com.autoglm.phone.agent.PhoneAgent
import com.autoglm.phone.api.ModelConfig
import com.autoglm.phone.data.SettingsRepository
import com.autoglm.phone.data.TaskHistoryRepository
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first

/**
 * Foreground Service for running AutoGLM tasks in background.
 * Shows notification with progress and allows stopping from notification.
 */
class TaskExecutionService : Service() {
    
    companion object {
        const val CHANNEL_ID = "autoglm_task_channel"
        const val NOTIFICATION_ID = 1001
        
        const val ACTION_START_TASK = "com.autoglm.phone.START_TASK"
        const val ACTION_STOP_TASK = "com.autoglm.phone.STOP_TASK"
        const val EXTRA_TASK = "task"
        
        private var instance: TaskExecutionService? = null
        fun getInstance(): TaskExecutionService? = instance
    }
    
    private val binder = LocalBinder()
    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    
    private var currentAgent: PhoneAgent? = null
    private var currentJob: Job? = null
    
    // State exposed to UI
    private val _executionState = MutableStateFlow(ExecutionState())
    val executionState: StateFlow<ExecutionState> = _executionState.asStateFlow()
    
    private val _logs = MutableStateFlow<List<LogEntry>>(emptyList())
    val logs: StateFlow<List<LogEntry>> = _logs.asStateFlow()
    
    private lateinit var settingsRepository: SettingsRepository
    private lateinit var historyRepository: TaskHistoryRepository
    
    inner class LocalBinder : Binder() {
        fun getService(): TaskExecutionService = this@TaskExecutionService
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        settingsRepository = SettingsRepository(this)
        historyRepository = TaskHistoryRepository(this)
        createNotificationChannel()
    }
    
    override fun onBind(intent: Intent?): IBinder = binder
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_TASK -> {
                val task = intent.getStringExtra(EXTRA_TASK) ?: return START_NOT_STICKY
                startTask(task)
            }
            ACTION_STOP_TASK -> {
                stopTask()
            }
        }
        return START_NOT_STICKY
    }
    
    override fun onDestroy() {
        super.onDestroy()
        instance = null
        serviceScope.cancel()
    }
    
    /**
     * Start executing a task.
     */
    fun startTask(task: String) {
        if (_executionState.value.isRunning) {
            addLog("⚠️ 已有任务正在执行", LogLevel.WARNING)
            return
        }
        
        // Start foreground
        startForeground(NOTIFICATION_ID, createNotification("准备中...", 0))
        
        // Reset state
        _executionState.value = ExecutionState(
            isRunning = true,
            taskDescription = task,
            currentStep = 0,
            totalSteps = 0,
            currentAction = "初始化..."
        )
        _logs.value = emptyList()
        
        val startTime = System.currentTimeMillis()
        addLog("📝 开始任务: $task", LogLevel.INFO)
        
        currentJob = serviceScope.launch {
            try {
                val service = AutoGLMAccessibilityService.getInstance()
                if (service == null) {
                    addLog("❌ 无障碍服务未启用", LogLevel.ERROR)
                    _executionState.value = _executionState.value.copy(
                        isRunning = false,
                        currentAction = "无障碍服务未启用"
                    )
                    stopForeground(STOP_FOREGROUND_REMOVE)
                    return@launch
                }
                
                // Get settings using first() (non-blocking)
                val baseUrl = settingsRepository.apiBaseUrl.first()
                val apiKey = settingsRepository.apiKey.first()
                val modelName = settingsRepository.modelName.first()
                
                val config = ModelConfig(
                    baseUrl = baseUrl,
                    apiKey = apiKey,
                    modelName = modelName
                )
                
                val screenshotHelper = ScreenshotHelper(this@TaskExecutionService)
                
                val agent = PhoneAgent(
                    config = config,
                    accessibilityService = service,
                    screenshotHelper = screenshotHelper,
                    onLog = { log -> addLog(log, LogLevel.INFO) },
                    onStep = { step, status -> 
                        _executionState.value = _executionState.value.copy(
                            currentStep = step,
                            currentAction = status
                        )
                        updateNotification("步骤 $step: $status", step)
                        // Show floating status at bottom of screen
                        FloatingStatusService.updateStatus(this@TaskExecutionService, "步骤$step: $status")
                    },
                    onHideOverlay = { hide ->
                        if (hide) {
                            FloatingStatusService.hide(this@TaskExecutionService)
                        }
                        // If not hiding, onStep will show it with updated status
                    }
                )
                currentAgent = agent
                
                val result = agent.run(task)
                
                addLog("✅ 任务完成: $result", LogLevel.SUCCESS)
                
                // Hide floating status
                FloatingStatusService.hide(this@TaskExecutionService)
                
                // Save to history
                val duration = System.currentTimeMillis() - startTime
                historyRepository.saveTask(task, result, duration, true)
                
                _executionState.value = _executionState.value.copy(
                    isRunning = false,
                    currentAction = "已完成: $result"
                )
                
            } catch (e: Exception) {
                addLog("❌ 执行错误: ${e.message}", LogLevel.ERROR)
                
                // Hide floating status
                FloatingStatusService.hide(this@TaskExecutionService)
                
                // Save failed task to history
                val duration = System.currentTimeMillis() - startTime
                historyRepository.saveTask(task, e.message ?: "Unknown error", duration, false)
                
                _executionState.value = _executionState.value.copy(
                    isRunning = false,
                    currentAction = "错误: ${e.message}"
                )
            } finally {
                currentAgent = null
                stopForeground(STOP_FOREGROUND_REMOVE)
            }
        }
    }
    
    /**
     * Stop the current task.
     */
    fun stopTask() {
        currentAgent?.stop()
        currentJob?.cancel()
        addLog("🛑 任务已停止", LogLevel.WARNING)
        FloatingStatusService.hide(this)
        _executionState.value = _executionState.value.copy(
            isRunning = false,
            currentAction = "已停止"
        )
        stopForeground(STOP_FOREGROUND_REMOVE)
    }
    
    private fun addLog(message: String, level: LogLevel) {
        val timestamp = java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
            .format(java.util.Date())
        val entry = LogEntry(timestamp, message, level)
        _logs.value = _logs.value + entry
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "AutoGLM 任务执行",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "显示任务执行进度"
                setShowBadge(false)
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(text: String, step: Int): Notification {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
        }
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val stopIntent = Intent(this, TaskExecutionService::class.java).apply {
            action = ACTION_STOP_TASK
        }
        val stopPendingIntent = PendingIntent.getService(
            this, 0, stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("AutoGLM 执行中")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_manage)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "停止", stopPendingIntent)
            .build()
    }
    
    private fun updateNotification(text: String, step: Int) {
        val notification = createNotification(text, step)
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(NOTIFICATION_ID, notification)
    }
}

/**
 * Current execution state.
 */
data class ExecutionState(
    val isRunning: Boolean = false,
    val taskDescription: String = "",
    val currentStep: Int = 0,
    val totalSteps: Int = 0,
    val currentAction: String = "等待任务",
    val currentScreenshot: String? = null
)

/**
 * Log entry with level.
 */
data class LogEntry(
    val timestamp: String,
    val message: String,
    val level: LogLevel
)

enum class LogLevel {
    INFO, SUCCESS, WARNING, ERROR
}
