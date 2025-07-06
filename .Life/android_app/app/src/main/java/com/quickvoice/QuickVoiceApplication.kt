package com.quickvoice

import android.app.Application
import android.app.NotificationManager
import android.content.Context
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit

class QuickVoiceApplication : Application() {
    
    private val applicationScope = CoroutineScope(Dispatchers.IO)
    
    lateinit var analyticsManager: AnalyticsManager
    lateinit var notificationManager: NotificationManager
    lateinit var contextManager: ContextManager
    
    override fun onCreate() {
        super.onCreate()
        
        // Инициализация компонентов
        analyticsManager = AnalyticsManager(this)
        notificationManager = NotificationManager(this)
        contextManager = ContextManager()
        
        // Запуск фоновых задач
        startBackgroundTasks()
    }
    
    private fun startBackgroundTasks() {
        applicationScope.launch {
            // Проверка напоминаний каждые 30 минут
            while (true) {
                try {
                    notificationManager.checkAndShowReminders()
                } catch (e: Exception) {
                    analyticsManager.logError("Background task error: ${e.message}")
                }
                
                kotlinx.coroutines.delay(TimeUnit.MINUTES.toMillis(30))
            }
        }
        
        applicationScope.launch {
            // Еженедельный отчет по воскресеньям
            while (true) {
                try {
                    val now = java.time.LocalDateTime.now()
                    if (now.dayOfWeek.value == 7 && now.hour == 10) { // Воскресенье, 10:00
                        notificationManager.showWeeklyReport()
                    }
                } catch (e: Exception) {
                    analyticsManager.logError("Weekly report error: ${e.message}")
                }
                
                kotlinx.coroutines.delay(TimeUnit.HOURS.toMillis(1))
            }
        }
    }
    
    companion object {
        fun getInstance(context: Context): QuickVoiceApplication {
            return context.applicationContext as QuickVoiceApplication
        }
    }
} 