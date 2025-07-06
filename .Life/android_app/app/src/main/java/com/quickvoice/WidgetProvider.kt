package com.quickvoice

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import androidx.core.app.NotificationCompat

class WidgetProvider : AppWidgetProvider() {
    
    companion object {
        const val ACTION_VOICE_COMMAND = "com.quickvoice.VOICE_COMMAND"
    }
    
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }
    
    private fun updateWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ) {
        val views = RemoteViews(context.packageName, R.layout.widget_voice_assistant)
        
        // Настройка кнопки записи
        val voiceIntent = Intent(context, WidgetProvider::class.java).apply {
            action = ACTION_VOICE_COMMAND
        }
        val voicePendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            voiceIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        views.setOnClickPendingIntent(R.id.widgetVoiceButton, voicePendingIntent)
        
        // Настройка кнопки настроек
        val settingsIntent = Intent(context, SettingsActivity::class.java)
        val settingsPendingIntent = PendingIntent.getActivity(
            context,
            1,
            settingsIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        views.setOnClickPendingIntent(R.id.widgetSettingsButton, settingsPendingIntent)
        
        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
    
    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        
        if (intent.action == ACTION_VOICE_COMMAND) {
            // Запускаем голосовой сервис
            val serviceIntent = Intent(context, VoiceService::class.java)
            context.startService(serviceIntent)
            
            // Отправляем команду на запись
            val voiceService = VoiceService()
            voiceService.startListening()
        }
    }
    
    fun updateWidgetStatus(context: Context, status: String) {
        val appWidgetManager = AppWidgetManager.getInstance(context)
        val appWidgetIds = appWidgetManager.getAppWidgetIds(
            ComponentName(context, WidgetProvider::class.java)
        )
        
        for (appWidgetId in appWidgetIds) {
            val views = RemoteViews(context.packageName, R.layout.widget_voice_assistant)
            views.setTextViewText(R.id.widgetStatusText, status)
            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
} 