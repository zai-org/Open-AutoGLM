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
        // Use AccessibilityService's dynamic app lookup
        // It searches installed apps by display name (exact and partial match)
        accessibilityService.launchAppByName(appName)
    }
}
