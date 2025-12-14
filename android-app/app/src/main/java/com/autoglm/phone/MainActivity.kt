package com.autoglm.phone

import android.Manifest
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import com.autoglm.phone.data.TaskHistoryEntry
import com.autoglm.phone.service.AutoGLMAccessibilityService
import com.autoglm.phone.service.LogEntry
import com.autoglm.phone.service.LogLevel
import com.autoglm.phone.service.ScreenshotHelper
import com.autoglm.phone.ui.theme.AutoGLMTheme
import com.autoglm.phone.viewmodel.MainViewModel
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : ComponentActivity() {
    
    private val mediaProjectionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            ScreenshotHelper.setMediaProjectionResult(result.resultCode, result.data)
            android.util.Log.d("MainActivity", "MediaProjection permission granted")
        } else {
            android.util.Log.e("MainActivity", "MediaProjection permission denied")
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Request overlay permission for floating status
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
            startActivity(intent)
        }
        
        // Request MediaProjection on Android 9-10 (required for screenshot)
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) {
            if (!ScreenshotHelper.hasMediaProjectionPermission()) {
                requestMediaProjectionPermission()
            }
        }
        
        setContent {
            AutoGLMTheme(darkTheme = true) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen(
                        onRequestMediaProjection = { requestMediaProjectionPermission() }
                    )
                }
            }
        }
    }
    
    private fun requestMediaProjectionPermission() {
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        val intent = projectionManager.createScreenCaptureIntent()
        mediaProjectionLauncher.launch(intent)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    viewModel: MainViewModel = viewModel(),
    onRequestMediaProjection: () -> Unit = {}
) {
    val context = LocalContext.current
    var showSettings by remember { mutableStateOf(false) }
    
    val uiState by viewModel.uiState.collectAsState()
    val logs by viewModel.logs.collectAsState()
    val history by viewModel.history.collectAsState()
    val isServiceEnabled = AutoGLMAccessibilityService.isServiceEnabled()
    
    // Request notification permission on Android 13+
    val notificationPermissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { /* result */ }
    
    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) 
                != PackageManager.PERMISSION_GRANTED) {
                notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(CircleShape)
                                .background(
                                    Brush.linearGradient(
                                        listOf(Color(0xFF2196F3), Color(0xFF00BCD4))
                                    )
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.SmartToy,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("AutoPhone", fontWeight = FontWeight.Bold)
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.toggleTemplates() }) {
                        Icon(
                            Icons.Default.Lightbulb, 
                            contentDescription = "模板",
                            tint = if (uiState.showTemplates) MaterialTheme.colorScheme.primary else LocalContentColor.current
                        )
                    }
                    IconButton(onClick = { viewModel.toggleHistory() }) {
                        Icon(
                            Icons.Default.History, 
                            contentDescription = "历史",
                            tint = if (uiState.showHistory) MaterialTheme.colorScheme.primary else LocalContentColor.current
                        )
                    }
                    IconButton(onClick = { viewModel.toggleScheduled() }) {
                        Icon(
                            Icons.Default.Alarm, 
                            contentDescription = "定时任务",
                            tint = if (uiState.showScheduled) MaterialTheme.colorScheme.primary else LocalContentColor.current
                        )
                    }
                    IconButton(onClick = { showSettings = true }) {
                        Icon(Icons.Default.Settings, contentDescription = "设置")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            // Service Status Card
            ServiceStatusCard(
                isEnabled = isServiceEnabled,
                onEnableClick = {
                    context.startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
                }
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Progress Card (visible when running)
            AnimatedVisibility(
                visible = uiState.isRunning,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                ProgressCard(
                    step = uiState.currentStep,
                    action = uiState.currentAction,
                    onStop = { viewModel.stopTask() }
                )
            }
            
            // History Panel
            AnimatedVisibility(
                visible = uiState.showHistory && !uiState.isRunning,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                HistoryPanel(
                    history = history,
                    onRunTask = { 
                        // Check MediaProjection permission on Android 9-10
                        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R && 
                            !ScreenshotHelper.hasMediaProjectionPermission()) {
                            onRequestMediaProjection()
                        }
                        viewModel.startTaskFromHistory(it) 
                    },
                    onClear = { viewModel.clearHistory() },
                    modifier = Modifier.weight(1f)
                )
            }
            
            // Templates Panel
            AnimatedVisibility(
                visible = uiState.showTemplates && !uiState.isRunning,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                TemplatesPanel(
                    onSelectTemplate = { viewModel.selectTemplate(it) },
                    modifier = Modifier.weight(1f)
                )
            }
            
            // Scheduled Tasks Panel
            AnimatedVisibility(
                visible = uiState.showScheduled && !uiState.isRunning,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                ScheduledTasksPanel(
                    onAddTask = { name, prompt, hour, minute -> },
                    modifier = Modifier.weight(1f)
                )
            }
            
            // Main content (task input + logs)
            AnimatedVisibility(
                visible = !uiState.showHistory && !uiState.showTemplates && !uiState.showScheduled || uiState.isRunning,
                enter = fadeIn(),
                exit = fadeOut()
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    // Task Input
                    TaskInputCard(
                        taskText = uiState.taskInput,
                        onTaskChange = { viewModel.updateTaskInput(it) },
                        isRunning = uiState.isRunning,
                        isServiceEnabled = isServiceEnabled,
                        onStartClick = { 
                            // Check MediaProjection permission on Android 9-10
                            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R && 
                                !ScreenshotHelper.hasMediaProjectionPermission()) {
                                onRequestMediaProjection()
                            }
                            viewModel.startTask() 
                        },
                        onStopClick = { viewModel.stopTask() }
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Logs
                    LogsCard(
                        logs = logs,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
    
    if (showSettings) {
        SettingsDialog(
            viewModel = viewModel,
            onDismiss = { showSettings = false }
        )
    }
}

@Composable
fun ProgressCard(
    step: Int,
    action: String,
    onStop: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF1A237E).copy(alpha = 0.4f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Animated indicator
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(Color(0xFF3F51B5)),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(40.dp),
                    color = Color.White,
                    strokeWidth = 3.dp
                )
                Text(
                    text = "$step",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "步骤 $step",
                    fontWeight = FontWeight.Medium,
                    color = Color.White
                )
                Text(
                    text = action,
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.White.copy(alpha = 0.8f),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
            }
            
            IconButton(
                onClick = onStop,
                colors = IconButtonDefaults.iconButtonColors(
                    containerColor = Color(0xFFE53935).copy(alpha = 0.8f)
                )
            ) {
                Icon(Icons.Default.Stop, contentDescription = "停止", tint = Color.White)
            }
        }
    }
}

@Composable
fun HistoryPanel(
    history: List<TaskHistoryEntry>,
    onRunTask: (String) -> Unit,
    onClear: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "任务历史",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
                if (history.isNotEmpty()) {
                    TextButton(onClick = onClear) {
                        Text("清除", color = Color(0xFFE53935))
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            if (history.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        "暂无历史记录",
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            } else {
                LazyColumn {
                    items(history) { entry ->
                        HistoryItem(
                            entry = entry,
                            onClick = { onRunTask(entry.task) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun HistoryItem(
    entry: TaskHistoryEntry,
    onClick: () -> Unit
) {
    val dateFormat = remember { SimpleDateFormat("MM/dd HH:mm", Locale.getDefault()) }
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (entry.success) Icons.Default.CheckCircle else Icons.Default.Error,
                contentDescription = null,
                tint = if (entry.success) Color(0xFF40C057) else Color(0xFFE53935),
                modifier = Modifier.size(20.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = entry.task,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = dateFormat.format(Date(entry.timestamp)),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Icon(
                Icons.Default.PlayArrow,
                contentDescription = "重新执行",
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
fun ServiceStatusCard(isEnabled: Boolean, onEnableClick: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isEnabled) Color(0xFF1B4332).copy(alpha = 0.5f) 
                           else Color(0xFF5C2323).copy(alpha = 0.5f)
        )
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isEnabled) Icons.Default.CheckCircle else Icons.Default.Warning,
                contentDescription = null,
                tint = if (isEnabled) Color(0xFF40C057) else Color(0xFFFA5252)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = if (isEnabled) "无障碍服务已启用" else "无障碍服务未启用",
                    fontWeight = FontWeight.Medium
                )
            }
            if (!isEnabled) {
                TextButton(onClick = onEnableClick) { Text("启用") }
            }
        }
    }
}

@Composable
fun TaskInputCard(
    taskText: String,
    onTaskChange: (String) -> Unit,
    isRunning: Boolean,
    isServiceEnabled: Boolean,
    onStartClick: () -> Unit,
    onStopClick: () -> Unit
) {
    val context = LocalContext.current
    var isListening by remember { mutableStateOf(false) }
    
    // Speech recognizer launcher
    val speechLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        isListening = false
        if (result.resultCode == Activity.RESULT_OK) {
            val spokenText = result.data
                ?.getStringArrayListExtra(android.speech.RecognizerIntent.EXTRA_RESULTS)
                ?.firstOrNull() ?: ""
            if (spokenText.isNotBlank()) {
                onTaskChange(spokenText)
            }
        }
    }
    
    fun startVoiceInput() {
        val intent = android.content.Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, 
                android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE, "zh-CN")
            putExtra(android.speech.RecognizerIntent.EXTRA_PROMPT, "请说出您的任务...")
        }
        try {
            isListening = true
            speechLauncher.launch(intent)
        } catch (e: Exception) {
            isListening = false
            android.widget.Toast.makeText(context, "语音输入不可用", android.widget.Toast.LENGTH_SHORT).show()
        }
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            // Text input with microphone button
            OutlinedTextField(
                value = taskText,
                onValueChange = onTaskChange,
                modifier = Modifier.fillMaxWidth(),
                label = { Text("任务描述") },
                placeholder = { Text("例如：打开微信发消息给文件传输助手") },
                enabled = !isRunning,
                minLines = 2,
                maxLines = 4,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                keyboardActions = KeyboardActions(
                    onDone = { if (isServiceEnabled && !isRunning) onStartClick() }
                ),
                trailingIcon = {
                    IconButton(
                        onClick = { startVoiceInput() },
                        enabled = !isRunning && !isListening
                    ) {
                        Icon(
                            if (isListening) Icons.Default.Mic else Icons.Default.MicNone,
                            contentDescription = "语音输入",
                            tint = if (isListening) 
                                MaterialTheme.colorScheme.primary 
                            else 
                                MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Button(
                onClick = onStartClick,
                modifier = Modifier.fillMaxWidth(),
                enabled = isServiceEnabled && !isRunning && taskText.isNotBlank()
            ) {
                Icon(Icons.Default.PlayArrow, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("开始任务")
            }
        }
    }
}

@Composable
fun LogsCard(logs: List<LogEntry>, modifier: Modifier = Modifier) {
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()
    
    LaunchedEffect(logs.size) {
        if (logs.isNotEmpty()) {
            coroutineScope.launch {
                listState.animateScrollToItem(logs.size - 1)
            }
        }
    }
    
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0D1117))
    ) {
        Column(modifier = Modifier.fillMaxSize().padding(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.Terminal,
                    contentDescription = null,
                    tint = Color(0xFF58A6FF),
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("执行日志", style = MaterialTheme.typography.labelLarge, color = Color(0xFF58A6FF))
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .clip(RoundedCornerShape(8.dp))
                    .background(Color(0xFF161B22))
                    .padding(8.dp)
            ) {
                if (logs.isEmpty()) {
                    Text("等待任务开始...", style = MaterialTheme.typography.bodySmall, color = Color(0xFF6E7681))
                } else {
                    LazyColumn(state = listState, modifier = Modifier.fillMaxSize()) {
                        items(logs) { log ->
                            Text(
                                text = "[${log.timestamp}] ${log.message}",
                                style = MaterialTheme.typography.bodySmall.copy(
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 11.sp
                                ),
                                color = when (log.level) {
                                    LogLevel.SUCCESS -> Color(0xFF40C057)
                                    LogLevel.ERROR -> Color(0xFFFA5252)
                                    LogLevel.WARNING -> Color(0xFFFCC419)
                                    LogLevel.INFO -> Color(0xFFC9D1D9)
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsDialog(viewModel: MainViewModel, onDismiss: () -> Unit) {
    val settings by viewModel.settings.collectAsState()
    var baseUrl by remember { mutableStateOf(settings.baseUrl) }
    var apiKey by remember { mutableStateOf(settings.apiKey) }
    var modelName by remember { mutableStateOf(settings.modelName) }
    var showApiKey by remember { mutableStateOf(false) }
    val context = LocalContext.current
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Settings, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("API 设置")
            }
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = baseUrl,
                    onValueChange = { baseUrl = it },
                    label = { Text("API Base URL") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                
                OutlinedTextField(
                    value = apiKey,
                    onValueChange = { apiKey = it },
                    label = { Text("API Key") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    visualTransformation = if (showApiKey) VisualTransformation.None else PasswordVisualTransformation(),
                    trailingIcon = {
                        IconButton(onClick = { showApiKey = !showApiKey }) {
                            Icon(
                                if (showApiKey) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                                contentDescription = null
                            )
                        }
                    }
                )
                
                // Link to get API key
                TextButton(
                    onClick = {
                        val intent = Intent(Intent.ACTION_VIEW, 
                            android.net.Uri.parse("https://bigmodel.cn/usercenter/proj-mgmt/apikeys"))
                        context.startActivity(intent)
                    },
                    modifier = Modifier.align(Alignment.End)
                ) {
                    Icon(Icons.Default.OpenInNew, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("获取 API Key", style = MaterialTheme.typography.bodySmall)
                }
                
                OutlinedTextField(
                    value = modelName,
                    onValueChange = { modelName = it },
                    label = { Text("模型名称") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                
                Divider(modifier = Modifier.padding(vertical = 8.dp))
                
                // Return to app setting
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("任务完成后返回应用", style = MaterialTheme.typography.bodyMedium)
                    var returnToApp by remember { mutableStateOf(true) }
                    LaunchedEffect(Unit) {
                        viewModel.settings.collect { 
                            // Note: will need to extend settings state for this
                        }
                    }
                    Switch(
                        checked = returnToApp,
                        onCheckedChange = { 
                            returnToApp = it
                            viewModel.setReturnToApp(it)
                        }
                    )
                }
            }
        },
        confirmButton = {
            Button(onClick = {
                viewModel.saveSettings(baseUrl, apiKey, modelName)
                onDismiss()
            }) { Text("保存") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("取消") }
        }
    )
}

/**
 * Templates panel showing built-in task templates.
 */
@Composable
fun TemplatesPanel(
    onSelectTemplate: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val categories = com.autoglm.phone.data.BuiltInTemplates.getCategories()
    var selectedCategory by remember { mutableStateOf(categories.firstOrNull() ?: "") }
    val templates = com.autoglm.phone.data.BuiltInTemplates.all
    
    Column(modifier = modifier) {
        // Category tabs
        ScrollableTabRow(
            selectedTabIndex = categories.indexOf(selectedCategory).coerceAtLeast(0),
            modifier = Modifier.fillMaxWidth(),
            edgePadding = 8.dp,
            containerColor = Color.Transparent,
            divider = {}
        ) {
            categories.forEach { category ->
                Tab(
                    selected = category == selectedCategory,
                    onClick = { selectedCategory = category },
                    text = { 
                        Text(
                            category, 
                            style = MaterialTheme.typography.bodyMedium
                        ) 
                    }
                )
            }
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // Template cards
        LazyColumn(
            modifier = Modifier.fillMaxWidth(),
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val filteredTemplates = templates.filter { it.category == selectedCategory }
            items(filteredTemplates) { template ->
                TemplateCard(
                    template = template,
                    onClick = { onSelectTemplate(template.prompt) }
                )
            }
        }
    }
}

@Composable
fun TemplateCard(
    template: com.autoglm.phone.data.TaskTemplate,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icon
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = template.icon,
                    fontSize = 24.sp
                )
            }
            
            Spacer(modifier = Modifier.width(12.dp))
            
            // Title and description
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = template.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = template.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            // Play button
            IconButton(onClick = onClick) {
                Icon(
                    Icons.Default.PlayArrow,
                    contentDescription = "执行",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

/**
 * Scheduled tasks management panel.
 */
@Composable
fun ScheduledTasksPanel(
    onAddTask: (String, String, Int, Int) -> Unit,  // name, prompt, hour, minute
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var showAddDialog by remember { mutableStateOf(false) }
    val scheduledTaskRepository = remember { com.autoglm.phone.data.ScheduledTaskRepository(context) }
    val scheduledTasks by scheduledTaskRepository.scheduledTasks.collectAsState(initial = emptyList())
    val coroutineScope = rememberCoroutineScope()
    
    Column(modifier = modifier.fillMaxSize()) {
        // Header with add button
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                "定时任务",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            IconButton(onClick = { showAddDialog = true }) {
                Icon(
                    Icons.Default.Add,
                    contentDescription = "添加定时任务",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
        
        if (scheduledTasks.isEmpty()) {
            // Empty state
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        Icons.Default.Alarm,
                        contentDescription = null,
                        modifier = Modifier.size(48.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        "暂无定时任务",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        "点击 + 添加每日自动执行的任务",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
            }
        } else {
            // Task list
            LazyColumn(
                modifier = Modifier.fillMaxWidth(),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(scheduledTasks) { task ->
                    ScheduledTaskCard(
                        task = task,
                        onToggle = { enabled ->
                            coroutineScope.launch {
                                scheduledTaskRepository.toggleTask(task.id, enabled)
                                if (enabled) {
                                    com.autoglm.phone.service.TaskScheduleWorker.scheduleTask(context, task.copy(isEnabled = true))
                                } else {
                                    com.autoglm.phone.service.TaskScheduleWorker.cancelTask(context, task.id)
                                }
                            }
                        },
                        onDelete = {
                            coroutineScope.launch {
                                scheduledTaskRepository.deleteTask(task.id)
                                com.autoglm.phone.service.TaskScheduleWorker.cancelTask(context, task.id)
                            }
                        }
                    )
                }
            }
        }
    }
    
    // Add task dialog
    if (showAddDialog) {
        AddScheduledTaskDialog(
            onDismiss = { showAddDialog = false },
            onConfirm = { name, prompt, hour, minute ->
                coroutineScope.launch {
                    val task = com.autoglm.phone.data.ScheduledTask(
                        name = name,
                        prompt = prompt,
                        hour = hour,
                        minute = minute,
                        repeatDays = emptyList() // Daily
                    )
                    scheduledTaskRepository.addTask(task)
                    com.autoglm.phone.service.TaskScheduleWorker.scheduleTask(context, task)
                }
                showAddDialog = false
            }
        )
    }
}

@Composable
fun ScheduledTaskCard(
    task: com.autoglm.phone.data.ScheduledTask,
    onToggle: (Boolean) -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    task.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    String.format("每天 %02d:%02d", task.hour, task.minute),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary
                )
                Text(
                    task.prompt,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
            
            Switch(
                checked = task.isEnabled,
                onCheckedChange = onToggle
            )
            
            IconButton(onClick = onDelete) {
                Icon(
                    Icons.Default.Delete,
                    contentDescription = "删除",
                    tint = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
fun AddScheduledTaskDialog(
    onDismiss: () -> Unit,
    onConfirm: (String, String, Int, Int) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var prompt by remember { mutableStateOf("") }
    var hour by remember { mutableStateOf(8) }
    var minute by remember { mutableStateOf(0) }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("添加定时任务") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("任务名称") },
                    placeholder = { Text("例如：每日签到") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = prompt,
                    onValueChange = { prompt = it },
                    label = { Text("任务描述") },
                    placeholder = { Text("例如：打开淘宝完成每日签到") },
                    minLines = 2,
                    modifier = Modifier.fillMaxWidth()
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("执行时间：", style = MaterialTheme.typography.bodyMedium)
                    Spacer(modifier = Modifier.width(8.dp))
                    
                    // Hour picker
                    OutlinedTextField(
                        value = hour.toString().padStart(2, '0'),
                        onValueChange = { 
                            val h = it.toIntOrNull() ?: 0
                            hour = h.coerceIn(0, 23)
                        },
                        modifier = Modifier.width(60.dp),
                        singleLine = true
                    )
                    Text(" : ", style = MaterialTheme.typography.titleLarge)
                    // Minute picker
                    OutlinedTextField(
                        value = minute.toString().padStart(2, '0'),
                        onValueChange = { 
                            val m = it.toIntOrNull() ?: 0
                            minute = m.coerceIn(0, 59)
                        },
                        modifier = Modifier.width(60.dp),
                        singleLine = true
                    )
                }
            }
        },
        confirmButton = {
            Button(
                onClick = { onConfirm(name, prompt, hour, minute) },
                enabled = name.isNotBlank() && prompt.isNotBlank()
            ) { Text("添加") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("取消") }
        }
    )
}
