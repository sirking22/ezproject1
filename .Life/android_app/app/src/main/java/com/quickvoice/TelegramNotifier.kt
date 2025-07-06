package com.quickvoice

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
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val botToken = "your_telegram_bot_token" // Из конфигурации
    private val chatId = "your_chat_id" // Из конфигурации
    private val mediaType = "application/json; charset=utf-8".toMediaType()
    
    suspend fun sendNotification(message: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val requestBody = JSONObject().apply {
                    put("chat_id", chatId)
                    put("text", message)
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
        val timestamp = java.time.LocalDateTime.now().format(
            java.time.format.DateTimeFormatter.ofPattern("HH:mm")
        )
        
        return when (type) {
            "task" -> """
                ✅ <b>Новая задача</b>
                📝 $content
                ⏰ $timestamp
                📱 Добавлено через голосовой ассистент
            """.trimIndent()
            
            "reflection" -> """
                💭 <b>Новая мысль</b>
                📝 $content
                ⏰ $timestamp
                🎤 Записано голосом
            """.trimIndent()
            
            "habit" -> """
                🔄 <b>Привычка отмечена</b>
                📝 $content
                ⏰ $timestamp
                ✅ Выполнено
            """.trimIndent()
            
            "idea" -> """
                💡 <b>Новая идея</b>
                📝 $content
                ⏰ $timestamp
                🎤 Записано голосом
            """.trimIndent()
            
            else -> """
                📱 <b>Обновление</b>
                📝 $content
                ⏰ $timestamp
            """.trimIndent()
        }
    }
    
    suspend fun sendDailySummary(summary: Map<String, Any>): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val message = formatDailySummary(summary)
                sendNotification(message)
            } catch (e: Exception) {
                false
            }
        }
    }
    
    private fun formatDailySummary(summary: Map<String, Any>): String {
        val date = summary["date"] as String
        val tasksCompleted = summary["tasks_completed"] as Int
        val tasksTotal = summary["tasks_total"] as Int
        val habitsCompleted = summary["habits_completed"] as Int
        val reflectionsCount = summary["reflections_count"] as Int
        val mood = summary["mood"] as String
        
        return """
            📊 <b>Дневной отчет</b>
            📅 $date
            
            ✅ Задачи: $tasksCompleted/$tasksTotal
            🔄 Привычки: $habitsCompleted выполнено
            💭 Рефлексии: $reflectionsCount записей
            😊 Настроение: $mood
            
            🎯 Продолжай в том же духе!
        """.trimIndent()
    }
    
    suspend fun sendContextualNotification(
        message: String,
        context: String,
        priority: String = "normal"
    ): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val formattedMessage = formatContextualMessage(message, context, priority)
                sendNotification(formattedMessage)
            } catch (e: Exception) {
                false
            }
        }
    }
    
    private fun formatContextualMessage(
        message: String,
        context: String,
        priority: String
    ): String {
        val emoji = when (context) {
            "work" -> "💼"
            "morning" -> "🌅"
            "evening" -> "🌙"
            "health" -> "🏃‍♂️"
            else -> "📱"
        }
        
        val priorityEmoji = when (priority) {
            "high" -> "🚨"
            "normal" -> "📢"
            "low" -> "💬"
            else -> "📢"
        }
        
        val timestamp = java.time.LocalDateTime.now().format(
            java.time.format.DateTimeFormatter.ofPattern("HH:mm")
        )
        
        return """
            $priorityEmoji $emoji <b>Уведомление</b>
            📝 $message
            ⏰ $timestamp
            🎤 Голосовой ассистент
        """.trimIndent()
    }
    
    suspend fun sendErrorNotification(error: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val message = """
                    ⚠️ <b>Ошибка в системе</b>
                    🚨 $error
                    ⏰ ${java.time.LocalDateTime.now().format(
                        java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss")
                    )}
                    📱 Android приложение
                """.trimIndent()
                
                sendNotification(message)
            } catch (e: Exception) {
                false
            }
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
    
    suspend fun sendVoiceCommandLog(command: String, response: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val message = """
                    🎤 <b>Голосовая команда</b>
                    📝 Команда: $command
                    💬 Ответ: $response
                    ⏰ ${java.time.LocalDateTime.now().format(
                        java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss")
                    )}
                """.trimIndent()
                
                sendNotification(message)
            } catch (e: Exception) {
                false
            }
        }
    }
} 