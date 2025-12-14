package com.autoglm.phone.agent

import java.util.regex.Pattern

/**
 * Parsed action from model response.
 */
sealed class ParsedAction {
    data class Do(
        val action: String,
        val element: List<Int>? = null,
        val message: String? = null,
        val app: String? = null,
        val text: String? = null,
        val direction: String? = null
    ) : ParsedAction()
    
    data class Finish(
        val message: String
    ) : ParsedAction()
    
    data class Error(
        val message: String
    ) : ParsedAction()
}

/**
 * Result of a single step execution.
 */
data class StepResult(
    val success: Boolean,
    val finished: Boolean,
    val action: ParsedAction?,
    val thinking: String,
    val message: String? = null
)

/**
 * Handler for parsing and executing actions from model output.
 */
class ActionHandler(
    private val accessibilityService: com.autoglm.phone.service.AutoGLMAccessibilityService
) {
    
    /**
     * Parse action string from model response.
     */
    fun parseAction(response: String): ParsedAction {
        // Check for finish action
        val finishPattern = Pattern.compile("""finish\(message=["'](.+?)["']\)""", Pattern.DOTALL)
        val finishMatcher = finishPattern.matcher(response)
        if (finishMatcher.find()) {
            return ParsedAction.Finish(finishMatcher.group(1) ?: "")
        }
        
        // Check for do action
        val doPattern = Pattern.compile("""do\((.+?)\)""", Pattern.DOTALL)
        val doMatcher = doPattern.matcher(response)
        if (doMatcher.find()) {
            val argsString = doMatcher.group(1) ?: ""
            return parseDoAction(argsString)
        }
        
        return ParsedAction.Error("Cannot parse action from response")
    }
    
    private fun parseDoAction(argsString: String): ParsedAction {
        val params = mutableMapOf<String, String>()
        
        // Parse action parameter
        val actionPattern = Pattern.compile("""action=["'](\w+)["']""")
        val actionMatcher = actionPattern.matcher(argsString)
        if (actionMatcher.find()) {
            params["action"] = actionMatcher.group(1) ?: ""
        }
        
        // Parse element parameter (coordinates)
        val elementPattern = Pattern.compile("""element=\[(\d+),\s*(\d+)\]""")
        val elementMatcher = elementPattern.matcher(argsString)
        var element: List<Int>? = null
        if (elementMatcher.find()) {
            element = listOf(
                elementMatcher.group(1)?.toIntOrNull() ?: 0,
                elementMatcher.group(2)?.toIntOrNull() ?: 0
            )
        }
        
        // Parse message parameter
        val messagePattern = Pattern.compile("""message=["'](.+?)["']""")
        val messageMatcher = messagePattern.matcher(argsString)
        if (messageMatcher.find()) {
            params["message"] = messageMatcher.group(1) ?: ""
        }
        
        // Parse app parameter
        val appPattern = Pattern.compile("""app=["'](.+?)["']""")
        val appMatcher = appPattern.matcher(argsString)
        if (appMatcher.find()) {
            params["app"] = appMatcher.group(1) ?: ""
        }
        
        // Parse text parameter
        val textPattern = Pattern.compile("""text=["'](.+?)["']""")
        val textMatcher = textPattern.matcher(argsString)
        if (textMatcher.find()) {
            params["text"] = textMatcher.group(1) ?: ""
        }
        
        // Parse direction parameter
        val dirPattern = Pattern.compile("""direction=["'](\w+)["']""")
        val dirMatcher = dirPattern.matcher(argsString)
        if (dirMatcher.find()) {
            params["direction"] = dirMatcher.group(1) ?: ""
        }
        
        return ParsedAction.Do(
            action = params["action"] ?: "",
            element = element,
            message = params["message"],
            app = params["app"],
            text = params["text"],
            direction = params["direction"]
        )
    }
    
    /**
     * Execute a parsed action.
     * @return true if the action should finish the task
     */
    suspend fun executeAction(action: ParsedAction): Pair<Boolean, String?> {
        return when (action) {
            is ParsedAction.Finish -> {
                Pair(true, action.message)
            }
            is ParsedAction.Do -> {
                executeDoAction(action)
                Pair(false, null)
            }
            is ParsedAction.Error -> {
                Pair(true, "Error: ${action.message}")
            }
        }
    }
    
    private suspend fun executeDoAction(action: ParsedAction.Do) {
        val (screenWidth, screenHeight) = accessibilityService.getScreenSize()
        
        when (action.action.lowercase()) {
            "tap" -> {
                action.element?.let { coords ->
                    // Convert from 0-1000 relative to absolute pixels
                    val x = (coords[0] * screenWidth / 1000f)
                    val y = (coords[1] * screenHeight / 1000f)
                    accessibilityService.tap(x, y)
                }
            }
            "swipe" -> {
                handleSwipe(action, screenWidth, screenHeight)
            }
            "type" -> {
                action.text?.let { text ->
                    accessibilityService.typeText(text)
                }
            }
            "launch" -> {
                action.app?.let { app ->
                    launchAppByName(app)
                }
            }
            "back" -> {
                accessibilityService.pressBack()
            }
            "home" -> {
                accessibilityService.pressHome()
            }
            "double_tap" -> {
                action.element?.let { coords ->
                    val x = (coords[0] * screenWidth / 1000f)
                    val y = (coords[1] * screenHeight / 1000f)
                    accessibilityService.doubleTap(x, y)
                }
            }
            "long_press" -> {
                action.element?.let { coords ->
                    val x = (coords[0] * screenWidth / 1000f)
                    val y = (coords[1] * screenHeight / 1000f)
                    accessibilityService.longPress(x, y)
                }
            }
            "wait" -> {
                kotlinx.coroutines.delay(2000)
            }
        }
    }
    
    private suspend fun handleSwipe(action: ParsedAction.Do, screenWidth: Int, screenHeight: Int) {
        val direction = action.direction?.lowercase() ?: return
        val centerX = screenWidth / 2f
        val centerY = screenHeight / 2f
        val swipeDistance = screenHeight / 3f
        
        when (direction) {
            "up" -> {
                accessibilityService.swipe(
                    centerX, centerY + swipeDistance/2,
                    centerX, centerY - swipeDistance/2
                )
            }
            "down" -> {
                accessibilityService.swipe(
                    centerX, centerY - swipeDistance/2,
                    centerX, centerY + swipeDistance/2
                )
            }
            "left" -> {
                accessibilityService.swipe(
                    centerX + swipeDistance/2, centerY,
                    centerX - swipeDistance/2, centerY
                )
            }
            "right" -> {
                accessibilityService.swipe(
                    centerX - swipeDistance/2, centerY,
                    centerX + swipeDistance/2, centerY
                )
            }
        }
    }
    
    private fun launchAppByName(appName: String) {
        // Map common app names to package names
        val packageMap = mapOf(
            "微信" to "com.tencent.mm",
            "wechat" to "com.tencent.mm",
            "淘宝" to "com.taobao.taobao",
            "taobao" to "com.taobao.taobao",
            "支付宝" to "com.eg.android.AlipayGphone",
            "alipay" to "com.eg.android.AlipayGphone",
            "抖音" to "com.ss.android.ugc.aweme",
            "douyin" to "com.ss.android.ugc.aweme",
            "京东" to "com.jingdong.app.mall",
            "jd" to "com.jingdong.app.mall",
            "美团" to "com.sankuai.meituan",
            "meituan" to "com.sankuai.meituan",
            "设置" to "com.android.settings",
            "settings" to "com.android.settings",
            "浏览器" to "com.android.browser",
            "browser" to "com.android.browser",
            "相机" to "com.android.camera",
            "camera" to "com.android.camera",
            "小红书" to "com.xingin.xhs",
            "xiaohongshu" to "com.xingin.xhs",
            "地图" to "com.autonavi.minimap",
            "高德" to "com.autonavi.minimap",
            "amap" to "com.autonavi.minimap",
            "百度地图" to "com.baidu.BaiduMap",
            "qq" to "com.tencent.mobileqq",
            "QQ" to "com.tencent.mobileqq"
        )
        
        val packageName = packageMap[appName.lowercase()] 
            ?: packageMap[appName]
            ?: appName  // Assume it's a package name if not in map
        
        accessibilityService.launchApp(packageName)
    }
}
