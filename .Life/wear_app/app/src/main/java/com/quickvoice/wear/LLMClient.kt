package com.quickvoice.wear

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

class LLMClient {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS) // Уменьшенный таймаут для часов
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .build()
    
    private val baseUrl = "http://192.168.1.100:8000"
    private val mediaType = "application/json; charset=utf-8".toMediaType()
    
    suspend fun processCommand(command: String, context: String = "wear"): String {
        return withContext(Dispatchers.IO) {
            try {
                val prompt = buildWearPrompt(command, context)
                val response = sendRequest(prompt, context)
                parseResponse(response)
            } catch (e: Exception) {
                "Ошибка: ${e.message}"
            }
        }
    }
    
    private fun buildWearPrompt(command: String, context: String): String {
        return """
            Ты ассистент для смарт-часов. Отвечай кратко и по делу.
            
            Команда: $command
            
            Контекст: $context
            
            Ответь максимально кратко, максимум 50 символов.
        """.trimIndent()
    }
    
    private fun sendRequest(prompt: String, context: String): String {
        val jsonBody = JSONObject().apply {
            put("prompt", prompt)
            put("context", context)
            put("max_tokens", 50) // Ограниченное количество токенов
            put("temperature", 0.7)
        }.toString()
        
        val request = Request.Builder()
            .url("$baseUrl/generate")
            .post(jsonBody.toRequestBody(mediaType))
            .addHeader("Content-Type", "application/json")
            .build()
        
        return client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("HTTP ${response.code}")
            }
            response.body?.string() ?: throw IOException("Пустой ответ")
        }
    }
    
    private fun parseResponse(response: String): String {
        return try {
            val jsonResponse = JSONObject(response)
            jsonResponse.optString("response", "Ошибка")
        } catch (e: Exception) {
            "Ошибка парсинга"
        }
    }
    
    suspend fun testConnection(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("$baseUrl/health")
                    .get()
                    .build()
                
                val response = client.newCall(request).execute()
                response.isSuccessful
            } catch (e: Exception) {
                false
            }
        }
    }
} 