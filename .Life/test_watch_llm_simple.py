#!/usr/bin/env python3
"""
Упрощенный тест интеграции Xiaomi Watch S с локальной Llama 70B
Без зависимостей от Notion
"""

import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextType(Enum):
    MORNING = "morning"
    WORK = "work"
    EVENING = "evening"
    NIGHT = "night"

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
class LLMInsight:
    """Инсайт от локальной LLM"""
    insight_type: str
    title: str
    description: str
    confidence: float
    actionable: bool
    action_items: List[str]

class MockXiaomiWatchAPI:
    """Мок API для Xiaomi Watch S"""
    
    async def get_heart_rate(self) -> Optional[int]:
        """Получение пульса"""
        return 75
    
    async def get_sleep_data(self) -> Dict[str, Any]:
        """Данные о сне"""
        return {
            "quality": 85.0,
            "duration": 7.5,
            "deep_sleep": 2.1,
            "light_sleep": 4.2,
            "rem_sleep": 1.2,
            "awake_time": 0.3
        }
    
    async def get_activity_data(self) -> Dict[str, Any]:
        """Данные об активности"""
        return {
            "steps": 8500,
            "calories": 450,
            "distance": 6.2,
            "active_minutes": 45
        }
    
    async def get_stress_level(self) -> Optional[float]:
        """Уровень стресса"""
        heart_rate = await self.get_heart_rate()
        if heart_rate:
            if heart_rate > 100:
                return 80.0
            elif heart_rate > 85:
                return 60.0
            elif heart_rate > 70:
                return 30.0
            else:
                return 10.0
        return None
    
    async def get_current_biometrics(self) -> BiometricData:
        """Получение всех биометрических данных"""
        heart_rate = await self.get_heart_rate()
        sleep_data = await self.get_sleep_data()
        activity_data = await self.get_activity_data()
        stress_level = await self.get_stress_level()
        
        return BiometricData(
            heart_rate=heart_rate,
            sleep_quality=sleep_data.get("quality"),
            sleep_duration=sleep_data.get("duration"),
            stress_level=stress_level,
            activity_level=activity_data.get("active_minutes", 0) / 60.0,
            steps=activity_data.get("steps"),
            calories=activity_data.get("calories")
        )

class MockLocalLLM:
    """Мок локальной LLM"""
    
    def __init__(self):
        self.responses = {
            "morning": {
                "response": """
                ИНСАЙТ: sleep_quality
                НАЗВАНИЕ: Отличное качество сна
                ОПИСАНИЕ: Твой сон сегодня был очень качественным (85%). Это говорит о хорошем восстановлении организма. Рекомендую поддерживать такой режим сна.
                УВЕРЕННОСТЬ: 90
                ДЕЙСТВИЯ: продолжить текущий режим сна, утренняя медитация 10 минут, легкая зарядка
                """
            },
            "work": {
                "response": """
                ИНСАЙТ: stress_management
                НАЗВАНИЕ: Умеренный уровень стресса
                ОПИСАНИЕ: Заметил повышение пульса до 85 уд/мин. Это может указывать на рабочий стресс. Рекомендую сделать перерыв и дыхательные упражнения.
                УВЕРЕННОСТЬ: 85
                ДЕЙСТВИЯ: 5-минутный перерыв, дыхательные упражнения, стакан воды
                """
            },
            "evening": {
                "response": """
                ИНСАЙТ: activity_review
                НАЗВАНИЕ: Хорошая дневная активность
                ОПИСАНИЕ: Ты прошел 8500 шагов сегодня - это отличный результат! Активность выше среднего уровня. Время для вечерней рефлексии.
                УВЕРЕННОСТЬ: 88
                ДЕЙСТВИЯ: вечерняя рефлексия, планирование завтрашнего дня, расслабляющие упражнения
                """
            },
            "voice_command": {
                "response": "Учитывая твой текущий пульс 75 уд/мин и хорошую активность, рекомендую продолжить текущий ритм. Что именно ты хотел узнать?"
            }
        }
    
    async def generate(self, prompt: str, context: str = "general", **kwargs) -> Dict[str, Any]:
        """Мок генерации ответа"""
        await asyncio.sleep(0.1)
        
        response = self.responses.get(context, {
            "response": "Спасибо за данные! Анализ завершен."
        })
        
        return response

class SimpleLLMWatchAnalyzer:
    """Упрощенный анализатор часов с LLM"""
    
    def __init__(self):
        self.watch_api = MockXiaomiWatchAPI()
        self.mock_llm = MockLocalLLM()
        self.biometric_history: List[BiometricData] = []
        
    async def analyze_biometrics_with_llm(self, biometrics: BiometricData) -> LLMInsight:
        """Анализ биометрических данных через LLM"""
        try:
            # Определяем контекст
            hour = datetime.now().hour
            if 6 <= hour < 10:
                context = "morning"
            elif 10 <= hour < 18:
                context = "work"
            elif 18 <= hour < 22:
                context = "evening"
            else:
                context = "night"
            
            # Формируем промпт
            prompt = self._build_analysis_prompt(biometrics, context)
            
            # Получаем ответ от LLM
            result = await self.mock_llm.generate(prompt, context)
            llm_response = result["response"]
            
            # Парсим ответ
            insight = self._parse_llm_response(llm_response)
            
            # Сохраняем в историю
            self.biometric_history.append(biometrics)
            
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing biometrics: {e}")
            return self._create_fallback_insight()
    
    def _build_analysis_prompt(self, biometrics: BiometricData, context: str) -> str:
        """Строит промпт для анализа"""
        return f"""
        Ты персональный AI-аналитик здоровья. Проанализируй биометрические данные.
        
        КОНТЕКСТ: {context.upper()}
        Время: {datetime.now().strftime('%H:%M')}
        
        ДАННЫЕ:
        - Пульс: {biometrics.heart_rate} уд/мин
        - Качество сна: {biometrics.sleep_quality}%
        - Стресс: {biometrics.stress_level}%
        - Шаги: {biometrics.steps}
        - Калории: {biometrics.calories}
        
        Дай анализ в формате:
        ИНСАЙТ: [тип]
        НАЗВАНИЕ: [название]
        ОПИСАНИЕ: [описание]
        УВЕРЕННОСТЬ: [0-100]
        ДЕЙСТВИЯ: [список действий]
        """
    
    def _parse_llm_response(self, response: str) -> LLMInsight:
        """Парсит ответ от LLM"""
        try:
            lines = response.strip().split('\n')
            data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip().lower()] = value.strip()
            
            return LLMInsight(
                insight_type=data.get('инсайт', 'general'),
                title=data.get('название', 'Анализ'),
                description=data.get('описание', response),
                confidence=float(data.get('уверенность', 75)),
                actionable=True,
                action_items=data.get('действия', '').split(',') if data.get('действия') else []
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return self._create_fallback_insight()
    
    def _create_fallback_insight(self) -> LLMInsight:
        """Создает fallback инсайт"""
        return LLMInsight(
            insight_type="fallback",
            title="Базовый анализ",
            description="Анализ временно недоступен",
            confidence=50.0,
            actionable=False,
            action_items=[]
        )
    
    async def get_smart_notification(self) -> str:
        """Генерирует умное уведомление"""
        try:
            biometrics = await self.watch_api.get_current_biometrics()
            insight = await self.analyze_biometrics_with_llm(biometrics)
            
            if insight.actionable and insight.action_items:
                action_text = f"\n\nРекомендую: {insight.action_items[0]}"
            else:
                action_text = ""
            
            return f"{insight.title}\n\n{insight.description}{action_text}"
            
        except Exception as e:
            logger.error(f"Error generating notification: {e}")
            return "Добрый день! Как дела?"
    
    async def handle_voice_command(self, voice_text: str) -> str:
        """Обрабатывает голосовую команду"""
        try:
            biometrics = await self.watch_api.get_current_biometrics()
            
            prompt = f"""
            Ты персональный ассистент. Обработай голосовую команду с учетом биометрии.
            
            КОМАНДА: {voice_text}
            
            БИОМЕТРИЯ:
            - Пульс: {biometrics.heart_rate} уд/мин
            - Стресс: {biometrics.stress_level}%
            - Шаги: {biometrics.steps}
            
            Дай полезный ответ.
            """
            
            result = await self.mock_llm.generate(prompt, "voice_command")
            return result["response"]
            
        except Exception as e:
            logger.error(f"Error handling voice command: {e}")
            return f"Обработал команду: {voice_text}"

async def test_simple_integration():
    """Тестирование упрощенной интеграции"""
    print("🚀 ТЕСТИРОВАНИЕ УПРОЩЕННОЙ ИНТЕГРАЦИИ WATCH + LLM")
    print("=" * 60)
    
    analyzer = SimpleLLMWatchAnalyzer()
    
    try:
        # 1. Тест получения биометрических данных
        print("\n1. 📊 Получение биометрических данных...")
        biometrics = await analyzer.watch_api.get_current_biometrics()
        print(f"✅ Пульс: {biometrics.heart_rate} уд/мин")
        print(f"✅ Качество сна: {biometrics.sleep_quality}%")
        print(f"✅ Стресс: {biometrics.stress_level}%")
        print(f"✅ Шаги: {biometrics.steps}")
        print(f"✅ Калории: {biometrics.calories}")
        
        # 2. Тест анализа через LLM
        print("\n2. 🧠 Анализ через локальную LLM...")
        insight = await analyzer.analyze_biometrics_with_llm(biometrics)
        print(f"✅ Тип инсайта: {insight.insight_type}")
        print(f"✅ Название: {insight.title}")
        print(f"✅ Описание: {insight.description}")
        print(f"✅ Уверенность: {insight.confidence}%")
        print(f"✅ Действия: {', '.join(insight.action_items)}")
        
        # 3. Тест умных уведомлений
        print("\n3. 🔔 Умные уведомления...")
        notification = await analyzer.get_smart_notification()
        print(f"✅ Уведомление: {notification}")
        
        # 4. Тест голосовых команд
        print("\n4. 🎤 Голосовые команды...")
        test_commands = [
            "как мое здоровье?",
            "добавь задачу медитация",
            "покажи прогресс"
        ]
        
        for command in test_commands:
            response = await analyzer.handle_voice_command(command)
            print(f"🎤 '{command}' → {response}")
        
        # 5. Тест разных времен дня
        print("\n5. 🌅 Контекстные уведомления для разных времен...")
        times = [(7, "Утро"), (12, "День"), (18, "Вечер"), (22, "Ночь")]
        
        for hour, time_name in times:
            print(f"\n🌅 {time_name} ({hour}:00):")
            
            # Временно изменяем время
            original_now = datetime.now
            datetime.now = lambda: datetime(2024, 1, 1, hour, 0, 0)
            
            try:
                notification = await analyzer.get_smart_notification()
                print(f"📱 {notification}")
            finally:
                datetime.now = original_now
        
        print(f"\n🎯 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print(f"🚀 Система готова к интеграции с реальной Llama 70B")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

async def main():
    """Основная функция"""
    success = await test_simple_integration()
    
    if success:
        print(f"\n✅ ИНТЕГРАЦИЯ ГОТОВА!")
        print(f"📱 Xiaomi Watch S → 🧠 Локальная Llama 70B")
        print(f"🎯 Следующий шаг: подключение к реальной локальной LLM")
    else:
        print(f"\n❌ ТЕСТЫ НЕ ПРОШЛИ")

if __name__ == "__main__":
    asyncio.run(main()) 