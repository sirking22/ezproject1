package com.quickvoice

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Switch
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class SettingsActivity : AppCompatActivity() {
    
    private lateinit var llmServerUrl: EditText
    private lateinit var notionToken: EditText
    private lateinit var telegramToken: EditText
    private lateinit var autoSyncSwitch: Switch
    private lateinit var notificationsSwitch: Switch
    private lateinit var contextAwareSwitch: Switch
    private lateinit var saveButton: Button
    private lateinit var testButton: Button
    
    private val llmClient = LLMClient()
    private val notionSync = NotionSync()
    private val telegramNotifier = TelegramNotifier()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)
        
        initializeViews()
        loadSettings()
        setupListeners()
    }
    
    private fun initializeViews() {
        llmServerUrl = findViewById(R.id.llmServerUrl)
        notionToken = findViewById(R.id.notionToken)
        telegramToken = findViewById(R.id.telegramToken)
        autoSyncSwitch = findViewById(R.id.autoSyncSwitch)
        notificationsSwitch = findViewById(R.id.notificationsSwitch)
        contextAwareSwitch = findViewById(R.id.contextAwareSwitch)
        saveButton = findViewById(R.id.saveButton)
        testButton = findViewById(R.id.testButton)
    }
    
    private fun loadSettings() {
        val sharedPrefs = getSharedPreferences("QuickVoiceSettings", MODE_PRIVATE)
        
        llmServerUrl.setText(sharedPrefs.getString("llm_server_url", "http://192.168.1.100:8000"))
        notionToken.setText(sharedPrefs.getString("notion_token", ""))
        telegramToken.setText(sharedPrefs.getString("telegram_token", ""))
        autoSyncSwitch.isChecked = sharedPrefs.getBoolean("auto_sync", true)
        notificationsSwitch.isChecked = sharedPrefs.getBoolean("notifications", true)
        contextAwareSwitch.isChecked = sharedPrefs.getBoolean("context_aware", true)
    }
    
    private fun setupListeners() {
        saveButton.setOnClickListener {
            saveSettings()
        }
        
        testButton.setOnClickListener {
            testConnections()
        }
    }
    
    private fun saveSettings() {
        val sharedPrefs = getSharedPreferences("QuickVoiceSettings", MODE_PRIVATE)
        val editor = sharedPrefs.edit()
        
        editor.putString("llm_server_url", llmServerUrl.text.toString())
        editor.putString("notion_token", notionToken.text.toString())
        editor.putString("telegram_token", telegramToken.text.toString())
        editor.putBoolean("auto_sync", autoSyncSwitch.isChecked)
        editor.putBoolean("notifications", notificationsSwitch.isChecked)
        editor.putBoolean("context_aware", contextAwareSwitch.isChecked)
        
        editor.apply()
        
        Toast.makeText(this, "Настройки сохранены", Toast.LENGTH_SHORT).show()
    }
    
    private fun testConnections() {
        lifecycleScope.launch {
            try {
                // Тест LLM сервера
                val llmConnected = llmClient.testConnection()
                val llmStatus = if (llmConnected) "✅ Подключен" else "❌ Ошибка"
                
                // Тест Notion
                val notionConnected = notionSync.testConnection()
                val notionStatus = if (notionConnected) "✅ Подключен" else "❌ Ошибка"
                
                // Тест Telegram
                val telegramConnected = telegramNotifier.testConnection()
                val telegramStatus = if (telegramConnected) "✅ Подключен" else "❌ Ошибка"
                
                val message = """
                    Результаты тестирования:
                    
                    LLM Сервер: $llmStatus
                    Notion API: $notionStatus
                    Telegram Bot: $telegramStatus
                """.trimIndent()
                
                Toast.makeText(this@SettingsActivity, message, Toast.LENGTH_LONG).show()
                
            } catch (e: Exception) {
                Toast.makeText(this@SettingsActivity, "Ошибка тестирования: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
} 