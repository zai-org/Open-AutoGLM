package com.autoglm.phone.api

/**
 * Configuration for the AI model.
 */
data class ModelConfig(
    val baseUrl: String = "https://open.bigmodel.cn/api/paas/v4",
    val apiKey: String = "",
    val modelName: String = "autoglm-phone",
    val maxTokens: Int = 3000,
    val temperature: Float = 0.0f,
    val topP: Float = 0.85f,
    val frequencyPenalty: Float = 0.2f
)

/**
 * A chat message.
 */
data class ChatMessage(
    val role: String,     // "system", "user", or "assistant"
    val content: Any      // String or List of content parts
)

/**
 * Content part for multimodal messages.
 */
sealed class ContentPart {
    data class Text(val text: String) : ContentPart()
    data class ImageUrl(val imageUrl: ImageUrlData) : ContentPart()
}

data class ImageUrlData(val url: String)

/**
 * Response from the model.
 */
data class ModelResponse(
    val thinking: String,
    val action: String,
    val rawContent: String
)

/**
 * Request body for chat completions.
 */
data class ChatCompletionRequest(
    val model: String,
    val messages: List<Map<String, Any>>,
    val max_tokens: Int,
    val temperature: Float,
    val top_p: Float,
    val frequency_penalty: Float,
    val stream: Boolean = false
)

/**
 * Response from chat completions API.
 */
data class ChatCompletionResponse(
    val id: String?,
    val choices: List<Choice>
)

data class Choice(
    val index: Int,
    val message: MessageContent?,
    val finish_reason: String?
)

data class MessageContent(
    val role: String?,
    val content: String?
)
