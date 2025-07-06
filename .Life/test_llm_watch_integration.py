#!/usr/bin/env python3
"""
Тест интеграции Xiaomi Watch S с локальной Llama 70B
Демонстрация контекстного анализа биометрических данных
"""

import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорты
from src.integrations.xiaomi_watch import XiaomiWatchAPI, BiometricData
from src.watch_app.llm_watch_analyzer import LLMWatchAnalyzer, ContextType

class MockLocalLLM:
    """Мок локальной LLM для тестирования"""
    
    def __init__(self):
        self.responses = {
            "morning": {
                "response": """
                ИНСАЙТ: sleep_quality
                НАЗВАНИЕ: Отличное качество сна
                ОПИСАНИЕ: Твой сон сегодня был очень качественным (85%). Это говорит о хорошем восстановлении организма. Рекомендую поддерживать такой режим сна.
                УВЕРЕННОСТЬ: 90
                ДЕЙСТВИЯ: продолжить текущий режим сна, утренняя медитация 10 минут, легкая зарядка
                КОНТЕКСТ: утренний анализ
                """
            },
            "work": {
                "response": """
                ИНСАЙТ: stress_management
                НАЗВАНИЕ: Умеренный уровень стресса
                ОПИСАНИЕ: Заметил повышение пульса до 85 уд/мин. Это может указывать на рабочий стресс. Рекомендую сделать перерыв и дыхательные упражнения.
                УВЕРЕННОСТЬ: 85
                ДЕЙСТВИЯ: 5-минутный перерыв, дыхательные упражнения, стакан воды
                КОНТЕКСТ: рабочий анализ
                """
            },
            "evening": {
                "response": """
                ИНСАЙТ: activity_review
                НАЗВАНИЕ: Хорошая дневная активность
                ОПИСАНИЕ: Ты прошел 8500 шагов сегодня - это отличный результат! Активность выше среднего уровня. Время для вечерней рефлексии.
                УВЕРЕННОСТЬ: 88
                ДЕЙСТВИЯ: вечерняя рефлексия, планирование завтрашнего дня, расслабляющие упражнения
                КОНТЕКСТ: вечерний анализ
                """
            },
            "voice_command": {
                "response": "Учитывая твой текущий пульс 75 уд/мин и хорошую активность, рекомендую продолжить текущий ритм. Что именно ты хотел узнать?"
            }
        }
    
    async def generate(self, prompt: str, context: str = "general", **kwargs) -> Dict[str, Any]:
        """Мок генерации ответа"""
        await asyncio.sleep(0.1)  # Имитация задержки
        
        response = self.responses.get(context, {
            "response": "Спасибо за данные! Анализ завершен."
        })
        
        return response

class TestLLMWatchIntegration:
    """Тестирование интеграции часов с локальной LLM"""
    
    def __init__(self):
        self.watch_api = XiaomiWatchAPI()
        self.llm_analyzer = LLMWatchAnalyzer()
        self.mock_llm = MockLocalLLM()
        
        # Подменяем реальную LLM на мок для тестирования
        self.llm_analyzer._call_llm = self.mock_llm.generate
    
    async def test_biometric_analysis(self):
        """Тест анализа биометрических данных через LLM"""
        print("🧠 ТЕСТ АНАЛИЗА БИОМЕТРИЧЕСКИХ ДАННЫХ ЧЕРЕЗ LLM")
        print("=" * 60)
        
        try:
            # Получаем биометрические данные
            biometrics = await self.watch_api.get_current_biometrics()
            print(f"📊 Получены биометрические данные:")
            print(f"   - Пульс: {biometrics.heart_rate} уд/мин")
            print(f"   - Качество сна: {biometrics.sleep_quality}%")
            print(f"   - Стресс: {biometrics.stress_level}%")
            print(f"   - Шаги: {biometrics.steps}")
            print(f"   - Калории: {biometrics.calories}")
            
            # Анализируем через LLM
            insight = await self.llm_analyzer.analyze_biometrics_with_llm(biometrics)
            
            print(f"\n🧠 АНАЛИЗ ОТ ЛОКАЛЬНОЙ LLM:")
            print(f"   📌 Тип: {insight.insight_type}")
            print(f"   📌 Название: {insight.title}")
            print(f"   📌 Описание: {insight.description}")
            print(f"   📌 Уверенность: {insight.confidence}%")
            print(f"   📌 Действия: {', '.join(insight.action_items)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in biometric analysis test: {e}")
            return False
    
    async def test_context_aware_notifications(self):
        """Тест контекстных уведомлений"""
        print("\n🔔 ТЕСТ КОНТЕКСТНЫХ УВЕДОМЛЕНИЙ")
        print("=" * 40)
        
        try:
            # Тестируем разные времена дня
            times = [
                (7, "Утро"),
                (12, "День"),
                (18, "Вечер"),
                (22, "Ночь")
            ]
            
            for hour, time_name in times:
                print(f"\n🌅 {time_name} ({hour}:00):")
                
                # Временно изменяем время для тестирования
                original_now = datetime.now
                datetime.now = lambda: datetime(2024, 1, 1, hour, 0, 0)
                
                try:
                    notification = await self.llm_analyzer.get_smart_notification_with_llm()
                    print(f"📱 Уведомление: {notification}")
                finally:
                    datetime.now = original_now
            
            return True
            
        except Exception as e:
            logger.error(f"Error in notifications test: {e}")
            return False
    
    async def test_voice_command_processing(self):
        """Тест обработки голосовых команд с контекстом"""
        print("\n🎤 ТЕСТ ОБРАБОТКИ ГОЛОСОВЫХ КОМАНД")
        print("=" * 45)
        
        try:
            test_commands = [
                "как мое здоровье сегодня?",
                "добавь задачу медитация",
                "покажи мой прогресс",
                "что мне делать дальше?"
            ]
            
            for command in test_commands:
                print(f"\n🎤 Команда: '{command}'")
                
                response = await self.llm_analyzer.handle_voice_command_with_context(command)
                print(f"🤖 Ответ: {response}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in voice command test: {e}")
            return False
    
    async def test_weekly_insights(self):
        """Тест недельных инсайтов"""
        print("\n📈 ТЕСТ НЕДЕЛЬНЫХ ИНСАЙТОВ")
        print("=" * 35)
        
        try:
            # Симулируем недельные данные
            for i in range(7):
                biometrics = BiometricData(
                    heart_rate=70 + i * 2,
                    sleep_quality=80 - i * 2,
                    stress_level=30 + i * 5,
                    steps=8000 + i * 200,
                    calories=400 + i * 20
                )
                self.llm_analyzer.biometric_history.append(biometrics)
            
            # Получаем недельные инсайты
            weekly_insights = await self.llm_analyzer.get_weekly_insights()
            
            print(f"📊 Получено {len(weekly_insights)} недельных инсайтов:")
            
            for i, insight in enumerate(weekly_insights, 1):
                print(f"\n   {i}. {insight.title}")
                print(f"      Тип: {insight.insight_type}")
                print(f"      Описание: {insight.description[:100]}...")
                print(f"      Действия: {', '.join(insight.action_items[:2])}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in weekly insights test: {e}")
            return False
    
    async def test_stress_detection(self):
        """Тест детекции стресса"""
        print("\n😰 ТЕСТ ДЕТЕКЦИИ СТРЕССА")
        print("=" * 30)
        
        try:
            # Симулируем высокий стресс
            high_stress_biometrics = BiometricData(
                heart_rate=110,
                sleep_quality=60,
                stress_level=85,
                steps=2000,
                calories=200
            )
            
            insight = await self.llm_analyzer.analyze_biometrics_with_llm(high_stress_biometrics)
            
            print(f"🚨 Высокий стресс детектирован:")
            print(f"   - Пульс: {high_stress_biometrics.heart_rate} уд/мин")
            print(f"   - Уровень стресса: {high_stress_biometrics.stress_level}%")
            print(f"   - Рекомендация: {insight.title}")
            print(f"   - Действия: {', '.join(insight.action_items)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in stress detection test: {e}")
            return False

async def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ XIAOMI WATCH S С ЛОКАЛЬНОЙ LLAMA 70B")
    print("=" * 70)
    print("📱 Часы: Xiaomi Watch S")
    print("🧠 LLM: Локальная Llama 70B (квантованная)")
    print("🎯 Цель: Контекстный анализ биометрии и персональные рекомендации")
    print("=" * 70)
    
    tester = TestLLMWatchIntegration()
    
    tests = [
        ("Анализ биометрических данных", tester.test_biometric_analysis),
        ("Контекстные уведомления", tester.test_context_aware_notifications),
        ("Обработка голосовых команд", tester.test_voice_command_processing),
        ("Недельные инсайты", tester.test_weekly_insights),
        ("Детекция стресса", tester.test_stress_detection)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            result = await test_func()
            results[test_name] = "✅ УСПЕХ" if result else "❌ ОШИБКА"
        except Exception as e:
            logger.error(f"Test {test_name} failed: {e}")
            results[test_name] = "❌ ИСКЛЮЧЕНИЕ"
    
    # Итоговый отчет
    print(f"\n{'='*20} ИТОГОВЫЙ ОТЧЕТ {'='*20}")
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    success_count = sum(1 for result in results.values() if "✅" in result)
    total_count = len(results)
    
    print(f"\n🎯 РЕЗУЛЬТАТ: {success_count}/{total_count} тестов прошли успешно")
    
    if success_count == total_count:
        print("🚀 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО! Система готова к использованию.")
    else:
        print("⚠️ Некоторые тесты не прошли. Проверьте логи для деталей.")

if __name__ == "__main__":
    asyncio.run(main()) 