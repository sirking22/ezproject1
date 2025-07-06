#!/usr/bin/env python3
"""
Простой тест Blender CLI интеграции
Проверяет доступность Blender и создает тестовый объект
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем путь к src
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from integrations.blender_cli_integration import BlenderCLIIntegration

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_blender_find():
    """Тест поиска Blender"""
    logger.info("🔍 Поиск Blender...")
    
    # Пробуем найти автоматически
    blender = BlenderCLIIntegration()
    status = blender.get_status()
    
    logger.info(f"📊 Статус: {status}")
    
    if status['available']:
        logger.info("✅ Blender найден автоматически!")
        return True
    else:
        logger.warning("⚠️ Blender не найден автоматически")
        
        # Показываем возможные пути
        logger.info("💡 Возможные пути установки:")
        possible_paths = [
            r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender\blender.exe",
            r"C:\Users\{}\AppData\Local\Programs\Blender Foundation\Blender\blender.exe".format(os.getenv('USERNAME', '')),
            r"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe",
            r"C:\blender\blender.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"  ✅ Найден: {path}")
            else:
                logger.info(f"  ❌ Не найден: {path}")
        
        return False

def test_with_custom_path():
    """Тест с указанием пути вручную"""
    logger.info("\n🔧 Тест с указанием пути вручную")
    
    # Попросим пользователя указать путь
    print("\n" + "="*60)
    print("УКАЗАНИЕ ПУТИ К BLENDER")
    print("="*60)
    print("Если Blender не найден автоматически, укажите путь к blender.exe")
    print("Примеры:")
    print("  C:\\Program Files\\Blender Foundation\\Blender\\blender.exe")
    print("  C:\\blender\\blender.exe")
    print("  C:\\Users\\YourName\\AppData\\Local\\Programs\\Blender Foundation\\Blender\\blender.exe")
    print()
    
    custom_path = input("Введите путь к blender.exe (или Enter для пропуска): ").strip()
    
    if not custom_path:
        logger.info("Путь не указан, пропускаем тест")
        return False
    
    if not os.path.exists(custom_path):
        logger.error(f"❌ Файл не найден: {custom_path}")
        return False
    
    logger.info(f"🔧 Тестируем с путем: {custom_path}")
    
    blender = BlenderCLIIntegration(custom_path)
    status = blender.get_status()
    
    logger.info(f"📊 Статус: {status}")
    
    if status['available']:
        logger.info("✅ Blender найден по указанному пути!")
        return True
    else:
        logger.error("❌ Blender не работает по указанному пути")
        return False

def test_simple_cube():
    """Тест создания простого куба"""
    logger.info("\n🧪 Тест создания простого куба")
    
    # Создаем интеграцию
    blender = BlenderCLIIntegration()
    
    if not blender.available:
        logger.warning("⚠️ Пропуск теста - Blender недоступен")
        return False
    
    # Создаем простой куб
    result = blender.create_precise_object(
        object_type='cube',
        dimensions={'width': 100, 'height': 100, 'depth': 100},
        name='TestCube',
        output_dir='test_output'
    )
    
    if result['success']:
        logger.info("✅ Куб создан успешно!")
        logger.info(f"📁 STL файл: {result['stl_file']}")
        logger.info(f"📸 Превью: {result['preview_file']}")
        return True
    else:
        logger.error(f"❌ Ошибка создания куба: {result['error']}")
        if 'stderr' in result:
            logger.error(f"🔍 Детали ошибки: {result['stderr']}")
        return False

def test_organic_lamp():
    """Тест создания органической лампы"""
    logger.info("\n🧪 Тест создания органической лампы")
    
    # Создаем интеграцию
    blender = BlenderCLIIntegration()
    
    if not blender.available:
        logger.warning("⚠️ Пропуск теста - Blender недоступен")
        return False
    
    # Создаем органическую лампу
    result = blender.create_organic_lamp(
        base_radius=80.0,
        complexity=1.2,
        output_dir='test_output'
    )
    
    if result['success']:
        logger.info("✅ Органическая лампа создана успешно!")
        logger.info(f"📁 STL файл: {result['stl_file']}")
        logger.info(f"📸 Превью: {result['preview_file']}")
        return True
    else:
        logger.error(f"❌ Ошибка создания лампы: {result['error']}")
        if 'stderr' in result:
            logger.error(f"🔍 Детали ошибки: {result['stderr']}")
        return False

def main():
    """Основная функция тестирования"""
    logger.info("🚀 Запуск тестирования Blender CLI интеграции")
    logger.info("=" * 60)
    
    # Создаем директорию для тестов
    os.makedirs('test_output', exist_ok=True)
    
    # Счетчики результатов
    total_tests = 4
    passed_tests = 0
    
    # Тест 1: Поиск Blender
    if test_blender_find():
        passed_tests += 1
    
    # Тест 2: Ручное указание пути
    if test_with_custom_path():
        passed_tests += 1
    
    # Тест 3: Простой куб
    if test_simple_cube():
        passed_tests += 1
    
    # Тест 4: Органическая лампа
    if test_organic_lamp():
        passed_tests += 1
    
    # Итоговый отчет
    logger.info("\n" + "=" * 60)
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ")
    logger.info(f"✅ Пройдено тестов: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Blender CLI интеграция работает корректно")
    elif passed_tests > 0:
        logger.info("⚠️ Частично пройдено. Проверьте настройки Blender")
    else:
        logger.error("❌ ВСЕ ТЕСТЫ ПРОВАЛЕНЫ! Проверьте установку Blender")
    
    logger.info("=" * 60)
    
    # Инструкции
    if passed_tests == 0:
        print("\n" + "="*60)
        print("ИНСТРУКЦИИ ПО УСТАНОВКЕ BLENDER")
        print("="*60)
        print("1. Скачайте Blender с официального сайта: https://www.blender.org/download/")
        print("2. Установите Blender в стандартную директорию")
        print("3. Убедитесь, что blender.exe доступен в PATH или укажите путь вручную")
        print("4. Запустите тест снова")
        print("="*60)

if __name__ == "__main__":
    main() 