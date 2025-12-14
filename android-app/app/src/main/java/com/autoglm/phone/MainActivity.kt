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
                        Text("AutoGLM", fontWeight = FontWeight.Bold)
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.toggleHistory() }) {
                        Icon(
                            Icons.Default.History, 
                            contentDescription = "历史",
                            tint = if (uiState.showHistory) MaterialTheme.colorScheme.primary else LocalContentColor.current
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
            
            // Main content (task input + logs)
            AnimatedVisibility(
                visible = !uiState.showHistory || uiState.isRunning,
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
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
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
                )
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
