#!/usr/bin/env python3
"""
Тест реального Xiaomi API
"""

import asyncio
import logging
from datetime import datetime, UTC

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_xiaomi_real_api():
    """Тестирование реального Xiaomi API"""
    print("📱 Тестирование реального Xiaomi API...")
    print("=" * 60)
    
    try:
        # Инициализация API (замените на реальные данные)
        email = "your_email@example.com"  # Замените на реальный email
        password = "your_password"        # Замените на реальный пароль
        
        print(f"🔐 Попытка аутентификации с email: {email}")
        
        # Импортируем функцию инициализации
        from src.integrations.xiaomi_real_api import init_xiaomi_real_api
        
        # Инициализируем API
        api = await init_xiaomi_real_api(email, password, "RU")
        
        if not api:
            print("❌ Не удалось инициализировать API")
            print("💡 Возможные причины:")
            print("   - Неверные учетные данные")
            print("   - Проблемы с сетью")
            print("   - API недоступен")
            print("   - Требуется двухфакторная аутентификация")
            return
        
        print("✅ API инициализирован успешно!")
        
        # Тестируем получение биометрических данных
        print("\n📊 Получение биометрических данных...")
        
        biometrics = await api.get_current_biometrics()
        
        print(f"✅ Биометрические данные получены:")
        print(f"   - Пульс: {biometrics.heart_rate} уд/мин")
        print(f"   - Качество сна: {biometrics.sleep_quality:.0f}%")
        print(f"   - Продолжительность сна: {biometrics.sleep_duration:.1f} ч")
        print(f"   - Уровень стресса: {biometrics.stress_level:.0f}%")
        print(f"   - Шаги: {biometrics.steps}")
        print(f"   - Калории: {biometrics.calories}")
        print(f"   - Расстояние: {biometrics.distance:.1f} км")
        print(f"   - Активные минуты: {biometrics.active_minutes}")
        
        # Закрываем сессию
        await api.close()
        
        print("\n🎉 Тестирование завершено успешно!")
        print("✅ Реальный Xiaomi API работает корректно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        print(f"❌ Ошибка: {e}")

async def test_with_mock_data():
    """Тест с моковыми данными для демонстрации"""
    print("\n🎭 Тест с моковыми данными...")
    print("=" * 60)
    
    try:
        # Создаем моковые данные
        from src.integrations.xiaomi_watch import BiometricData
        
        mock_biometrics = BiometricData(
            heart_rate=75,
            sleep_quality=85.0,
            sleep_duration=7.5,
            stress_level=30.0,
            activity_level=0.75,
            steps=8500,
            calories=450
        )
        
        print(f"✅ Моковые биометрические данные:")
        print(f"   - Пульс: {mock_biometrics.heart_rate} уд/мин")
        print(f"   - Качество сна: {mock_biometrics.sleep_quality:.0f}%")
        print(f"   - Продолжительность сна: {mock_biometrics.sleep_duration:.1f} ч")
        print(f"   - Уровень стресса: {mock_biometrics.stress_level:.0f}%")
        print(f"   - Шаги: {mock_biometrics.steps}")
        print(f"   - Калории: {mock_biometrics.calories}")
        
        print("\n🎉 Моковые данные работают корректно!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования моковых данных: {e}")

async def main():
    """Основная функция"""
    print("🚀 Запуск тестирования Xiaomi API...")
    
    # Тест с реальными данными (закомментируйте, если нет реальных данных)
    # await test_xiaomi_real_api()
    
    # Тест с моковыми данными
    await test_with_mock_data()
    
    print("\n📋 Следующие шаги:")
    print("1. Настройте реальные учетные данные Xiaomi")
    print("2. Убедитесь, что часы синхронизированы с Mi Fit")
    print("3. Запустите тест с реальными данными")
    print("4. Интегрируйте с основной системой")

if __name__ == "__main__":
    asyncio.run(main()) 