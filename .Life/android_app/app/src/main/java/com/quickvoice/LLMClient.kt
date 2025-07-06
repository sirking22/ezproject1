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

class LLMClient {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val baseUrl = "http://192.168.1.100:8000" // Локальный сервер LLM
    private val mediaType = "application/json; charset=utf-8".toMediaType()
    
    suspend fun processCommand(command: String, context: String = "home"): String {
        return withContext(Dispatchers.IO) {
            try {
                val prompt = buildPrompt(command, context)
                val response = sendRequest(prompt, context)
                parseResponse(response)
            } catch (e: Exception) {
                "Ошибка обработки команды: ${e.message}"
            }
        }
    }
    
    private fun buildPrompt(command: String, context: String): String {
        val systemPrompt = when (context) {
            "work" -> """
                Ты рабочий ассистент. Обрабатывай команды кратко и по делу.
                Формат ответа: краткое описание действия + результат.
                Примеры:
                - "Добавить задачу" → "Задача 'название' добавлена в рабочий список"
                - "Показать прогресс" → "Завершено 5 из 8 задач на этой неделе"
            """.trimIndent()
            
            "morning" -> """
                Ты утренний ассистент. Помогай планировать день и создавать ритуалы.
                Формат ответа: мотивирующее сообщение + план действий.
                Примеры:
                - "Утренний ритуал" → "Доброе утро! План на день: медитация, завтрак, работа"
                - "Задачи дня" → "Ключевые задачи: 1) Проект А, 2) Встреча с командой"
            """.trimIndent()
            
            "evening" -> """
                Ты вечерний ассистент. Помогай рефлексировать и планировать завтра.
                Формат ответа: анализ дня + рекомендации.
                Примеры:
                - "Вечерняя рефлексия" → "День был продуктивным. Завтра сосредоточься на..."
                - "Анализ настроения" → "Настроение стабильное. Рекомендую отдых"
            """.trimIndent()
            
            else -> """
                Ты персональный ассистент. Обрабатывай команды естественно и полезно.
                Формат ответа: понятное описание действия + результат.
                Примеры:
                - "Добавить задачу" → "Задача 'название' добавлена в список"
                - "Записать мысль" → "Мысль 'содержание' сохранена в рефлексии"
                - "Показать прогресс" → "Ваш прогресс: 3 привычки подряд, 5 задач выполнено"
            """.trimIndent()
        }
        
        return """
            $systemPrompt
            
            Команда пользователя: $command
            
            Ответ:
        """.trimIndent()
    }
    
    private fun sendRequest(prompt: String, context: String): String {
        val jsonBody = JSONObject().apply {
            put("prompt", prompt)
            put("context", context)
            put("max_tokens", 150)
            put("temperature", 0.7)
        }.toString()
        
        val request = Request.Builder()
            .url("$baseUrl/generate")
            .post(jsonBody.toRequestBody(mediaType))
            .addHeader("Content-Type", "application/json")
            .build()
        
        return client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("HTTP ${response.code}: ${response.message}")
            }
            response.body?.string() ?: throw IOException("Пустой ответ от сервера")
        }
    }
    
    private fun parseResponse(response: String): String {
        return try {
            val jsonResponse = JSONObject(response)
            jsonResponse.optString("response", "Не удалось получить ответ")
        } catch (e: Exception) {
            "Ошибка парсинга ответа: ${e.message}"
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
    
    suspend fun getContextualResponse(
        command: String,
        userContext: Map<String, Any>
    ): String {
        return withContext(Dispatchers.IO) {
            try {
                val contextPrompt = buildContextualPrompt(command, userContext)
                val response = sendRequest(contextPrompt, "contextual")
                parseResponse(response)
            } catch (e: Exception) {
                "Ошибка контекстной обработки: ${e.message}"
            }
        }
    }
    
    private fun buildContextualPrompt(command: String, context: Map<String, Any>): String {
        val contextInfo = context.entries.joinToString("\n") { (key, value) ->
            "- $key: $value"
        }
        
        return """
            Ты персональный ассистент с контекстом пользователя.
            
            Контекст:
            $contextInfo
            
            Команда: $command
            
            Учти контекст при ответе и дай персонализированный ответ.
            
            Ответ:
        """.trimIndent()
    }
} 