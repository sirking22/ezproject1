package com.quickvoice

import java.time.LocalDateTime
import java.time.LocalTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ContextManager {
    
    private var currentContext = "home"
    private var lastActivityTime = LocalDateTime.now()
    private var userPreferences = mutableMapOf<String, Any>()
    
    fun getCurrentContext(): String {
        val now = LocalDateTime.now()
        val time = now.toLocalTime()
        
        return when {
            isMorningTime(time) -> "morning"
            isWorkTime(time) -> "work"
            isEveningTime(time) -> "evening"
            isNightTime(time) -> "night"
            else -> "home"
        }
    }
    
    private fun isMorningTime(time: LocalTime): Boolean {
        return time.isAfter(LocalTime.of(5, 0)) && 
               time.isBefore(LocalTime.of(11, 0))
    }
    
    private fun isWorkTime(time: LocalTime): Boolean {
        return time.isAfter(LocalTime.of(9, 0)) && 
               time.isBefore(LocalTime.of(18, 0))
    }
    
    private fun isEveningTime(time: LocalTime): Boolean {
        return time.isAfter(LocalTime.of(18, 0)) && 
               time.isBefore(LocalTime.of(22, 0))
    }
    
    private fun isNightTime(time: LocalTime): Boolean {
        return time.isAfter(LocalTime.of(22, 0)) || 
               time.isBefore(LocalTime.of(5, 0))
    }
    
    fun getUserContext(): Map<String, Any> {
        val context = mutableMapOf<String, Any>()
        
        // Время дня
        context["time_of_day"] = getCurrentContext()
        context["current_time"] = LocalDateTime.now().toString()
        
        // День недели
        context["day_of_week"] = LocalDateTime.now().dayOfWeek.toString()
        
        // Активность
        context["last_activity"] = lastActivityTime.toString()
        context["activity_gap_minutes"] = 
            java.time.Duration.between(lastActivityTime, LocalDateTime.now()).toMinutes()
        
        // Пользовательские предпочтения
        context.putAll(userPreferences)
        
        return context
    }
    
    fun updateActivity() {
        lastActivityTime = LocalDateTime.now()
    }
    
    fun setUserPreference(key: String, value: Any) {
        userPreferences[key] = value
    }
    
    fun getUserPreference(key: String): Any? {
        return userPreferences[key]
    }
    
    fun getContextualPrompt(command: String): String {
        val context = getCurrentContext()
        val userContext = getUserContext()
        
        return when (context) {
            "morning" -> buildMorningPrompt(command, userContext)
            "work" -> buildWorkPrompt(command, userContext)
            "evening" -> buildEveningPrompt(command, userContext)
            "night" -> buildNightPrompt(command, userContext)
            else -> buildDefaultPrompt(command, userContext)
        }
    }
    
    private fun buildMorningPrompt(command: String, context: Map<String, Any>): String {
        return """
            Ты утренний ассистент. Сейчас утро, время планировать день и настраиваться на продуктивность.
            
            Контекст:
            - Время дня: ${context["time_of_day"]}
            - День недели: ${context["day_of_week"]}
            - Последняя активность: ${context["last_activity"]}
            
            Команда: $command
            
            Ответь мотивирующе и помоги настроиться на продуктивный день. Предложи план действий.
        """.trimIndent()
    }
    
    private fun buildWorkPrompt(command: String, context: Map<String, Any>): String {
        return """
            Ты рабочий ассистент. Сейчас рабочее время, фокус на продуктивности и задачах.
            
            Контекст:
            - Время дня: ${context["time_of_day"]}
            - День недели: ${context["day_of_week"]}
            - Последняя активность: ${context["last_activity"]}
            
            Команда: $command
            
            Ответь кратко и по делу. Помоги с рабочими задачами и планированием.
        """.trimIndent()
    }
    
    private fun buildEveningPrompt(command: String, context: Map<String, Any>): String {
        return """
            Ты вечерний ассистент. Сейчас вечер, время для рефлексии и планирования завтра.
            
            Контекст:
            - Время дня: ${context["time_of_day"]}
            - День недели: ${context["day_of_week"]}
            - Последняя активность: ${context["last_activity"]}
            
            Команда: $command
            
            Помоги проанализировать день и подготовиться к завтрашнему дню.
        """.trimIndent()
    }
    
    private fun buildNightPrompt(command: String, context: Map<String, Any>): String {
        return """
            Ты ночной ассистент. Сейчас ночь, время для отдыха и спокойных размышлений.
            
            Контекст:
            - Время дня: ${context["time_of_day"]}
            - День недели: ${context["day_of_week"]}
            - Последняя активность: ${context["last_activity"]}
            
            Команда: $command
            
            Ответь спокойно и расслабленно. Помоги подготовиться ко сну.
        """.trimIndent()
    }
    
    private fun buildDefaultPrompt(command: String, context: Map<String, Any>): String {
        return """
            Ты персональный ассистент. Обрабатывай команды естественно и полезно.
            
            Контекст:
            - Время дня: ${context["time_of_day"]}
            - День недели: ${context["day_of_week"]}
            - Последняя активность: ${context["last_activity"]}
            
            Команда: $command
            
            Ответь понятно и полезно.
        """.trimIndent()
    }
    
    fun shouldSendNotification(command: String, context: String): Boolean {
        return when (context) {
            "work" -> command.contains("задача", ignoreCase = true) || 
                     command.contains("встреча", ignoreCase = true)
            "morning" -> command.contains("ритуал", ignoreCase = true) || 
                        command.contains("план", ignoreCase = true)
            "evening" -> command.contains("рефлексия", ignoreCase = true) || 
                        command.contains("анализ", ignoreCase = true)
            else -> true
        }
    }
    
    fun getNotificationPriority(context: String): String {
        return when (context) {
            "work" -> "high"
            "morning" -> "normal"
            "evening" -> "normal"
            "night" -> "low"
            else -> "normal"
        }
    }
    
    suspend fun analyzeUserPatterns(): Map<String, Any> {
        return withContext(Dispatchers.Default) {
            val patterns = mutableMapOf<String, Any>()
            
            // Анализ времени активности
            val now = LocalDateTime.now()
            val activityGap = java.time.Duration.between(lastActivityTime, now).toMinutes()
            
            patterns["activity_gap_minutes"] = activityGap
            patterns["is_active_user"] = activityGap < 60
            patterns["preferred_time"] = getCurrentContext()
            patterns["last_activity_type"] = "voice_command"
            
            patterns
        }
    }
} 