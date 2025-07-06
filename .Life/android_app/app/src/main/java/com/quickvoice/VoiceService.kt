package com.quickvoice

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Binder
import android.os.IBinder
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.util.*

class VoiceService : Service() {
    
    private val binder = VoiceServiceBinder()
    private var speechRecognizer: SpeechRecognizer? = null
    private var isListening = false
    
    private val llmClient = LLMClient()
    private val notionSync = NotionSync()
    private val telegramNotifier = TelegramNotifier()
    private val contextManager = ContextManager()
    
    private val serviceScope = CoroutineScope(Dispatchers.IO)
    
    companion object {
        private const val NOTIFICATION_ID = 1
        private const val CHANNEL_ID = "voice_service_channel"
    }
    
    inner class VoiceServiceBinder : Binder() {
        fun getService(): VoiceService = this@VoiceService
    }
    
    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        setupSpeechRecognizer()
    }
    
    override fun onBind(intent: Intent): IBinder {
        return binder
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification("Голосовой ассистент активен"))
        return START_STICKY
    }
    
    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Голосовой сервис",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Фоновый сервис для обработки голосовых команд"
        }
        
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.createNotificationChannel(channel)
    }
    
    private fun createNotification(content: String): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("🎤 Quick Voice Assistant")
            .setContentText(content)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
    
    private fun setupSpeechRecognizer() {
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
        speechRecognizer?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                isListening = true
                updateNotification("Слушаю...")
            }
            
            override fun onBeginningOfSpeech() {
                updateNotification("Говорите...")
            }
            
            override fun onRmsChanged(rmsdB: Float) {
                // Анимация уровня звука
            }
            
            override fun onBufferReceived(buffer: ByteArray?) {}
            
            override fun onEndOfSpeech() {
                updateNotification("Обрабатываю...")
            }
            
            override fun onError(error: Int) {
                isListening = false
                updateNotification("Готов к работе")
            }
            
            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!matches.isNullOrEmpty()) {
                    val command = matches[0]
                    processCommand(command)
                }
                isListening = false
                updateNotification("Готов к работе")
            }
            
            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
    }
    
    fun startListening() {
        if (!isListening) {
            val intent = RecognizerIntent.getVoiceDetailsIntent(this)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ru-RU")
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            
            speechRecognizer?.startListening(intent)
        }
    }
    
    fun stopListening() {
        speechRecognizer?.stopListening()
        isListening = false
        updateNotification("Готов к работе")
    }
    
    private fun processCommand(command: String) {
        serviceScope.launch {
            try {
                // Получаем контекст
                val context = contextManager.getCurrentContext()
                
                // Отправляем в LLM
                val llmResponse = llmClient.processCommand(command, context)
                
                // Обрабатываем результат
                val result = processLLMResponse(llmResponse, command)
                
                // Синхронизируем с Notion
                if (result.shouldSync) {
                    notionSync.syncData(result.data)
                }
                
                // Отправляем уведомление в Telegram
                if (result.shouldNotify) {
                    telegramNotifier.sendNotification(result.message)
                }
                
                // Логируем команду
                telegramNotifier.sendVoiceCommandLog(command, result.message)
                
            } catch (e: Exception) {
                telegramNotifier.sendErrorNotification("Ошибка обработки: ${e.message}")
            }
        }
    }
    
    private fun processLLMResponse(llmResponse: String, originalCommand: String): CommandResult {
        return when {
            originalCommand.contains("задача", ignoreCase = true) || 
            originalCommand.contains("todo", ignoreCase = true) -> {
                CommandResult(
                    message = "✅ Задача добавлена: $llmResponse",
                    shouldSync = true,
                    shouldNotify = true,
                    data = mapOf(
                        "type" to "task",
                        "content" to llmResponse,
                        "source" to "voice_service"
                    )
                )
            }
            
            originalCommand.contains("мысль", ignoreCase = true) || 
            originalCommand.contains("рефлексия", ignoreCase = true) -> {
                CommandResult(
                    message = "💭 Мысль записана: $llmResponse",
                    shouldSync = true,
                    shouldNotify = false,
                    data = mapOf(
                        "type" to "reflection",
                        "content" to llmResponse,
                        "source" to "voice_service"
                    )
                )
            }
            
            originalCommand.contains("привычка", ignoreCase = true) -> {
                CommandResult(
                    message = "🔄 Привычка отмечена: $llmResponse",
                    shouldSync = true,
                    shouldNotify = true,
                    data = mapOf(
                        "type" to "habit",
                        "content" to llmResponse,
                        "source" to "voice_service"
                    )
                )
            }
            
            originalCommand.contains("прогресс", ignoreCase = true) || 
            originalCommand.contains("статистика", ignoreCase = true) -> {
                CommandResult(
                    message = "📊 $llmResponse",
                    shouldSync = false,
                    shouldNotify = false,
                    data = emptyMap()
                )
            }
            
            else -> {
                CommandResult(
                    message = llmResponse,
                    shouldSync = false,
                    shouldNotify = false,
                    data = emptyMap()
                )
            }
        }
    }
    
    private fun updateNotification(content: String) {
        val notification = createNotification(content)
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, notification)
    }
    
    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer?.destroy()
    }
} 