#!/usr/bin/env python3
"""
Упрощенный FastAPI сервер для тестирования
"""

import json
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Создание FastAPI приложения
app = FastAPI(
    title="Quick Voice Assistant API",
    description="API для обработки голосовых команд",
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

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Quick Voice Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Статус здоровья сервера"""
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "components": {
            "llm": True,
            "notion": True,
            "telegram": True
        }
    }

@app.get("/ping")
async def ping():
    """Проверка доступности сервера"""
    return {
        "status": "ok",
        "timestamp": int(time.time()),
        "message": "pong"
    }

@app.post("/watch/voice")
async def process_voice_command(request: dict):
    """Обработка голосовой команды от часов"""
    try:
        query = request.get("query", "")
        context = request.get("context", "watch_voice")
        user_id = request.get("user_id", "test_user")
        
        print(f"🎤 Получена команда: {query}")
        
        # Простая обработка команд
        response_text = "Команда обработана успешно!"
        action = None
        data = {}
        
        query_lower = query.lower()
        
        if "задача" in query_lower or "добавь" in query_lower:
            action = "create_task"
            task_text = query.replace("добавь задачу", "").replace("создай задачу", "").strip()
            data["task"] = task_text
            response_text = f"Задача '{task_text}' создана!"
            
        elif "рефлексия" in query_lower or "мысль" in query_lower:
            action = "save_reflection"
            reflection_text = query.replace("добавь рефлексию", "").replace("запиши мысль", "").strip()
            data["reflection"] = reflection_text
            response_text = f"Рефлексия '{reflection_text}' сохранена!"
            
        elif "привычка" in query_lower:
            action = "create_habit"
            habit_text = query.replace("создай привычку", "").replace("привычка", "").strip()
            data["habit"] = habit_text
            response_text = f"Привычка '{habit_text}' создана!"
            
        elif "как дела" in query_lower:
            response_text = "Отлично! Готов помочь с задачами и рефлексиями."
            
        elif "помощь" in query_lower:
            response_text = "Доступные команды: добавить задачу, записать рефлексию, создать привычку"
            
        else:
            response_text = "Команда распознана. Что еще могу помочь?"
        
        return {
            "response": response_text,
            "action": action,
            "data": data,
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/telegram/send")
async def send_telegram_message(request: dict):
    """Отправка сообщения в Telegram"""
    try:
        message = request.get("message", "")
        source = request.get("source", "watch_voice")
        
        print(f"📱 Отправка в Telegram: {message[:50]}...")
        
        return {
            "status": "sent",
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Метрики производительности"""
    return {
        "uptime": int(time.time()),
        "requests_processed": 0,
        "llm_requests": 0,
        "notion_operations": 0,
        "telegram_messages": 0
    }

if __name__ == "__main__":
    print("🚀 Запуск упрощенного сервера...")
    print("📡 Сервер будет доступен на http://localhost:8000")
    print("🔍 Для тестирования используйте: python test_watch_api.py")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 