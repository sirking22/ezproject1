#!/usr/bin/env python3
"""
Конфигурация окружения для всех интеграций
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class EnvironmentConfig:
    """Конфигурация всех интеграций"""
    
    def __init__(self):
        # Todoist
        self.TODOIST_API_TOKEN = "05e680098895c97a2e24b1eab2c9de3977672a69"
        
        # Telegram
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.ALLOWED_TELEGRAM_USERS = os.getenv("ALLOWED_TELEGRAM_USERS", "").split(",")
        
        # Notion
        self.NOTION_TOKEN = os.getenv("NOTION_TOKEN")
        self.NOTION_DATABASES = {
            "tasks": os.getenv("NOTION_TASKS_DB_ID"),
            "habits": os.getenv("NOTION_HABITS_DB_ID"),
            "reflections": os.getenv("NOTION_REFLECTIONS_DB_ID"),
            "rituals": os.getenv("NOTION_RITUALS_DB_ID"),
            "guides": os.getenv("NOTION_GUIDES_DB_ID"),
            "actions": os.getenv("NOTION_ACTIONS_DB_ID"),
            "terms": os.getenv("NOTION_TERMS_DB_ID"),
            "materials": os.getenv("NOTION_MATERIALS_DB_ID"),
        }
        
        # LLM
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        # Календарь (Google Calendar)
        self.GOOGLE_CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        self.GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
        
        # Настройки системы
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
    def validate(self) -> Dict[str, bool]:
        """Проверка конфигурации"""
        validation = {
            "todoist": bool(self.TODOIST_API_TOKEN),
            "telegram": bool(self.TELEGRAM_BOT_TOKEN),
            "notion": bool(self.NOTION_TOKEN),
            "llm": bool(self.OPENROUTER_API_KEY or self.OPENAI_API_KEY),
            "calendar": bool(self.GOOGLE_CALENDAR_CREDENTIALS),
        }
        return validation
    
    def get_missing_configs(self) -> list:
        """Получение отсутствующих конфигураций"""
        validation = self.validate()
        missing = []
        
        if not validation["telegram"]:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not validation["notion"]:
            missing.append("NOTION_TOKEN")
        if not validation["llm"]:
            missing.append("OPENROUTER_API_KEY или OPENAI_API_KEY")
        if not validation["calendar"]:
            missing.append("GOOGLE_CALENDAR_CREDENTIALS")
            
        return missing

# Глобальный экземпляр конфигурации
config = EnvironmentConfig() 