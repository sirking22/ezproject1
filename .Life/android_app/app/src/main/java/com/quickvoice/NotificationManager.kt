package com.quickvoice

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.LocalDateTime
import java.time.LocalTime

class NotificationManager(private val context: Context) {
    
    private val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    private val analyticsManager = AnalyticsManager(context)
    private val contextManager = ContextManager()
    
    companion object {
        const val CHANNEL_ID_REMINDERS = "voice_reminders"
        const val CHANNEL_ID_UPDATES = "voice_updates"
        const val NOTIFICATION_ID_REMINDER = 100
        const val NOTIFICATION_ID_UPDATE = 101
    }
    
    init {
        createNotificationChannels()
    }
    
    private fun createNotificationChannels() {
        val reminderChannel = NotificationChannel(
            CHANNEL_ID_REMINDERS,
            "Напоминания",
            NotificationManager.IMPORTANCE_DEFAULT
        ).apply {
            description = "Напоминания о голосовых командах"
        }
        
        val updateChannel = NotificationChannel(
            CHANNEL_ID_UPDATES,
            "Обновления",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Обновления и статистика"
        }
        
        notificationManager.createNotificationChannel(reminderChannel)
        notificationManager.createNotificationChannel(updateChannel)
    }
    
    suspend fun showSmartReminder() {
        withContext(Dispatchers.IO) {
            val currentContext = contextManager.getCurrentContext()
            val dailyUsage = analyticsManager.getDailyUsageCount()
            
            val (title, message) = when {
                dailyUsage == 0 -> {
                    when (currentContext) {
                        "morning" -> "🌅 Доброе утро!" to "Запланируй день голосовой командой"
                        "work" -> "💼 Рабочее время" to "Добавь задачи голосом"
                        "evening" -> "🌙 Вечер" to "Запиши мысли о дне"
                        else -> "🎤 Голосовой ассистент" to "Попробуй голосовую команду"
                    }
                }
                
                dailyUsage < 3 -> {
                    "📈 Прогресс" to "Ты использовал ассистента $dailyUsage раз сегодня"
                }
                
                else -> {
                    "🎯 Отличная работа!" to "Ты активно используешь голосовой ассистент"
                }
            }
            
            showNotification(
                channelId = CHANNEL_ID_REMINDERS,
                notificationId = NOTIFICATION_ID_REMINDER,
                title = title,
                message = message,
                autoCancel = true
            )
        }
    }
    
    suspend fun showContextualReminder() {
        withContext(Dispatchers.IO) {
            val currentContext = contextManager.getCurrentContext()
            val time = LocalTime.now()
            
            val (title, message) = when (currentContext) {
                "morning" -> {
                    if (time.isBefore(LocalTime.of(9, 0))) {
                        "🌅 Утренний ритуал" to "Создай план дня голосовой командой"
                    } else {
                        "💼 Начинаем работу" to "Добавь первые задачи дня"
                    }
                }
                
                "work" -> {
                    if (time.isBefore(LocalTime.of(12, 0))) {
                        "📋 Утренние задачи" to "Запланируй важные дела"
                    } else if (time.isBefore(LocalTime.of(15, 0))) {
                        "🍽️ Обеденный перерыв" to "Запиши идеи за обедом"
                    } else {
                        "📊 Вечерний обзор" to "Проверь прогресс по задачам"
                    }
                }
                
                "evening" -> {
                    if (time.isBefore(LocalTime.of(20, 0))) {
                        "🌙 Вечерняя рефлексия" to "Проанализируй прошедший день"
                    } else {
                        "😴 Подготовка ко сну" to "Запиши мысли перед сном"
                    }
                }
                
                else -> {
                    "🎤 Голосовой ассистент" to "Попробуй новую команду"
                }
            }
            
            showNotification(
                channelId = CHANNEL_ID_REMINDERS,
                notificationId = NOTIFICATION_ID_REMINDER + 1,
                title = title,
                message = message,
                autoCancel = true
            )
        }
    }
    
    suspend fun showUsageUpdate() {
        withContext(Dispatchers.IO) {
            val dailyUsage = analyticsManager.getDailyUsageCount()
            val stats = analyticsManager.generateUsageStats()
            
            val message = when {
                dailyUsage == 0 -> "Ты еще не использовал ассистента сегодня"
                dailyUsage == 1 -> "Отличное начало! Одна команда сегодня"
                dailyUsage < 5 -> "Хорошо! $dailyUsage команд сегодня"
                else -> "Отлично! $dailyUsage команд сегодня"
            }
            
            showNotification(
                channelId = CHANNEL_ID_UPDATES,
                notificationId = NOTIFICATION_ID_UPDATE,
                title = "📊 Статистика использования",
                message = message,
                autoCancel = true
            )
        }
    }
    
    suspend fun showAchievementNotification(achievement: String) {
        withContext(Dispatchers.IO) {
            showNotification(
                channelId = CHANNEL_ID_UPDATES,
                notificationId = NOTIFICATION_ID_UPDATE + 1,
                title = "🏆 Достижение!",
                message = achievement,
                autoCancel = true
            )
        }
    }
    
    private fun showNotification(
        channelId: String,
        notificationId: Int,
        title: String,
        message: String,
        autoCancel: Boolean = true
    ) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        
        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notification = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(autoCancel)
            .setContentIntent(pendingIntent)
            .build()
        
        notificationManager.notify(notificationId, notification)
    }
    
    fun cancelNotification(notificationId: Int) {
        notificationManager.cancel(notificationId)
    }
    
    fun cancelAllNotifications() {
        notificationManager.cancelAll()
    }
    
    suspend fun checkAndShowReminders() {
        withContext(Dispatchers.IO) {
            // Проверяем, нужно ли показать напоминание
            if (analyticsManager.shouldShowUsageReminder()) {
                showSmartReminder()
                analyticsManager.markReminderShown()
            }
            
            // Показываем контекстные напоминания в определенное время
            val time = LocalTime.now()
            when {
                time.hour == 9 && time.minute == 0 -> showContextualReminder()
                time.hour == 12 && time.minute == 0 -> showContextualReminder()
                time.hour == 18 && time.minute == 0 -> showContextualReminder()
                time.hour == 21 && time.minute == 0 -> showContextualReminder()
            }
        }
    }
    
    suspend fun showWeeklyReport() {
        withContext(Dispatchers.IO) {
            val stats = analyticsManager.generateUsageStats()
            
            if (stats.totalCommands > 0) {
                showNotification(
                    channelId = CHANNEL_ID_UPDATES,
                    notificationId = NOTIFICATION_ID_UPDATE + 2,
                    title = "📊 Еженедельный отчет готов",
                    message = "Нажми, чтобы посмотреть статистику",
                    autoCancel = true
                )
            }
        }
    }
} 