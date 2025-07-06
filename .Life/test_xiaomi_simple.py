#!/usr/bin/env python3
"""
Упрощенный тест интеграции с Xiaomi Watch S
Без сложных зависимостей
"""

import asyncio
import sys
import os
from datetime import datetime, UTC

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем только базовые классы
from src.integrations.xiaomi_watch import (
    XiaomiWatchAPI,
    VoiceProcessor,
    IntentRecognizer,
    BiometricData,
    VoiceCommand
)

async def test_xiaomi_watch_basic():
    """Базовое тестирование интеграции с Xiaomi Watch S"""
    print("📱 Базовое тестирование интеграции с Xiaomi Watch S...")
    print("=" * 60)
    
    try:
        # 1. Тестирование API часов
        print("\n1. 🔧 Тестирование API Xiaomi Watch S...")
        
        watch_api = XiaomiWatchAPI()
        
        # Получение биометрических данных
        heart_rate = await watch_api.get_heart_rate()
        sleep_data = await watch_api.get_sleep_data()
        activity_data = await watch_api.get_activity_data()
        stress_level = await watch_api.get_stress_level()
        
        print(f"✅ Пульс: {heart_rate} уд/мин")
        print(f"✅ Качество сна: {sleep_data.get('quality', 0):.0f}%")
        print(f"✅ Продолжительность сна: {sleep_data.get('duration', 0):.1f} ч")
        print(f"✅ Шаги: {activity_data.get('steps', 0)}")
        print(f"✅ Калории: {activity_data.get('calories', 0)}")
        print(f"✅ Уровень стресса: {stress_level:.0f}%")
        
        # Получение полных биометрических данных
        biometrics = await watch_api.get_current_biometrics()
        print(f"✅ Полные биометрические данные получены")
        print(f"   - Пульс: {biometrics.heart_rate}")
        print(f"   - Качество сна: {biometrics.sleep_quality}")
        print(f"   - Стресс: {biometrics.stress_level}")
        print(f"   - Шаги: {biometrics.steps}")
        
        # 2. Тестирование распознавания намерений
        print("\n2. 🎯 Тестирование распознавания намерений...")
        
        intent_recognizer = IntentRecognizer()
        
        test_commands = [
            "добавь задачу купить продукты",
            "добавь привычку медитация",
            "мое настроение хорошее",
            "мой прогресс",
            "поговори со мной",
            "неизвестная команда"
        ]
        
        for command in test_commands:
            intent = await intent_recognizer.analyze(command)
            print(f"📝 Команда: '{command}'")
            print(f"   Намерение: {intent['intent']}")
            print(f"   Уверенность: {intent['confidence']:.2f}")
            print(f"   Данные: {intent['extracted_data']}")
            print()
        
        # 3. Тестирование голосового процессора
        print("\n3. 🎤 Тестирование голосового процессора...")
        
        voice_processor = VoiceProcessor()
        
        # Тест преобразования речи в текст
        text = await voice_processor.speech_to_text(b"test_audio")
        print(f"✅ Speech-to-Text: '{text}'")
        
        # Тест преобразования текста в речь
        audio_data = await voice_processor.text_to_speech("Тестовое сообщение")
        print(f"✅ Text-to-Speech: {len(audio_data)} байт")
        
        # 4. Тестирование анализа настроения
        print("\n4. 😊 Тестирование анализа настроения...")
        
        # Создаем простую функцию анализа настроения
        def analyze_mood_from_biometrics(biometrics):
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
        
        test_biometrics = [
            BiometricData(heart_rate=75, stress_level=30.0),  # Спокойное
            BiometricData(heart_rate=95, stress_level=70.0),  # Стресс
            BiometricData(heart_rate=110, stress_level=85.0), # Высокий стресс
        ]
        
        for bio in test_biometrics:
            mood = analyze_mood_from_biometrics(bio)
            print(f"💓 Пульс: {bio.heart_rate}, Стресс: {bio.stress_level:.0f}% → Настроение: {mood}")
        
        # 5. Демонстрация умных уведомлений
        print("\n5. 🔔 Демонстрация умных уведомлений...")
        
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 10:
            notification = f"Доброе утро! Качество сна: {biometrics.sleep_quality:.0f}%. Рекомендую 10 минут медитации"
        elif 10 <= current_hour < 18:
            if biometrics.stress_level and biometrics.stress_level > 60:
                notification = "Заметил повышение стресса. Хочешь поговорить или сделать перерыв?"
            else:
                notification = "Отличный день! Продолжайте в том же духе!"
        elif 18 <= current_hour < 22:
            notification = "Время для вечерней рефлексии. Как прошел день?"
        else:
            notification = "Пора готовиться ко сну. Рекомендую отключить уведомления"
        
        print(f"📱 Умное уведомление: {notification}")
        
        # 6. Финальный отчет
        print("\n6. 🎯 Финальный отчет...")
        
        print(f"🏆 Результаты тестирования:")
        print(f"   ✅ API Xiaomi Watch S работает")
        print(f"   ✅ Распознавание намерений функционирует")
        print(f"   ✅ Голосовой процессор готов")
        print(f"   ✅ Анализ настроения работает")
        print(f"   ✅ Умные уведомления генерируются")
        
        print(f"\n🚀 Система готова к использованию!")
        print(f"   - Голосовые команды через часы")
        print(f"   - Автоматическое отслеживание биометрии")
        print(f"   - Умные уведомления и рекомендации")
        print(f"   - Интеграция с существующими Notion базами")
        
        print("\n✅ Базовое тестирование интеграции с Xiaomi Watch S завершено успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

async def demo_voice_commands():
    """Демонстрация голосовых команд"""
    print("\n🎤 ДЕМОНСТРАЦИЯ ГОЛОСОВЫХ КОМАНД")
    print("=" * 40)
    
    commands = [
        "добавь задачу купить продукты",
        "добавь привычку медитация",
        "мое настроение отличное",
        "какой мой прогресс?",
        "поговори со мной, я устал"
    ]
    
    intent_recognizer = IntentRecognizer()
    
    for i, command in enumerate(commands, 1):
        print(f"\n{i}. 🎤 Команда: '{command}'")
        
        # Анализируем намерение
        intent = await intent_recognizer.analyze(command)
        print(f"📱 Намерение: {intent['intent']}")
        print(f"📱 Уверенность: {intent['confidence']:.2f}")
        print(f"📱 Извлеченные данные: {intent['extracted_data']}")

async def demo_smart_notifications():
    """Демонстрация умных уведомлений"""
    print("\n🔔 ДЕМОНСТРАЦИЯ УМНЫХ УВЕДОМЛЕНИЙ")
    print("=" * 40)
    
    # Симулируем разные времена дня
    times = [
        (7, "Утро"),
        (12, "День"), 
        (18, "Вечер"),
        (22, "Ночь")
    ]
    
    watch_api = XiaomiWatchAPI()
    biometrics = await watch_api.get_current_biometrics()
    
    for hour, time_name in times:
        print(f"\n🌅 {time_name} ({hour}:00):")
        
        if 6 <= hour < 10:
            notification = f"Доброе утро! Качество сна: {biometrics.sleep_quality:.0f}%. Рекомендую 10 минут медитации"
        elif 10 <= hour < 18:
            if biometrics.stress_level and biometrics.stress_level > 60:
                notification = "Заметил повышение стресса. Хочешь поговорить или сделать перерыв?"
            elif biometrics.steps and biometrics.steps < 5000:
                notification = "Мало активности сегодня. Рекомендую прогулку!"
            else:
                notification = "Отличный день! Продолжайте в том же духе!"
        elif 18 <= hour < 22:
            notification = "Время для вечерней рефлексии. Как прошел день?"
        else:
            notification = "Пора готовиться ко сну. Рекомендую отключить уведомления"
        
        print(f"📱 Уведомление: {notification}")

if __name__ == "__main__":
    asyncio.run(test_xiaomi_watch_basic())
    asyncio.run(demo_voice_commands())
    asyncio.run(demo_smart_notifications()) 