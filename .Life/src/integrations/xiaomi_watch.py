#!/usr/bin/env python3
"""
Интеграция с Xiaomi Watch S
Голосовые команды, биометрические данные, умные уведомления
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, UTC
from dataclasses import dataclass
import httpx

# Импорты для голосового интерфейса
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logging.warning("Speech recognition not available. Install speech_recognition and pyttsx3")

from ..agents.agent_core import agent_core
from ..notion.universal_repository import UniversalNotionRepository
from ..core.config import Settings

logger = logging.getLogger(__name__)

@dataclass
class BiometricData:
    """Структура биометрических данных"""
    heart_rate: Optional[int] = None
    sleep_quality: Optional[float] = None
    sleep_duration: Optional[float] = None
    stress_level: Optional[float] = None
    activity_level: Optional[float] = None
    steps: Optional[int] = None
    calories: Optional[int] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)

@dataclass
class VoiceCommand:
    """Структура голосовой команды"""
    text: str
    intent: str
    confidence: float
    biometrics: Optional[BiometricData] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

class XiaomiWatchAPI:
    """API для работы с Xiaomi Watch S"""
    
    def __init__(self):
        self.base_url = "https://api.mi.com/v1"
        self.session = httpx.AsyncClient()
        self.biometric_cache = {}
        
    async def get_heart_rate(self) -> Optional[int]:
        """Получение пульса в реальном времени"""
        try:
            # Здесь будет реальный API вызов к Xiaomi
            # Пока используем моковые данные
            return 75  # Моковые данные
        except Exception as e:
            logger.error(f"Error getting heart rate: {e}")
            return None
    
    async def get_sleep_data(self) -> Dict[str, Any]:
        """Данные о сне за последнюю ночь"""
        try:
            # Моковые данные сна
            return {
                "quality": 85.0,
                "duration": 7.5,
                "deep_sleep": 2.1,
                "light_sleep": 4.2,
                "rem_sleep": 1.2,
                "awake_time": 0.3
            }
        except Exception as e:
            logger.error(f"Error getting sleep data: {e}")
            return {}
    
    async def get_activity_data(self) -> Dict[str, Any]:
        """Данные об активности за день"""
        try:
            return {
                "steps": 8500,
                "calories": 450,
                "distance": 6.2,
                "active_minutes": 45
            }
        except Exception as e:
            logger.error(f"Error getting activity data: {e}")
            return {}
    
    async def get_stress_level(self) -> Optional[float]:
        """Уровень стресса (0-100)"""
        try:
            # Анализ на основе пульса и других данных
            heart_rate = await self.get_heart_rate()
            if heart_rate:
                # Простая логика определения стресса
                if heart_rate > 100:
                    return 80.0
                elif heart_rate > 85:
                    return 60.0
                elif heart_rate > 70:
                    return 30.0
                else:
                    return 10.0
            return None
        except Exception as e:
            logger.error(f"Error getting stress level: {e}")
            return None
    
    async def get_current_biometrics(self) -> BiometricData:
        """Получение всех текущих биометрических данных"""
        heart_rate = await self.get_heart_rate()
        sleep_data = await self.get_sleep_data()
        activity_data = await self.get_activity_data()
        stress_level = await self.get_stress_level()
        
        return BiometricData(
            heart_rate=heart_rate,
            sleep_quality=sleep_data.get("quality"),
            sleep_duration=sleep_data.get("duration"),
            stress_level=stress_level,
            activity_level=activity_data.get("active_minutes", 0) / 60.0,  # Часы активности
            steps=activity_data.get("steps"),
            calories=activity_data.get("calories")
        )

class VoiceProcessor:
    """Обработка голосовых команд"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer() if VOICE_AVAILABLE else None
        self.engine = pyttsx3.init() if VOICE_AVAILABLE else None
        
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Преобразование речи в текст"""
        if not VOICE_AVAILABLE:
            return "Speech recognition not available"
        
        try:
            # Здесь будет обработка аудио с часов
            # Пока возвращаем тестовый текст
            return "добавь задачу купить продукты"
        except Exception as e:
            logger.error(f"Error in speech to text: {e}")
            return ""
    
    async def text_to_speech(self, text: str) -> bytes:
        """Преобразование текста в речь"""
        if not VOICE_AVAILABLE:
            return b""
        
        try:
            # Генерация аудио ответа
            self.engine.say(text)
            self.engine.runAndWait()
            return b"audio_data"  # Моковые данные
        except Exception as e:
            logger.error(f"Error in text to speech: {e}")
            return b""

class IntentRecognizer:
    """Распознавание намерений в голосовых командах"""
    
    def __init__(self):
        self.intent_patterns = {
            "add_task": [
                "добавь задачу", "создай задачу", "новая задача",
                "add task", "create task", "new task"
            ],
            "add_habit": [
                "добавь привычку", "создай привычку", "новая привычка",
                "add habit", "create habit", "new habit"
            ],
            "add_reflection": [
                "мое настроение", "добавь рефлексию", "запиши мысли",
                "my mood", "add reflection", "write thoughts"
            ],
            "check_progress": [
                "мой прогресс", "как дела", "статистика",
                "my progress", "how am i doing", "statistics"
            ],
            "chat": [
                "поговори со мной", "нужна помощь", "посоветуй",
                "talk to me", "need help", "advise me"
            ]
        }
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Анализ текста и определение намерения"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return {
                        "intent": intent,
                        "confidence": 0.9,
                        "text": text,
                        "extracted_data": self._extract_data(text, intent)
                    }
        
        # Если не найдено конкретное намерение, считаем это чатом
        return {
            "intent": "chat",
            "confidence": 0.5,
            "text": text,
            "extracted_data": {}
        }
    
    def _extract_data(self, text: str, intent: str) -> Dict[str, Any]:
        """Извлечение данных из команды"""
        if intent == "add_task":
            # Извлекаем описание задачи
            if "добавь задачу" in text.lower():
                task_desc = text.lower().replace("добавь задачу", "").strip()
                return {"task_description": task_desc}
        elif intent == "add_habit":
            if "добавь привычку" in text.lower():
                habit_name = text.lower().replace("добавь привычку", "").strip()
                return {"habit_name": habit_name}
        elif intent == "add_reflection":
            if "мое настроение" in text.lower():
                mood_desc = text.lower().replace("мое настроение", "").strip()
                return {"mood_description": mood_desc}
        
        return {}

class XiaomiWatchIntegration:
    """Основной класс интеграции с Xiaomi Watch S"""
    
    def __init__(self):
        self.watch_api = XiaomiWatchAPI()
        self.voice_processor = VoiceProcessor()
        self.intent_recognizer = IntentRecognizer()
        self.settings = Settings()
        self.notion_repo = UniversalNotionRepository(self.settings)
        
        # История команд для контекста
        self.command_history = []
        
    async def handle_voice_command(self, audio_data: bytes) -> str:
        """Обработка голосовой команды с часов"""
        try:
            # 1. Преобразование речи в текст
            text = await self.voice_processor.speech_to_text(audio_data)
            if not text:
                return "Не удалось распознать речь"
            
            # 2. Получение биометрических данных
            biometrics = await self.watch_api.get_current_biometrics()
            
            # 3. Анализ намерения
            intent_data = await self.intent_recognizer.analyze(text)
            
            # 4. Создание команды
            command = VoiceCommand(
                text=text,
                intent=intent_data["intent"],
                confidence=intent_data["confidence"],
                biometrics=biometrics,
                context=intent_data["extracted_data"]
            )
            
            # 5. Выполнение команды
            response = await self._execute_command(command)
            
            # 6. Сохранение в историю
            self.command_history.append(command)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling voice command: {e}")
            return f"Произошла ошибка: {str(e)}"
    
    async def _execute_command(self, command: VoiceCommand) -> str:
        """Выполнение голосовой команды"""
        try:
            if command.intent == "add_task":
                return await self._add_task(command)
            elif command.intent == "add_habit":
                return await self._add_habit(command)
            elif command.intent == "add_reflection":
                return await self._add_reflection(command)
            elif command.intent == "check_progress":
                return await self._check_progress(command)
            elif command.intent == "chat":
                return await self._chat_with_ai(command)
            else:
                return "Неизвестная команда"
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return f"Ошибка выполнения команды: {str(e)}"
    
    async def _add_task(self, command: VoiceCommand) -> str:
        """Добавление задачи"""
        task_desc = command.context.get("task_description", command.text)
        
        # Создаем задачу в Notion
        task_data = {
            "title": task_desc,
            "status": "pending",
            "priority": "medium",
            "created_date": datetime.now(UTC).isoformat()
        }
        
        result = await self.notion_repo.create_action(task_data)
        
        if result:
            return f"Задача '{task_desc}' успешно добавлена"
        else:
            return "Не удалось добавить задачу"
    
    async def _add_habit(self, command: VoiceCommand) -> str:
        """Добавление привычки"""
        habit_name = command.context.get("habit_name", command.text)
        
        habit_data = {
            "title": habit_name,
            "status": "active",
            "frequency": "daily",
            "created_date": datetime.now(UTC).isoformat()
        }
        
        result = await self.notion_repo.create_habit(habit_data)
        
        if result:
            return f"Привычка '{habit_name}' успешно добавлена"
        else:
            return "Не удалось добавить привычку"
    
    async def _add_reflection(self, command: VoiceCommand) -> str:
        """Добавление рефлексии"""
        mood_desc = command.context.get("mood_description", command.text)
        
        # Анализируем биометрические данные для определения настроения
        mood_type = self._analyze_mood_from_biometrics(command.biometrics)
        
        reflection_data = {
            "title": f"Рефлексия {datetime.now().strftime('%H:%M')}",
            "type": "mood",
            "content": mood_desc,
            "mood": mood_type,
            "created_date": datetime.now(UTC).isoformat()
        }
        
        result = await self.notion_repo.create_reflection(reflection_data)
        
        if result:
            return f"Рефлексия записана. Определенное настроение: {mood_type}"
        else:
            return "Не удалось записать рефлексию"
    
    async def _check_progress(self, command: VoiceCommand) -> str:
        """Проверка прогресса"""
        try:
            # Получаем данные из Notion
            habits = await self.notion_repo.get_habits()
            actions = await self.notion_repo.get_actions()
            reflections = await self.notion_repo.get_reflections()
            
            # Анализируем биометрические данные
            biometrics = command.biometrics
            
            progress_summary = f"""
📊 Ваш прогресс:
• Привычек: {len(habits)} активных
• Задач: {len([a for a in actions if a.get('status') == 'completed'])} выполнено
• Рефлексий: {len(reflections)} за сегодня
• Пульс: {biometrics.heart_rate} уд/мин
• Стресс: {biometrics.stress_level:.0f}%
• Активность: {biometrics.steps} шагов
            """.strip()
            
            return progress_summary
            
        except Exception as e:
            logger.error(f"Error checking progress: {e}")
            return "Не удалось получить данные о прогрессе"
    
    async def _chat_with_ai(self, command: VoiceCommand) -> str:
        """Чат с ИИ на основе контекста"""
        try:
            # Формируем контекст для ИИ
            context = f"""
Пользователь: {command.text}

Биометрические данные:
- Пульс: {command.biometrics.heart_rate} уд/мин
- Стресс: {command.biometrics.stress_level:.0f}%
- Качество сна: {command.biometrics.sleep_quality:.0f}%
- Активность: {command.biometrics.steps} шагов

История команд: {[cmd.text for cmd in self.command_history[-3:]]}
            """.strip()
            
            # Получаем ответ от ИИ
            response = await agent_core.get_agent_response(
                role="Personal Assistant",
                context=context,
                user_input=command.text,
                model_type="default"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error chatting with AI: {e}")
            return "Не удалось получить ответ от ИИ"
    
    def _analyze_mood_from_biometrics(self, biometrics: BiometricData) -> str:
        """Анализ настроения на основе биометрических данных"""
        if biometrics.stress_level is None:
            return "neutral"
        
        if biometrics.stress_level > 70:
            return "stressed"
        elif biometrics.stress_level > 40:
            return "anxious"
        elif biometrics.stress_level > 20:
            return "calm"
        else:
            return "relaxed"
    
    async def get_smart_notification(self) -> str:
        """Генерация умного уведомления на основе биометрии"""
        try:
            biometrics = await self.watch_api.get_current_biometrics()
            current_hour = datetime.now().hour
            
            if 6 <= current_hour < 10:
                # Утреннее уведомление
                sleep_quality = biometrics.sleep_quality or 0
                return f"Доброе утро! Качество сна: {sleep_quality:.0f}%. " + \
                       ("Рекомендую 10 минут медитации" if sleep_quality < 80 else "Отличный сон!")
            
            elif 10 <= current_hour < 18:
                # Дневное уведомление
                if biometrics.stress_level and biometrics.stress_level > 60:
                    return "Заметил повышение стресса. Хочешь поговорить или сделать перерыв?"
                elif biometrics.steps and biometrics.steps < 5000:
                    return "Мало активности сегодня. Рекомендую прогулку!"
            
            elif 18 <= current_hour < 22:
                # Вечернее уведомление
                return "Время для вечерней рефлексии. Как прошел день?"
            
            else:
                # Ночное уведомление
                return "Пора готовиться ко сну. Рекомендую отключить уведомления"
                
        except Exception as e:
            logger.error(f"Error generating smart notification: {e}")
            return "Добрый день! Как дела?"

# Глобальный экземпляр интеграции
xiaomi_integration = XiaomiWatchIntegration() 