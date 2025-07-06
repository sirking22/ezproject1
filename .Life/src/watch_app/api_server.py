#!/usr/bin/env python3
"""
API сервер для Life Watch App
Обрабатывает данные с Xiaomi Watch S и интегрирует с существующей системой
"""

import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Модели данных
class WatchData(BaseModel):
    type: str = Field(..., description="Тип данных (heart_rate, activity, task, voice_command, etc.)")
    data: Dict[str, Any] = Field(..., description="Данные с часов")
    timestamp: int = Field(..., description="Временная метка")

class NotificationData(BaseModel):
    title: str = Field(..., description="Заголовок уведомления")
    message: str = Field(..., description="Текст уведомления")
    icon: Optional[str] = Field(None, description="Иконка")
    vibration: bool = Field(True, description="Вибрация")
    sound: bool = Field(True, description="Звук")
    duration: int = Field(5000, description="Длительность в мс")

class AIResponse(BaseModel):
    response: str = Field(..., description="Ответ от ИИ")
    context: Optional[Dict[str, Any]] = Field(None, description="Контекст")
    confidence: float = Field(0.8, description="Уверенность")

class SyncResponse(BaseModel):
    status: str = Field(..., description="Статус синхронизации")
    message: str = Field(..., description="Сообщение")
    processed_count: int = Field(0, description="Количество обработанных записей")

# Создание FastAPI приложения
app = FastAPI(
    title="Life Watch API",
    description="API для интеграции Xiaomi Watch S с системой личностного развития",
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

# Глобальные переменные для хранения данных
watch_data_buffer: List[Dict[str, Any]] = []
notifications_queue: List[Dict[str, Any]] = []
ai_responses_queue: List[Dict[str, Any]] = []

class WatchDataProcessor:
    """Обработчик данных с часов"""
    
    def __init__(self):
        self.stats = {
            "heart_rate_count": 0,
            "activity_count": 0,
            "task_count": 0,
            "voice_command_count": 0,
            "total_processed": 0
        }
    
    async def process_heart_rate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка данных пульса"""
        logger.info(f"Обработка данных пульса: {data}")
        
        heart_rate = data.get("heartRate", 0)
        quality = data.get("quality", "unknown")
        timestamp = data.get("timestamp", 0)
        
        # Анализ стресса
        stress_level = self._analyze_stress(heart_rate)
        
        # Сохранение в буфер для интеграции с Notion
        processed_data = {
            "type": "heart_rate",
            "heart_rate": heart_rate,
            "quality": quality,
            "stress_level": stress_level,
            "timestamp": timestamp,
            "processed_at": datetime.now(UTC).isoformat()
        }
        
        watch_data_buffer.append(processed_data)
        self.stats["heart_rate_count"] += 1
        self.stats["total_processed"] += 1
        
        # Генерация уведомлений при необходимости
        if stress_level == "high":
            await self._generate_stress_notification(heart_rate)
        
        return processed_data
    
    async def process_activity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка данных активности"""
        logger.info(f"Обработка данных активности: {data}")
        
        steps = data.get("steps", 0)
        calories = data.get("calories", 0)
        distance = data.get("distance", 0)
        active_minutes = data.get("activeMinutes", 0)
        timestamp = data.get("timestamp", 0)
        
        # Проверка целей
        goals_achieved = self._check_activity_goals(steps, calories)
        
        # Сохранение в буфер
        processed_data = {
            "type": "activity",
            "steps": steps,
            "calories": calories,
            "distance": distance,
            "active_minutes": active_minutes,
            "goals_achieved": goals_achieved,
            "timestamp": timestamp,
            "processed_at": datetime.now(UTC).isoformat()
        }
        
        watch_data_buffer.append(processed_data)
        self.stats["activity_count"] += 1
        self.stats["total_processed"] += 1
        
        # Генерация уведомлений о достижении целей
        for goal in goals_achieved:
            await self._generate_goal_notification(goal)
        
        return processed_data
    
    async def process_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка задач"""
        logger.info(f"Обработка задачи: {data}")
        
        task_text = data.get("text", "")
        task_id = data.get("id", "")
        completed = data.get("completed", False)
        priority = data.get("priority", "medium")
        timestamp = data.get("timestamp", 0)
        
        # Сохранение в буфер для интеграции с Notion
        processed_data = {
            "type": "task",
            "id": task_id,
            "text": task_text,
            "completed": completed,
            "priority": priority,
            "timestamp": timestamp,
            "processed_at": datetime.now(UTC).isoformat()
        }
        
        watch_data_buffer.append(processed_data)
        self.stats["task_count"] += 1
        self.stats["total_processed"] += 1
        
        # Генерация уведомления о новой задаче
        if not completed:
            await self._generate_task_notification(task_text)
        
        return processed_data
    
    async def process_voice_command(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка голосовых команд"""
        logger.info(f"Обработка голосовой команды: {data}")
        
        command_text = data.get("text", "")
        audio_data = data.get("audio", None)
        timestamp = data.get("timestamp", 0)
        
        # Распознавание намерения
        intent = self._recognize_intent(command_text)
        
        # Сохранение в буфер
        processed_data = {
            "type": "voice_command",
            "text": command_text,
            "intent": intent,
            "audio_data": audio_data is not None,
            "timestamp": timestamp,
            "processed_at": datetime.now(UTC).isoformat()
        }
        
        watch_data_buffer.append(processed_data)
        self.stats["voice_command_count"] += 1
        self.stats["total_processed"] += 1
        
        # Генерация ответа ИИ
        ai_response = await self._generate_ai_response(command_text, intent)
        ai_responses_queue.append(ai_response)
        
        return processed_data
    
    def _analyze_stress(self, heart_rate: int) -> str:
        """Анализ уровня стресса по пульсу"""
        if heart_rate > 100:
            return "high"
        elif heart_rate > 80:
            return "medium"
        else:
            return "low"
    
    def _check_activity_goals(self, steps: int, calories: int) -> List[str]:
        """Проверка достижения целей активности"""
        goals = []
        
        if steps >= 10000:
            goals.append("steps_10000")
        if calories >= 500:
            goals.append("calories_500")
        
        return goals
    
    def _recognize_intent(self, command_text: str) -> str:
        """Распознавание намерения в голосовой команде"""
        command_lower = command_text.lower()
        
        if "добавь задачу" in command_lower or "создай задачу" in command_lower:
            return "add_task"
        elif "покажи прогресс" in command_lower or "статистика" in command_lower:
            return "show_progress"
        elif "рефлексия" in command_lower or "мысли" in command_lower:
            return "add_reflection"
        elif "помощь" in command_lower or "что делать" in command_lower:
            return "help"
        else:
            return "unknown"
    
    async def _generate_stress_notification(self, heart_rate: int):
        """Генерация уведомления о стрессе"""
        notification = {
            "title": "⚠️ Высокий пульс",
            "message": f"Ваш пульс {heart_rate} уд/мин. Рекомендуется отдых.",
            "icon": "heart",
            "vibration": True,
            "sound": True,
            "duration": 5000
        }
        notifications_queue.append(notification)
    
    async def _generate_goal_notification(self, goal: str):
        """Генерация уведомления о достижении цели"""
        if goal == "steps_10000":
            notification = {
                "title": "🎉 Цель достигнута!",
                "message": "10000 шагов выполнено! Отличная работа!",
                "icon": "steps",
                "vibration": True,
                "sound": True,
                "duration": 5000
            }
        elif goal == "calories_500":
            notification = {
                "title": "🔥 Калории сожжены!",
                "message": "500+ калорий сожжено! Продолжайте в том же духе!",
                "icon": "calories",
                "vibration": True,
                "sound": True,
                "duration": 3000
            }
        else:
            return
        
        notifications_queue.append(notification)
    
    async def _generate_task_notification(self, task_text: str):
        """Генерация уведомления о новой задаче"""
        notification = {
            "title": "✅ Задача добавлена",
            "message": task_text[:50] + "..." if len(task_text) > 50 else task_text,
            "icon": "task",
            "vibration": True,
            "sound": True,
            "duration": 3000
        }
        notifications_queue.append(notification)
    
    async def _generate_ai_response(self, command_text: str, intent: str) -> Dict[str, Any]:
        """Генерация ответа ИИ"""
        # Здесь будет интеграция с существующими агентами
        responses = {
            "add_task": f"Задача '{command_text}' добавлена в ваш список дел.",
            "show_progress": "Показываю ваш прогресс за сегодня...",
            "add_reflection": "Записываю ваши мысли...",
            "help": "Я могу помочь добавить задачи, показать прогресс, записать рефлексию.",
            "unknown": "Не совсем понял команду. Попробуйте сказать 'добавь задачу' или 'покажи прогресс'."
        }
        
        response_text = responses.get(intent, responses["unknown"])
        
        return {
            "type": "ai_response",
            "response": response_text,
            "intent": intent,
            "original_command": command_text,
            "timestamp": datetime.now(UTC).isoformat()
        }

# Создание обработчика
processor = WatchDataProcessor()

# API endpoints
@app.post("/watch/sync", response_model=SyncResponse)
async def sync_watch_data(watch_data: WatchData, background_tasks: BackgroundTasks):
    """Синхронизация данных с часов"""
    try:
        logger.info(f"Получены данные с часов: {watch_data.type}")
        
        # Обработка данных в зависимости от типа
        if watch_data.type == "heart_rate":
            processed_data = await processor.process_heart_rate(watch_data.data)
        elif watch_data.type == "activity":
            processed_data = await processor.process_activity(watch_data.data)
        elif watch_data.type == "task":
            processed_data = await processor.process_task(watch_data.data)
        elif watch_data.type == "voice_command":
            processed_data = await processor.process_voice_command(watch_data.data)
        elif watch_data.type == "sleep":
            processed_data = await processor.process_sleep(watch_data.data)
        else:
            raise HTTPException(status_code=400, detail=f"Неизвестный тип данных: {watch_data.type}")
        
        # Запуск фоновой задачи для интеграции с Notion
        background_tasks.add_task(integrate_with_notion, processed_data)
        
        return SyncResponse(
            status="success",
            message=f"Данные типа {watch_data.type} обработаны",
            processed_count=processor.stats["total_processed"]
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки данных: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/phone/notifications")
async def get_notifications():
    """Получение уведомлений для часов"""
    try:
        # Возвращаем все уведомления из очереди
        notifications = notifications_queue.copy()
        notifications_queue.clear()
        
        return {"notifications": notifications}
        
    except Exception as e:
        logger.error(f"Ошибка получения уведомлений: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/phone/ai_responses")
async def get_ai_responses():
    """Получение ответов ИИ для часов"""
    try:
        # Возвращаем все ответы ИИ из очереди
        responses = ai_responses_queue.copy()
        ai_responses_queue.clear()
        
        return {"ai_responses": responses}
        
    except Exception as e:
        logger.error(f"Ошибка получения ответов ИИ: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/phone/ai_chat")
async def ai_chat(chat_data: WatchData):
    """Обработка чата с ИИ"""
    try:
        # Получение ответа от ИИ
        response = await processor._generate_ai_response(
            chat_data.data.get("text", ""),
            processor._recognize_intent(chat_data.data.get("text", ""))
        )
        
        return AIResponse(
            response=response["response"],
            context={"intent": response["intent"]},
            confidence=0.8
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки чата: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Получение статистики обработки данных"""
    return {
        "processor_stats": processor.stats,
        "buffer_size": len(watch_data_buffer),
        "notifications_queue_size": len(notifications_queue),
        "ai_responses_queue_size": len(ai_responses_queue),
        "uptime": datetime.now(UTC).isoformat()
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервера"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0"
    }

# Фоновые задачи
async def integrate_with_notion(data: Dict[str, Any]):
    """Интеграция данных с Notion"""
    try:
        logger.info(f"Интеграция с Notion: {data['type']}")
        
        # Здесь будет код интеграции с существующей системой Notion
        # Пока просто логируем
        logger.info(f"Данные готовы для интеграции: {data}")
        
    except Exception as e:
        logger.error(f"Ошибка интеграции с Notion: {e}")

# Дополнительные методы для процессора
async def process_sleep(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка данных сна"""
    logger.info(f"Обработка данных сна: {data}")
    
    quality = data.get("quality", "unknown")
    duration = data.get("duration", 0)
    deep_sleep = data.get("deepSleep", 0)
    light_sleep = data.get("lightSleep", 0)
    rem_sleep = data.get("remSleep", 0)
    timestamp = data.get("timestamp", 0)
    
    # Анализ качества сна
    sleep_score = self._calculate_sleep_score(quality, duration, deep_sleep)
    
    processed_data = {
        "type": "sleep",
        "quality": quality,
        "duration": duration,
        "deep_sleep": deep_sleep,
        "light_sleep": light_sleep,
        "rem_sleep": rem_sleep,
        "sleep_score": sleep_score,
        "timestamp": timestamp,
        "processed_at": datetime.now(UTC).isoformat()
    }
    
    watch_data_buffer.append(processed_data)
    self.stats["total_processed"] += 1
    
    # Генерация уведомления о качестве сна
    if sleep_score < 0.6:
        await self._generate_sleep_notification(sleep_score)
    
    return processed_data

def _calculate_sleep_score(self, quality: str, duration: float, deep_sleep: float) -> float:
    """Расчет оценки качества сна"""
    score = 0.0
    
    # Качество сна
    if quality == "good":
        score += 0.4
    elif quality == "fair":
        score += 0.2
    
    # Продолжительность сна
    if 7 <= duration <= 9:
        score += 0.4
    elif 6 <= duration < 7 or 9 < duration <= 10:
        score += 0.2
    
    # Глубокий сон
    if deep_sleep >= 1.5:
        score += 0.2
    
    return min(score, 1.0)

async def _generate_sleep_notification(self, sleep_score: float):
    """Генерация уведомления о качестве сна"""
    if sleep_score < 0.4:
        message = "Качество сна низкое. Рекомендуется больше спать."
    else:
        message = "Качество сна удовлетворительное."
    
    notification = {
        "title": "😴 Качество сна",
        "message": message,
        "icon": "sleep",
        "vibration": True,
        "sound": True,
        "duration": 5000
    }
    notifications_queue.append(notification)

# Добавляем методы к классу
WatchDataProcessor.process_sleep = process_sleep
WatchDataProcessor._calculate_sleep_score = _calculate_sleep_score
WatchDataProcessor._generate_sleep_notification = _generate_sleep_notification

if __name__ == "__main__":
    logger.info("🚀 Запуск Life Watch API сервера...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    ) 