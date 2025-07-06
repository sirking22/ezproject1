#!/usr/bin/env python3
"""
FastAPI сервер для Quick Voice Assistant
Обработка голосовых команд и интеграция с LLM
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from config import (
    SERVER_CONFIG, LLM_CONFIG, NOTION_CONFIG, TELEGRAM_CONFIG,
    VOICE_COMMANDS, DEFAULT_RESPONSES, validate_config
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, SERVER_CONFIG.get("log_level", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Quick Voice Assistant API",
    description="API для обработки голосовых команд с интеграцией LLM",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class VoiceRequest(BaseModel):
    query: str = Field(..., description="Текст голосовой команды")
    context: str = Field(default="watch_voice", description="Контекст запроса")
    timestamp: Optional[int] = Field(default=None, description="Временная метка")
    user_id: Optional[str] = Field(default="user123", description="ID пользователя")

class VoiceResponse(BaseModel):
    response: str = Field(..., description="Ответ на команду")
    action: Optional[str] = Field(default=None, description="Выполненное действие")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Дополнительные данные")
    timestamp: int = Field(..., description="Временная метка ответа")

class TelegramMessage(BaseModel):
    message: str = Field(..., description="Текст сообщения")
    source: str = Field(default="watch_voice", description="Источник сообщения")

# Глобальные переменные
llm_model = None
notion_client = None
telegram_bot = None

class LLMProcessor:
    """Обработчик LLM запросов"""
    
    def __init__(self):
        self.model = None
        self.use_local = LLM_CONFIG["use_local"]
        self.fallback_to_openai = LLM_CONFIG["fallback_to_openai"]
        
    async def initialize(self):
        """Инициализация LLM модели"""
        if self.use_local and LLM_CONFIG["model_path"]:
            try:
                # Инициализация локальной модели
                logger.info("Загрузка локальной LLM модели...")
                # Здесь будет код загрузки локальной модели
                self.model = "local_model"
                logger.info("Локальная LLM модель загружена")
            except Exception as e:
                logger.error(f"Ошибка загрузки локальной модели: {e}")
                self.model = None
        
    async def process_query(self, query: str, context: str = "watch_voice") -> str:
        """Обработка запроса через LLM"""
        try:
            if self.model:
                # Использование локальной модели
                return await self._process_local(query, context)
            elif self.fallback_to_openai:
                # Fallback к OpenAI
                return await self._process_openai(query, context)
            else:
                # Простая обработка без LLM
                return await self._process_simple(query, context)
        except Exception as e:
            logger.error(f"Ошибка обработки LLM запроса: {e}")
            return "Извините, произошла ошибка при обработке запроса."
    
    async def _process_local(self, query: str, context: str) -> str:
        """Обработка через локальную модель"""
        # Здесь будет код для локальной Llama 70B
        logger.info(f"Обработка через локальную модель: {query}")
        return f"Локальная модель обработала: {query}"
    
    async def _process_openai(self, query: str, context: str) -> str:
        """Обработка через OpenAI"""
        # Здесь будет код для OpenAI API
        logger.info(f"Обработка через OpenAI: {query}")
        return f"OpenAI обработал: {query}"
    
    async def _process_simple(self, query: str, context: str) -> str:
        """Простая обработка без LLM"""
        query_lower = query.lower()
        
        # Поиск подходящей команды
        for command_type, command_info in VOICE_COMMANDS.items():
            for pattern in command_info["patterns"]:
                if pattern in query_lower:
                    # Извлечение данных из запроса
                    data = self._extract_data(query, pattern, command_type)
                    
                    # Получение ответа
                    response_template = DEFAULT_RESPONSES.get(command_type, DEFAULT_RESPONSES["unknown"])
                    response = response_template.format(**data)
                    
                    logger.info(f"Простая обработка: {query} -> {command_type}")
                    return response
        
        return DEFAULT_RESPONSES["unknown"]

    def _extract_data(self, query: str, pattern: str, command_type: str) -> Dict[str, str]:
        """Извлечение данных из запроса"""
        data = {}
        
        if command_type == "add_task":
            task = query.replace(pattern, "").strip()
            data["task"] = task
        elif command_type == "save_thought":
            thought = query.replace(pattern, "").strip()
            data["thought"] = thought
        elif command_type == "create_habit":
            habit = query.replace(pattern, "").strip()
            data["habit"] = habit
        elif command_type == "show_progress":
            data["progress"] = "85% шагов, 90% калорий, 7/10 привычек"
        elif command_type == "health_check":
            data["details"] = "Пульс 75 уд/мин, стресс 30%"
        
        return data

class NotionIntegration:
    """Интеграция с Notion"""
    
    def __init__(self):
        self.token = NOTION_CONFIG["token"]
        self.databases = NOTION_CONFIG["databases"]
        self.enabled = NOTION_CONFIG["enabled"]
        
    async def initialize(self):
        """Инициализация клиента Notion"""
        if not self.enabled or not self.token:
            logger.warning("Интеграция с Notion отключена")
            return
        
        try:
            # Здесь будет инициализация Notion клиента
            logger.info("Notion клиент инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Notion: {e}")
    
    async def create_task(self, task_text: str) -> bool:
        """Создание задачи в Notion"""
        if not self.enabled:
            return False
        
        try:
            logger.info(f"Создание задачи в Notion: {task_text}")
            # Здесь будет код создания задачи
            return True
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            return False
    
    async def save_reflection(self, reflection_text: str) -> bool:
        """Сохранение рефлексии в Notion"""
        if not self.enabled:
            return False
        
        try:
            logger.info(f"Сохранение рефлексии в Notion: {reflection_text}")
            # Здесь будет код сохранения рефлексии
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения рефлексии: {e}")
            return False
    
    async def create_habit(self, habit_text: str) -> bool:
        """Создание привычки в Notion"""
        if not self.enabled:
            return False
        
        try:
            logger.info(f"Создание привычки в Notion: {habit_text}")
            # Здесь будет код создания привычки
            return True
        except Exception as e:
            logger.error(f"Ошибка создания привычки: {e}")
            return False

class TelegramIntegration:
    """Интеграция с Telegram"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_CONFIG["bot_token"]
        self.chat_id = TELEGRAM_CONFIG["chat_id"]
        self.enabled = TELEGRAM_CONFIG["enabled"]
        
    async def initialize(self):
        """Инициализация Telegram бота"""
        if not self.enabled or not self.bot_token:
            logger.warning("Интеграция с Telegram отключена")
            return
        
        try:
            # Здесь будет инициализация Telegram бота
            logger.info("Telegram бот инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Telegram: {e}")
    
    async def send_message(self, message: str, source: str = "watch_voice") -> bool:
        """Отправка сообщения в Telegram"""
        if not self.enabled:
            return False
        
        try:
            formatted_message = f"🎤 {source.upper()}\n\n{message}"
            logger.info(f"Отправка в Telegram: {formatted_message[:100]}...")
            # Здесь будет код отправки сообщения
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки в Telegram: {e}")
            return False

# Инициализация компонентов
llm_processor = LLMProcessor()
notion_integration = NotionIntegration()
telegram_integration = TelegramIntegration()

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    logger.info("🚀 Запуск Quick Voice Assistant API...")
    
    # Проверка конфигурации
    if not validate_config():
        logger.error("❌ Ошибка конфигурации")
        return
    
    # Инициализация компонентов
    await llm_processor.initialize()
    await notion_integration.initialize()
    await telegram_integration.initialize()
    
    logger.info("✅ Quick Voice Assistant API запущен")

@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    logger.info("🛑 Остановка Quick Voice Assistant API...")

# Эндпоинты API

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Quick Voice Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/ping")
async def ping():
    """Проверка доступности сервера"""
    return {
        "status": "ok",
        "timestamp": int(time.time()),
        "message": "pong"
    }

@app.get("/health")
async def health():
    """Статус здоровья сервера"""
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "components": {
            "llm": llm_processor.model is not None,
            "notion": notion_integration.enabled,
            "telegram": telegram_integration.enabled
        }
    }

@app.post("/watch/voice", response_model=VoiceResponse)
async def process_voice_command(request: VoiceRequest, background_tasks: BackgroundTasks):
    """Обработка голосовой команды от часов"""
    try:
        logger.info(f"🎤 Получена голосовая команда: {request.query}")
        
        # Обработка через LLM
        response_text = await llm_processor.process_query(
            request.query, 
            request.context
        )
        
        # Определение действия
        action = None
        data = {}
        
        query_lower = request.query.lower()
        for command_type, command_info in VOICE_COMMANDS.items():
            for pattern in command_info["patterns"]:
                if pattern in query_lower:
                    action = command_info["action"]
                    
                    # Выполнение действия в фоне
                    if action == "create_task":
                        task_text = request.query.replace(pattern, "").strip()
                        background_tasks.add_task(notion_integration.create_task, task_text)
                        data["task"] = task_text
                    elif action == "save_reflection":
                        reflection_text = request.query.replace(pattern, "").strip()
                        background_tasks.add_task(notion_integration.save_reflection, reflection_text)
                        data["reflection"] = reflection_text
                    elif action == "create_habit":
                        habit_text = request.query.replace(pattern, "").strip()
                        background_tasks.add_task(notion_integration.create_habit, habit_text)
                        data["habit"] = habit_text
                    
                    break
            if action:
                break
        
        # Отправка в Telegram
        background_tasks.add_task(
            telegram_integration.send_message,
            f"Запрос: {request.query}\nОтвет: {response_text}",
            "watch_voice"
        )
        
        return VoiceResponse(
            response=response_text,
            action=action,
            data=data,
            timestamp=int(time.time())
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки голосовой команды: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/telegram/send")
async def send_telegram_message(message: TelegramMessage):
    """Отправка сообщения в Telegram"""
    try:
        success = await telegram_integration.send_message(
            message.message, 
            message.source
        )
        
        return {
            "status": "sent" if success else "failed",
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в Telegram: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Метрики производительности"""
    return {
        "uptime": int(time.time()),
        "requests_processed": 0,  # Здесь будет счетчик запросов
        "llm_requests": 0,        # Здесь будет счетчик LLM запросов
        "notion_operations": 0,   # Здесь будет счетчик операций Notion
        "telegram_messages": 0    # Здесь будет счетчик сообщений Telegram
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    logger.error(f"❌ Необработанное исключение: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": int(time.time())
        }
    )

if __name__ == "__main__":
    # Запуск сервера
    uvicorn.run(
        "llm_api_server:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        reload=SERVER_CONFIG["reload"],
        log_level=SERVER_CONFIG.get("log_level", "info").lower()
    ) 