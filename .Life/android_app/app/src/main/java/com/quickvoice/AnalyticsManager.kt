package com.quickvoice

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import org.json.JSONObject
import org.json.JSONArray

class AnalyticsManager(private val context: Context) {
    
    private val sharedPrefs: SharedPreferences = context.getSharedPreferences("QuickVoiceAnalytics", Context.MODE_PRIVATE)
    private val telegramNotifier = TelegramNotifier()
    
    data class VoiceCommand(
        val command: String,
        val timestamp: String,
        val context: String,
        val success: Boolean,
        val responseTime: Long,
        val error: String? = null
    )
    
    data class UsageStats(
        val totalCommands: Int,
        val successfulCommands: Int,
        val averageResponseTime: Long,
        val mostUsedCommands: List<String>,
        val contextDistribution: Map<String, Int>,
        val dailyUsage: Map<String, Int>
    )
    
    fun logVoiceCommand(
        command: String,
        context: String,
        success: Boolean,
        responseTime: Long,
        error: String? = null
    ) {
        val timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
        
        val voiceCommand = VoiceCommand(
            command = command,
            timestamp = timestamp,
            context = context,
            success = success,
            responseTime = responseTime,
            error = error
        )
        
        saveVoiceCommand(voiceCommand)
    }
    
    private fun saveVoiceCommand(voiceCommand: VoiceCommand) {
        val commands = getVoiceCommands().toMutableList()
        commands.add(voiceCommand)
        
        // Ограничиваем количество сохраненных команд
        if (commands.size > 1000) {
            commands.removeAt(0)
        }
        
        val commandsJson = JSONArray()
        commands.forEach { cmd ->
            val cmdJson = JSONObject().apply {
                put("command", cmd.command)
                put("timestamp", cmd.timestamp)
                put("context", cmd.context)
                put("success", cmd.success)
                put("responseTime", cmd.responseTime)
                put("error", cmd.error)
            }
            commandsJson.put(cmdJson)
        }
        
        sharedPrefs.edit().putString("voice_commands", commandsJson.toString()).apply()
    }
    
    private fun getVoiceCommands(): List<VoiceCommand> {
        val commandsJson = sharedPrefs.getString("voice_commands", "[]")
        val commands = mutableListOf<VoiceCommand>()
        
        try {
            val jsonArray = JSONArray(commandsJson)
            for (i in 0 until jsonArray.length()) {
                val cmdJson = jsonArray.getJSONObject(i)
                val command = VoiceCommand(
                    command = cmdJson.getString("command"),
                    timestamp = cmdJson.getString("timestamp"),
                    context = cmdJson.getString("context"),
                    success = cmdJson.getBoolean("success"),
                    responseTime = cmdJson.getLong("responseTime"),
                    error = if (cmdJson.has("error")) cmdJson.getString("error") else null
                )
                commands.add(command)
            }
        } catch (e: Exception) {
            // Игнорируем ошибки парсинга
        }
        
        return commands
    }
    
    suspend fun generateUsageStats(): UsageStats {
        return withContext(Dispatchers.Default) {
            val commands = getVoiceCommands()
            
            val totalCommands = commands.size
            val successfulCommands = commands.count { it.success }
            val averageResponseTime = if (commands.isNotEmpty()) {
                commands.map { it.responseTime }.average().toLong()
            } else 0L
            
            val mostUsedCommands = commands
                .groupBy { it.command }
                .mapValues { it.value.size }
                .entries
                .sortedByDescending { it.value }
                .take(5)
                .map { it.key }
            
            val contextDistribution = commands
                .groupBy { it.context }
                .mapValues { it.value.size }
            
            val dailyUsage = commands
                .groupBy { 
                    LocalDateTime.parse(it.timestamp, DateTimeFormatter.ISO_LOCAL_DATE_TIME)
                        .format(DateTimeFormatter.ISO_LOCAL_DATE)
                }
                .mapValues { it.value.size }
            
            UsageStats(
                totalCommands = totalCommands,
                successfulCommands = successfulCommands,
                averageResponseTime = averageResponseTime,
                mostUsedCommands = mostUsedCommands,
                contextDistribution = contextDistribution,
                dailyUsage = dailyUsage
            )
        }
    }
    
    suspend fun sendWeeklyReport() {
        withContext(Dispatchers.IO) {
            try {
                val stats = generateUsageStats()
                val report = formatWeeklyReport(stats)
                telegramNotifier.sendNotification(report)
            } catch (e: Exception) {
                // Логируем ошибку, но не прерываем работу
            }
        }
    }
    
    private fun formatWeeklyReport(stats: UsageStats): String {
        val successRate = if (stats.totalCommands > 0) {
            (stats.successfulCommands * 100.0 / stats.totalCommands).toInt()
        } else 0
        
        val topCommands = stats.mostUsedCommands.take(3).joinToString(", ")
        
        val contextBreakdown = stats.contextDistribution.entries
            .sortedByDescending { it.value }
            .take(3)
            .joinToString(", ") { "${it.key}: ${it.value}" }
        
        return """
            📊 <b>Еженедельный отчет</b>
            
            🎤 Всего команд: ${stats.totalCommands}
            ✅ Успешных: ${stats.successfulCommands} ($successRate%)
            ⏱️ Среднее время ответа: ${stats.averageResponseTime}ms
            
            🔝 Популярные команды:
            $topCommands
            
            🎯 Контексты:
            $contextBreakdown
            
            📈 Продолжай использовать голосовой ассистент!
        """.trimIndent()
    }
    
    fun logError(error: String, context: String = "general") {
        logVoiceCommand(
            command = "ERROR",
            context = context,
            success = false,
            responseTime = 0,
            error = error
        )
    }
    
    fun logSuccess(command: String, context: String, responseTime: Long) {
        logVoiceCommand(
            command = command,
            context = context,
            success = true,
            responseTime = responseTime
        )
    }
    
    fun getDailyUsageCount(): Int {
        val today = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE)
        val commands = getVoiceCommands()
        
        return commands.count { 
            LocalDateTime.parse(it.timestamp, DateTimeFormatter.ISO_LOCAL_DATE_TIME)
                .format(DateTimeFormatter.ISO_LOCAL_DATE) == today
        }
    }
    
    fun shouldShowUsageReminder(): Boolean {
        val dailyUsage = getDailyUsageCount()
        val lastReminder = sharedPrefs.getString("last_reminder_date", "")
        val today = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE)
        
        return dailyUsage == 0 && lastReminder != today
    }
    
    fun markReminderShown() {
        val today = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE)
        sharedPrefs.edit().putString("last_reminder_date", today).apply()
    }
} 