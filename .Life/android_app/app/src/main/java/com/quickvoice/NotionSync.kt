package com.quickvoice

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
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val notionToken = "your_notion_token" // Из конфигурации
    private val mediaType = "application/json; charset=utf-8".toMediaType()
    
    // ID баз данных Notion
    private val databases = mapOf(
        "tasks" to "your_tasks_database_id",
        "reflections" to "your_reflections_database_id",
        "habits" to "your_habits_database_id",
        "ideas" to "your_ideas_database_id"
    )
    
    suspend fun syncData(data: Map<String, Any>): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                when (data["type"]) {
                    "task" -> createTask(data)
                    "reflection" -> createReflection(data)
                    "habit" -> createHabit(data)
                    "idea" -> createIdea(data)
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
                    put("name", "Voice")
                })
            })
            put("Created", JSONObject().apply {
                put("date", JSONObject().apply {
                    put("start", java.time.LocalDateTime.now().toString())
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
                    put("name", "Voice Reflection")
                })
            })
            put("Date", JSONObject().apply {
                put("date", JSONObject().apply {
                    put("start", java.time.LocalDate.now().toString())
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
            put("Date", JSONObject().apply {
                put("date", JSONObject().apply {
                    put("start", java.time.LocalDate.now().toString())
                })
            })
            put("Source", JSONObject().apply {
                put("select", JSONObject().apply {
                    put("name", "Voice")
                })
            })
        }
        
        return createNotionPage(databaseId, properties)
    }
    
    private suspend fun createIdea(data: Map<String, Any>): Boolean {
        val content = data["content"] as String
        val databaseId = databases["ideas"] ?: return false
        
        val properties = JSONObject().apply {
            put("Title", JSONObject().apply {
                put("title", JSONObject().apply {
                    put("content", content)
                })
            })
            put("Status", JSONObject().apply {
                put("select", JSONObject().apply {
                    put("name", "New")
                })
            })
            put("Source", JSONObject().apply {
                put("select", JSONObject().apply {
                    put("name", "Voice")
                })
            })
            put("Created", JSONObject().apply {
                put("date", JSONObject().apply {
                    put("start", java.time.LocalDateTime.now().toString())
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
    
    suspend fun getRecentItems(type: String, limit: Int = 5): List<Map<String, Any>> {
        return withContext(Dispatchers.IO) {
            try {
                val databaseId = databases[type] ?: return@withContext emptyList()
                
                val requestBody = JSONObject().apply {
                    put("filter", JSONObject().apply {
                        put("property", "Created")
                        put("date", JSONObject().apply {
                            put("past_week", JSONObject())
                        })
                    })
                    put("sorts", JSONObject().apply {
                        put("property", "Created")
                        put("direction", "descending")
                    })
                    put("page_size", limit)
                }.toString()
                
                val request = Request.Builder()
                    .url("https://api.notion.com/v1/databases/$databaseId/query")
                    .post(requestBody.toRequestBody(mediaType))
                    .addHeader("Authorization", "Bearer $notionToken")
                    .addHeader("Notion-Version", "2022-06-28")
                    .addHeader("Content-Type", "application/json")
                    .build()
                
                val response = client.newCall(request).execute()
                if (response.isSuccessful) {
                    parseNotionResponse(response.body?.string() ?: "")
                } else {
                    emptyList()
                }
            } catch (e: Exception) {
                emptyList()
            }
        }
    }
    
    private fun parseNotionResponse(response: String): List<Map<String, Any>> {
        return try {
            val jsonResponse = JSONObject(response)
            val results = jsonResponse.getJSONArray("results")
            val items = mutableListOf<Map<String, Any>>()
            
            for (i in 0 until results.length()) {
                val item = results.getJSONObject(i)
                val properties = item.getJSONObject("properties")
                
                val itemData = mutableMapOf<String, Any>()
                itemData["id"] = item.getString("id")
                
                // Извлекаем основные свойства
                if (properties.has("Name")) {
                    val nameProp = properties.getJSONObject("Name")
                    if (nameProp.has("title") && nameProp.getJSONArray("title").length() > 0) {
                        itemData["name"] = nameProp.getJSONArray("title")
                            .getJSONObject(0)
                            .getJSONObject("text")
                            .getString("content")
                    }
                }
                
                if (properties.has("Content")) {
                    val contentProp = properties.getJSONObject("Content")
                    if (contentProp.has("rich_text") && contentProp.getJSONArray("rich_text").length() > 0) {
                        itemData["content"] = contentProp.getJSONArray("rich_text")
                            .getJSONObject(0)
                            .getJSONObject("text")
                            .getString("content")
                    }
                }
                
                items.add(itemData)
            }
            
            items
        } catch (e: Exception) {
            emptyList()
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