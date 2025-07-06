package com.quickvoice.wear

import java.time.LocalDateTime
import java.time.LocalTime

class ContextManager {
    
    fun getCurrentContext(): String {
        val now = LocalDateTime.now()
        val time = now.toLocalTime()
        
        return when {
            isMorningTime(time) -> "morning"
            isWorkTime(time) -> "work"
            isEveningTime(time) -> "evening"
            isNightTime(time) -> "night"
            else -> "wear"
        }
    }
    
    private fun isMorningTime(time: LocalTime): Boolean {
        return time.isAfter(LocalTime.of(5, 0)) && 
               time.isBefore(LocalTime.of(11, 0))
    }
    
    private fun isWorkTime(time: LocalTime): Boolean {
        return time.isAfter(LocalTime.of(9, 0)) && 
               time.isBefore(LocalTime.of(18, 0))
    }
    
    private fun isEveningTime(time: LocalTime): Boolean {
        return time.isAfter(LocalTime.of(18, 0)) && 
               time.isBefore(LocalTime.of(22, 0))
    }
    
    private fun isNightTime(time: LocalTime): Boolean {
        return time.isAfter(LocalTime.of(22, 0)) || 
               time.isBefore(LocalTime.of(5, 0))
    }
    
    fun getWearPrompt(command: String): String {
        val context = getCurrentContext()
        
        return when (context) {
            "morning" -> "Утро. $command"
            "work" -> "Работа. $command"
            "evening" -> "Вечер. $command"
            "night" -> "Ночь. $command"
            else -> command
        }
    }
} 