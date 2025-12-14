package com.autoglm.phone.agent

import com.autoglm.phone.api.AutoGLMApiClient
import com.autoglm.phone.api.ChatMessage
import com.autoglm.phone.api.ModelConfig
import com.autoglm.phone.service.AutoGLMAccessibilityService
import com.autoglm.phone.service.ScreenshotHelper
import com.google.gson.Gson
import kotlinx.coroutines.delay
import java.text.SimpleDateFormat
import java.util.*

/**
 * Main PhoneAgent class that orchestrates phone automation.
 * 
 * Mirrors the Python PhoneAgent logic from phone_agent/agent.py
 */
class PhoneAgent(
    private val config: ModelConfig,
    private val accessibilityService: AutoGLMAccessibilityService,
    private val screenshotHelper: ScreenshotHelper,
    private val onLog: (String) -> Unit = {},
    private val onStep: (Int, String) -> Unit = { _, _ -> },
    private val onHideOverlay: (Boolean) -> Unit = {} // true=hide, false=show
) {
    private val apiClient = AutoGLMApiClient(config)
    private val actionHandler = ActionHandler(accessibilityService)
    private val gson = Gson()
    
    private var context = mutableListOf<ChatMessage>()
    private var stepCount = 0
    private var isRunning = false
    
    private val maxSteps = 100
    
    companion object {
        private val DATE_FORMAT = SimpleDateFormat("yyyy年MM月dd日", Locale.CHINA)
        
        private fun getSystemPrompt(): String {
            val today = DATE_FORMAT.format(Date())
            return """今天的日期是: $today
你是一个智能体分析专家，可以根据操作历史和当前状态图执行一系列操作来完成任务。
你必须严格按照要求输出以下格式：
<think>{think}</think>
<answer>{action}</answer>

其中：
- {think} 是对你为什么选择这个操作的简短推理说明。
- {action} 是本次执行的具体操作指令，必须严格遵循下方定义的指令格式。

**重要提示：**
截图底部可能显示AutoPhone的悬浮状态栏（如"步骤X: ..."或日志信息），这是自动化工具的UI，不是目标应用的一部分，请忽略它们，专注于实际应用界面进行操作。

**可用操作：**

- do(action="Tap", element=[x,y])  
    点击屏幕上的特定点。坐标系统从左上角 (0,0) 开始到右下角（999,999)结束。

- do(action="Type", text="内容")  
    输入文字到当前输入框。

- do(action="Swipe", direction="up/down/left/right")  
    向指定方向滑动屏幕。

- do(action="Launch", app="应用名")  
    启动指定应用。

- do(action="Back")  
    返回上一页。

- do(action="Home")  
    返回主屏幕。

- do(action="Wait")  
    等待页面加载。

- finish(message="任务完成说明")  
    任务完成时调用，说明完成情况。"""
        }
    }
    
    /**
     * Run a task until completion.
     * @param task Natural language task description
     * @return Final message from agent
     */
    suspend fun run(task: String): String {
        reset()
        isRunning = true
        
        log("📝 开始任务: $task")
        
        // Initialize context with system prompt
        context.add(ChatMessage("system", getSystemPrompt()))
        
        var lastMessage = ""
        
        while (isRunning && stepCount < maxSteps) {
            val result = step(if (stepCount == 0) task else null)
            
            if (!result.success) {
                log("❌ 步骤失败: ${result.message}")
                lastMessage = result.message ?: "Unknown error"
                break
            }
            
            if (result.finished) {
                lastMessage = result.message ?: "任务完成"
                log("✅ 任务完成: $lastMessage")
                break
            }
            
            // Small delay between steps
            delay(500)
        }
        
        if (stepCount >= maxSteps) {
            lastMessage = "已达到最大步数限制 ($maxSteps)"
            log("⚠️ $lastMessage")
        }
        
        isRunning = false
        return lastMessage
    }
    
    /**
     * Execute a single step.
     */
    suspend fun step(task: String? = null): StepResult {
        stepCount++
        onStep(stepCount, "截取屏幕中...")
        log("🔄 步骤 $stepCount")
        
        try {
            // Take screenshot using ScreenshotHelper (works on Android 9+)
            val screenshot = screenshotHelper.takeScreenshot()
            
            onStep(stepCount, "分析屏幕中...")
            
            if (screenshot == null) {
                return StepResult(
                    success = false,
                    finished = true,
                    action = null,
                    thinking = "",
                    message = "无法截取屏幕"
                )
            }
            
            // Get current app
            val currentApp = accessibilityService.getCurrentApp() ?: "unknown"
            
            // Build screen info
            val screenInfo = gson.toJson(mapOf("current_app" to currentApp))
            
            // Build user message
            val userText = if (task != null) {
                "任务: $task\n当前状态: $screenInfo"
            } else {
                "当前状态: $screenInfo"
            }
            
            val userContent = AutoGLMApiClient.buildUserContent(userText, screenshot)
            context.add(ChatMessage("user", userContent))
            
            // Call API
            onStep(stepCount, "AI思考中...")
            log("💭 思考中...")
            val response = apiClient.chat(context, screenshot)
            
            if (response.isFailure) {
                val error = response.exceptionOrNull()?.message ?: "API调用失败"
                return StepResult(
                    success = false,
                    finished = true,
                    action = null,
                    thinking = "",
                    message = error
                )
            }
            
            val modelResponse = response.getOrNull()!!
            log("💡 思考: ${modelResponse.thinking.take(100)}...")
            
            // Add assistant response to context
            context.add(ChatMessage("assistant", modelResponse.rawContent))
            
            // Remove image from previous user message to save context
            removeLastUserImage()
            
            // Parse and execute action
            val action = actionHandler.parseAction(modelResponse.action)
            
            // Generate user-friendly action description
            val actionDesc = getActionDescription(action)
            onStep(stepCount, actionDesc)
            log("⚡ 动作: $action")
            
            val (finished, message) = actionHandler.executeAction(action)
            
            return StepResult(
                success = true,
                finished = finished,
                action = action,
                thinking = modelResponse.thinking,
                message = message
            )
            
        } catch (e: Exception) {
            log("❌ 错误: ${e.message}")
            return StepResult(
                success = false,
                finished = true,
                action = null,
                thinking = "",
                message = e.message
            )
        }
    }
    
    /**
     * Stop the running task.
     */
    fun stop() {
        isRunning = false
        log("🛑 任务已停止")
    }
    
    /**
     * Reset agent state for a new task.
     */
    fun reset() {
        context.clear()
        stepCount = 0
        isRunning = false
    }
    
    private fun log(message: String) {
        onLog(message)
        android.util.Log.d("PhoneAgent", message)
    }
    
    /**
     * Remove image from the last user message to save context space.
     */
    private fun removeLastUserImage() {
        val lastUserIndex = context.indexOfLast { it.role == "user" }
        if (lastUserIndex >= 0) {
            val message = context[lastUserIndex]
            if (message.content is List<*>) {
                val textOnly = (message.content as List<*>).filterIsInstance<Map<*, *>>()
                    .filter { it["type"] == "text" }
                context[lastUserIndex] = ChatMessage("user", textOnly)
            }
        }
    }
    
    /**
     * Generate user-friendly action description for floating status.
     */
    private fun getActionDescription(action: ParsedAction): String {
        return when (action) {
            is ParsedAction.Do -> {
                when (action.action.lowercase()) {
                    "tap" -> {
                        if (action.element != null) 
                            "点击屏幕 (${action.element[0]}, ${action.element[1]})"
                        else "点击屏幕"
                    }
                    "type" -> {
                        if (action.text != null) 
                            "输入: ${action.text.take(15)}..."
                        else "输入文字"
                    }
                    "swipe" -> {
                        val direction = when (action.direction) {
                            "up" -> "上"
                            "down" -> "下"
                            "left" -> "左"
                            "right" -> "右"
                            else -> ""
                        }
                        "向${direction}滑动"
                    }
                    "launch" -> "打开应用: ${action.app ?: "未知"}"
                    "back" -> "返回"
                    "home" -> "回到桌面"
                    "wait" -> "等待页面加载"
                    else -> action.action
                }
            }
            is ParsedAction.Finish -> "任务完成"
            is ParsedAction.Error -> "错误: ${action.message}"
        }
    }
}
