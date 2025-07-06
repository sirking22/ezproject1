package com.quickvoice.wear

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import java.util.*

class MainActivity : ComponentActivity() {
    
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
        
        setupSpeechRecognizer()
        checkPermissions()
        
        setContent {
            WearVoiceAssistantApp(
                isListening = isListening,
                onVoiceButtonClick = {
                    if (isListening) {
                        stopListening()
                    } else {
                        startListening()
                    }
                },
                onSettingsClick = {
                    // Открыть настройки
                }
            )
        }
    }
    
    private fun setupSpeechRecognizer() {
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
        speechRecognizer?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                isListening = true
            }
            
            override fun onBeginningOfSpeech() {
                // Анимация записи
            }
            
            override fun onRmsChanged(rmsdB: Float) {
                // Уровень звука
            }
            
            override fun onBufferReceived(buffer: ByteArray?) {}
            
            override fun onEndOfSpeech() {
                // Обработка
            }
            
            override fun onError(error: Int) {
                isListening = false
            }
            
            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!matches.isNullOrEmpty()) {
                    val command = matches[0]
                    processCommand(command)
                }
                isListening = false
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
    }
    
    private fun processCommand(command: String) {
        lifecycleScope.launch {
            try {
                val context = contextManager.getCurrentContext()
                val llmResponse = llmClient.processCommand(command, context)
                val result = processLLMResponse(llmResponse, command)
                
                if (result.shouldSync) {
                    notionSync.syncData(result.data)
                }
                
                if (result.shouldNotify) {
                    telegramNotifier.sendNotification(result.message)
                }
                
            } catch (e: Exception) {
                // Обработка ошибок
            }
        }
    }
    
    private fun processLLMResponse(llmResponse: String, originalCommand: String): CommandResult {
        return when {
            originalCommand.contains("задача", ignoreCase = true) -> {
                CommandResult(
                    message = "✅ Задача добавлена",
                    shouldSync = true,
                    shouldNotify = true,
                    data = mapOf(
                        "type" to "task",
                        "content" to llmResponse,
                        "source" to "wear"
                    )
                )
            }
            
            originalCommand.contains("мысль", ignoreCase = true) -> {
                CommandResult(
                    message = "💭 Мысль записана",
                    shouldSync = true,
                    shouldNotify = false,
                    data = mapOf(
                        "type" to "reflection",
                        "content" to llmResponse,
                        "source" to "wear"
                    )
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
    
    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer?.destroy()
    }
}

@Composable
fun WearVoiceAssistantApp(
    isListening: Boolean,
    onVoiceButtonClick: () -> Unit,
    onSettingsClick: () -> Unit
) {
    MaterialTheme {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Заголовок
            Text(
                text = "🎤 Voice",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Основная кнопка записи
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(CircleShape)
                    .background(
                        if (isListening) Color.Red else MaterialTheme.colorScheme.primary
                    )
                    .clickable { onVoiceButtonClick() },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Mic,
                    contentDescription = "Voice",
                    tint = Color.White,
                    modifier = Modifier.size(32.dp)
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Статус
            Text(
                text = if (isListening) "Слушаю..." else "Нажми для записи",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Быстрые команды
            Text(
                text = "Быстрые команды:",
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            Text(
                text = "• \"Добавить задачу\"",
                fontSize = 8.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Text(
                text = "• \"Записать мысль\"",
                fontSize = 8.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Кнопка настроек
            IconButton(
                onClick = onSettingsClick,
                modifier = Modifier.size(32.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = "Settings",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(16.dp)
                )
            }
        }
    }
}

data class CommandResult(
    val message: String,
    val shouldSync: Boolean,
    val shouldNotify: Boolean,
    val data: Map<String, Any>
) 