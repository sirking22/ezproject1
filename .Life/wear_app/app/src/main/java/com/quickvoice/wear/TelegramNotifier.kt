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

class TelegramNotifier {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .build()
    
    private val botToken = "your_telegram_bot_token"
    private val chatId = "your_chat_id"
    private val mediaType = "application/json; charset=utf-8".toMediaType()
    
    suspend fun sendNotification(message: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val requestBody = JSONObject().apply {
                    put("chat_id", chatId)
                    put("text", "⌚ $message")
                    put("parse_mode", "HTML")
                }.toString()
                
                val request = Request.Builder()
                    .url("https://api.telegram.org/bot$botToken/sendMessage")
                    .post(requestBody.toRequestBody(mediaType))
                    .addHeader("Content-Type", "application/json")
                    .build()
                
                val response = client.newCall(request).execute()
                response.isSuccessful
            } catch (e: Exception) {
                false
            }
        }
    }
    
    suspend fun sendQuickUpdate(data: Map<String, Any>): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val message = formatQuickUpdate(data)
                sendNotification(message)
            } catch (e: Exception) {
                false
            }
        }
    }
    
    private fun formatQuickUpdate(data: Map<String, Any>): String {
        val type = data["type"] as String
        val content = data["content"] as String
        
        return when (type) {
            "task" -> "✅ Задача: $content"
            "reflection" -> "💭 Мысль: $content"
            "habit" -> "🔄 Привычка: $content"
            else -> "📱 Обновление: $content"
        }
    }
    
    suspend fun testConnection(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("https://api.telegram.org/bot$botToken/getMe")
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