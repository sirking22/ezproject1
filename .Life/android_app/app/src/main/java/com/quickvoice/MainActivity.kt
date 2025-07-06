package com.quickvoice

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import java.util.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var voiceButton: Button
    private lateinit var statusText: TextView
    private lateinit var commandText: TextView
    private lateinit var resultText: TextView
    
    private var speechRecognizer: SpeechRecognizer? = null
    private var isListening = false
    
    private val llmClient = LLMClient()
    private val notionSync = NotionSync()
    private val telegramNotifier = TelegramNotifier()
    private val contextManager = ContextManager()
    
    companion object {
        private const val PERMISSION_REQUEST_CODE = 123
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initializeViews()
        setupVoiceRecognition()
        checkPermissions()
        updateStatus("Готов к работе")
    }
    
    private fun initializeViews() {
        voiceButton = findViewById(R.id.voiceButton)
        statusText = findViewById(R.id.statusText)
        commandText = findViewById(R.id.commandText)
        resultText = findViewById(R.id.resultText)
        
        voiceButton.setOnClickListener {
            if (isListening) {
                stopListening()
            } else {
                startListening()
            }
        }
    }
    
    private fun setupVoiceRecognition() {
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
        speechRecognizer?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                updateStatus("Слушаю...")
                isListening = true
                voiceButton.text = "🛑 Остановить"
            }
            
            override fun onBeginningOfSpeech() {
                updateStatus("Говорите...")
            }
            
            override fun onRmsChanged(rmsdB: Float) {
                // Анимация уровня звука
            }
            
            override fun onBufferReceived(buffer: ByteArray?) {}
            
            override fun onEndOfSpeech() {
                updateStatus("Обрабатываю...")
            }
            
            override fun onError(error: Int) {
                when (error) {
                    SpeechRecognizer.ERROR_NO_MATCH -> {
                        updateStatus("Не удалось распознать речь")
                        Toast.makeText(this@MainActivity, "Попробуйте еще раз", Toast.LENGTH_SHORT).show()
                    }
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> {
                        updateStatus("Время ожидания истекло")
                    }
                    else -> {
                        updateStatus("Ошибка распознавания")
                    }
                }
                stopListening()
            }
            
            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!matches.isNullOrEmpty()) {
                    val command = matches[0]
                    processCommand(command)
                }
                stopListening()
            }
            
            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
    }
    
    private fun startListening() {
        if (checkPermissions()) {
            val intent = RecognizerIntent.getVoiceDetailsIntent(this)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ru-RU")
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            
            speechRecognizer?.startListening(intent)
        }
    }
    
    private fun stopListening() {
        speechRecognizer?.stopListening()
        isListening = false
        voiceButton.text = "🎤 Начать запись"
        updateStatus("Готов к работе")
    }
    
    private fun processCommand(command: String) {
        commandText.text = "Команда: $command"
        updateStatus("Обрабатываю команду...")
        
        lifecycleScope.launch {
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
                
                // Показываем результат
                resultText.text = result.message
                updateStatus("Готово")
                
                Toast.makeText(this@MainActivity, "Команда выполнена", Toast.LENGTH_SHORT).show()
                
            } catch (e: Exception) {
                updateStatus("Ошибка: ${e.message}")
                resultText.text = "Произошла ошибка при обработке команды"
                Toast.makeText(this@MainActivity, "Ошибка обработки", Toast.LENGTH_SHORT).show()
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
                        "source" to "voice"
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
                        "source" to "voice"
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
                        "source" to "voice"
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
    
    private fun updateStatus(status: String) {
        statusText.text = "Статус: $status"
    }
    
    private fun checkPermissions(): Boolean {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.RECORD_AUDIO),
                PERMISSION_REQUEST_CODE
            )
            return false
        }
        return true
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Разрешение на микрофон получено", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Необходимо разрешение на микрофон", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer?.destroy()
    }
}

data class CommandResult(
    val message: String,
    val shouldSync: Boolean,
    val shouldNotify: Boolean,
    val data: Map<String, Any>
) 