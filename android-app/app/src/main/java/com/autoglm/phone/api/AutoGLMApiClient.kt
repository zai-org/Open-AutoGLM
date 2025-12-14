package com.autoglm.phone.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST
import java.util.concurrent.TimeUnit

/**
 * Retrofit API interface for OpenAI-compatible endpoints.
 */
interface OpenAIApi {
    @POST("chat/completions")
    suspend fun chatCompletions(
        @Header("Authorization") authorization: String,
        @Body request: ChatCompletionRequest
    ): Response<ChatCompletionResponse>
}

/**
 * Client for AutoGLM API calls.
 */
class AutoGLMApiClient(private val config: ModelConfig) {
    
    private val api: OpenAIApi
    
    init {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()
        
        val retrofit = Retrofit.Builder()
            .baseUrl(config.baseUrl.trimEnd('/') + "/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        
        api = retrofit.create(OpenAIApi::class.java)
    }
    
    /**
     * Send a chat completion request.
     * 
     * @param messages List of chat messages
     * @param imageBase64 Optional base64 encoded image
     * @return ModelResponse with parsed thinking and action
     */
    suspend fun chat(
        messages: List<ChatMessage>,
        imageBase64: String? = null
    ): Result<ModelResponse> {
        return try {
            val formattedMessages = messages.map { message ->
                when (message.content) {
                    is String -> mapOf(
                        "role" to message.role,
                        "content" to message.content
                    )
                    is List<*> -> mapOf(
                        "role" to message.role,
                        "content" to message.content
                    )
                    else -> mapOf(
                        "role" to message.role,
                        "content" to message.content.toString()
                    )
                }
            }
            
            val request = ChatCompletionRequest(
                model = config.modelName,
                messages = formattedMessages,
                max_tokens = config.maxTokens,
                temperature = config.temperature,
                top_p = config.topP,
                frequency_penalty = config.frequencyPenalty,
                stream = false
            )
            
            val response = api.chatCompletions(
                authorization = "Bearer ${config.apiKey}",
                request = request
            )
            
            if (response.isSuccessful) {
                val body = response.body()
                val content = body?.choices?.firstOrNull()?.message?.content ?: ""
                val (thinking, action) = parseResponse(content)
                Result.success(ModelResponse(thinking, action, content))
            } else {
                Result.failure(Exception("API Error: ${response.code()} - ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Parse model response into thinking and action parts.
     */
    private fun parseResponse(content: String): Pair<String, String> {
        // Rule 1: Check for finish(message=
        if (content.contains("finish(message=")) {
            val parts = content.split("finish(message=", limit = 2)
            val thinking = parts[0].trim()
            val action = "finish(message=" + parts.getOrElse(1) { "" }
            return thinking to action
        }
        
        // Rule 2: Check for do(action=
        if (content.contains("do(action=")) {
            val parts = content.split("do(action=", limit = 2)
            val thinking = parts[0].trim()
            val action = "do(action=" + parts.getOrElse(1) { "" }
            return thinking to action
        }
        
        // Rule 3: Legacy XML tag parsing
        if (content.contains("<answer>")) {
            val parts = content.split("<answer>", limit = 2)
            val thinking = parts[0]
                .replace("<think>", "")
                .replace("</think>", "")
                .trim()
            val action = parts.getOrElse(1) { "" }
                .replace("</answer>", "")
                .trim()
            return thinking to action
        }
        
        // Rule 4: No markers found
        return "" to content
    }
    
    companion object {
        /**
         * Build user message content with optional image.
         */
        fun buildUserContent(text: String, imageBase64: String? = null): Any {
            return if (imageBase64 != null) {
                listOf(
                    mapOf(
                        "type" to "image_url",
                        "image_url" to mapOf("url" to "data:image/png;base64,$imageBase64")
                    ),
                    mapOf(
                        "type" to "text",
                        "text" to text
                    )
                )
            } else {
                text
            }
        }
    }
}
