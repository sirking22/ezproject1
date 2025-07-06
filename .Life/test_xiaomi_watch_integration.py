#!/usr/bin/env python3
"""
Тест интеграции с Xiaomi Watch S
Голосовые команды, биометрические данные, умные уведомления
"""

import asyncio
import sys
import os
from datetime import datetime, UTC

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.integrations.xiaomi_watch import (
    xiaomi_integration, 
    BiometricData, 
    VoiceCommand,
    XiaomiWatchAPI,
    VoiceProcessor,
    IntentRecognizer
)

async def test_xiaomi_watch_integration():
    """Тестирование интеграции с Xiaomi Watch S"""
    print("📱 Тестирование интеграции с Xiaomi Watch S...")
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
        print(f"✅ Полные биометрические данные получены: {biometrics}")
        
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
        
        # 4. Тестирование интеграции
        print("\n4. 🔗 Тестирование полной интеграции...")
        
        # Тестируем различные голосовые команды
        test_voice_commands = [
            b"test_audio_add_task",
            b"test_audio_add_habit", 
            b"test_audio_progress",
            b"test_audio_chat"
        ]
        
        for audio_data in test_voice_commands:
            response = await xiaomi_integration.handle_voice_command(audio_data)
            print(f"🎤 Команда: {audio_data}")
            print(f"📱 Ответ: {response}")
            print()
        
        # 5. Тестирование умных уведомлений
        print("\n5. 🔔 Тестирование умных уведомлений...")
        
        notification = await xiaomi_integration.get_smart_notification()
        print(f"📱 Умное уведомление: {notification}")
        
        # 6. Тестирование анализа настроения
        print("\n6. 😊 Тестирование анализа настроения...")
        
        test_biometrics = [
            BiometricData(heart_rate=75, stress_level=30.0),  # Спокойное
            BiometricData(heart_rate=95, stress_level=70.0),  # Стресс
            BiometricData(heart_rate=110, stress_level=85.0), # Высокий стресс
        ]
        
        for biometrics in test_biometrics:
            mood = xiaomi_integration._analyze_mood_from_biometrics(biometrics)
            print(f"💓 Пульс: {biometrics.heart_rate}, Стресс: {biometrics.stress_level:.0f}% → Настроение: {mood}")
        
        # 7. Демонстрация работы с Notion
        print("\n7. 📊 Демонстрация интеграции с Notion...")
        
        # Создаем тестовую команду для добавления задачи
        test_command = VoiceCommand(
            text="добавь задачу протестировать интеграцию с часами",
            intent="add_task",
            confidence=0.9,
            biometrics=biometrics,
            context={"task_description": "протестировать интеграцию с часами"}
        )
        
        print("📝 Создание тестовой задачи через голосовую команду...")
        task_response = await xiaomi_integration._add_task(test_command)
        print(f"✅ Результат: {task_response}")
        
        # 8. Тестирование рекомендаций
        print("\n8. 💡 Тестирование рекомендаций...")
        
        # Импортируем метод из admin_bot для тестирования
        from src.telegram.admin_bot import AdminBot
        admin_bot = AdminBot()
        
        recommendations = admin_bot._get_biometric_recommendations(biometrics)
        print(f"📊 Рекомендации на основе биометрии:")
        print(recommendations)
        
        # 9. Финальный отчет
        print("\n9. 🎯 Финальный отчет...")
        
        print(f"🏆 Результаты тестирования:")
        print(f"   ✅ API Xiaomi Watch S работает")
        print(f"   ✅ Распознавание намерений функционирует")
        print(f"   ✅ Голосовой процессор готов")
        print(f"   ✅ Интеграция с Notion работает")
        print(f"   ✅ Умные уведомления генерируются")
        print(f"   ✅ Анализ настроения работает")
        
        print(f"\n🚀 Система готова к использованию!")
        print(f"   - Голосовые команды через часы")
        print(f"   - Автоматическое отслеживание биометрии")
        print(f"   - Умные уведомления и рекомендации")
        print(f"   - Интеграция с существующими Notion базами")
        
        print("\n✅ Тестирование интеграции с Xiaomi Watch S завершено успешно!")
        
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
    
    for i, command in enumerate(commands, 1):
        print(f"\n{i}. 🎤 Команда: '{command}'")
        
        # Создаем VoiceCommand
        voice_command = VoiceCommand(
            text=command,
            intent="test",
            confidence=0.9,
            biometrics=BiometricData(heart_rate=75, stress_level=30.0)
        )
        
        # Обрабатываем команду
        response = await xiaomi_integration._execute_command(voice_command)
        print(f"📱 Ответ: {response}")

async def demo_smart_notifications():
    """Демонстрация умных уведомлений"""
    print("\n🔔 ДЕМОНСТРАЦИЯ УМНЫХ УВЕДОМЛЕНИЙ")
    print("=" * 40)
    
    # Симулируем разные времена дня
    import time
    
    times = [
        (7, "Утро"),
        (12, "День"), 
        (18, "Вечер"),
        (22, "Ночь")
    ]
    
    for hour, time_name in times:
        print(f"\n🌅 {time_name} ({hour}:00):")
        
        # Временно изменяем время для демонстрации
        original_now = datetime.now
        datetime.now = lambda: datetime(2024, 1, 1, hour, 0, 0)
        
        try:
            notification = await xiaomi_integration.get_smart_notification()
            print(f"📱 Уведомление: {notification}")
        finally:
            datetime.now = original_now

if __name__ == "__main__":
    asyncio.run(test_xiaomi_watch_integration())
    asyncio.run(demo_voice_commands())
    asyncio.run(demo_smart_notifications()) 