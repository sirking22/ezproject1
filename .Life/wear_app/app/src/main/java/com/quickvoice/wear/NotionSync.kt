package com.quickvoice.wear

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

class NotionSync {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .build()
    
    private val notionToken = "your_notion_token"
    private val mediaType = "application/json; charset=utf-8".toMediaType()
    
    private val databases = mapOf(
        "tasks" to "your_tasks_database_id",
        "reflections" to "your_reflections_database_id",
        "habits" to "your_habits_database_id"
    )
    
    suspend fun syncData(data: Map<String, Any>): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                when (data["type"]) {
                    "task" -> createTask(data)
                    "reflection" -> createReflection(data)
                    "habit" -> createHabit(data)
                    else -> false
                }
            } catch (e: Exception) {
                false
            }
        }
    }
    
    private suspend fun createTask(data: Map<String, Any>): Boolean {
        val content = data["content"] as String
        val databaseId = databases["tasks"] ?: return false
        
        val properties = JSONObject().apply {
            put("Name", JSONObject().apply {
                put("title", JSONObject().apply {
                    put("content", content)
                })
            })
            put("Status", JSONObject().apply {
                put("select", JSONObject().apply {
                    put("name", "To Do")
                })
            })
            put("Source", JSONObject().apply {
                put("select", JSONObject().apply {
                    put("name", "Wear")
                })
            })
        }
        
        return createNotionPage(databaseId, properties)
    }
    
    private suspend fun createReflection(data: Map<String, Any>): Boolean {
        val content = data["content"] as String
        val databaseId = databases["reflections"] ?: return false
        
        val properties = JSONObject().apply {
            put("Content", JSONObject().apply {
                put("rich_text", JSONObject().apply {
                    put("content", content)
                })
            })
            put("Type", JSONObject().apply {
                put("select", JSONObject().apply {
                    put("name", "Wear Reflection")
                })
            })
        }
        
        return createNotionPage(databaseId, properties)
    }
    
    private suspend fun createHabit(data: Map<String, Any>): Boolean {
        val content = data["content"] as String
        val databaseId = databases["habits"] ?: return false
        
        val properties = JSONObject().apply {
            put("Name", JSONObject().apply {
                put("title", JSONObject().apply {
                    put("content", content)
                })
            })
            put("Status", JSONObject().apply {
                put("select", JSONObject().apply {
                    put("name", "Completed")
                })
            })
            put("Source", JSONObject().apply {
                put("select", JSONObject().apply {
                    put("name", "Wear")
                })
            })
        }
        
        return createNotionPage(databaseId, properties)
    }
    
    private suspend fun createNotionPage(databaseId: String, properties: JSONObject): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val requestBody = JSONObject().apply {
                    put("parent", JSONObject().apply {
                        put("database_id", databaseId)
                    })
                    put("properties", properties)
                }.toString()
                
                val request = Request.Builder()
                    .url("https://api.notion.com/v1/pages")
                    .post(requestBody.toRequestBody(mediaType))
                    .addHeader("Authorization", "Bearer $notionToken")
                    .addHeader("Notion-Version", "2022-06-28")
                    .addHeader("Content-Type", "application/json")
                    .build()
                
                val response = client.newCall(request).execute()
                response.isSuccessful
            } catch (e: Exception) {
                false
            }
        }
    }
    
    suspend fun testConnection(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("https://api.notion.com/v1/users/me")
                    .get()
                    .addHeader("Authorization", "Bearer $notionToken")
                    .addHeader("Notion-Version", "2022-06-28")
                    .build()
                
                val response = client.newCall(request).execute()
                response.isSuccessful
            } catch (e: Exception) {
                false
            }
        }
    }
} 