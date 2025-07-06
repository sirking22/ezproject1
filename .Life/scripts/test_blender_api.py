#!/usr/bin/env python3
"""
Тест Blender API генератора
Проверяет интеграцию с системой управления жизнью
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем путь к src
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from integrations.blender_integration import BlenderIntegration

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_blender_availability():
    """Тест доступности Blender API"""
    logger.info("🧪 Тест 1: Проверка доступности Blender API")
    
    blender = BlenderIntegration()
    status = blender.get_status()
    
    logger.info(f"📊 Статус Blender: {status}")
    
    if status['available']:
        logger.info("✅ Blender API доступен")
        return True
    else:
        logger.warning("⚠️ Blender API недоступен")
        logger.info("💡 Убедитесь, что Blender установлен и доступен в PATH")
        return False

def test_organic_lamp_generation():
    """Тест генерации органической лампы"""
    logger.info("\n🧪 Тест 2: Генерация органической лампы")
    
    blender = BlenderIntegration()
    
    if not blender.is_available():
        logger.warning("⚠️ Пропуск теста - Blender недоступен")
        return False
    
    # Создаем органическую лампу
    result = blender.generate_3d_object({
        'type': 'organic_lamp',
        'base_radius': 80.0,
        'complexity': 1.5
    })
    
    if result['success']:
        logger.info(f"✅ Органическая лампа создана: {result['filepath']}")
        logger.info(f"📸 Превью: {result['preview_path']}")
        logger.info(f"📊 Информация: {result['object_info']}")
        return True
    else:
        logger.error(f"❌ Ошибка создания лампы: {result['error']}")
        return False

def test_precise_objects():
    """Тест создания точных объектов"""
    logger.info("\n🧪 Тест 3: Создание точных объектов")
    
    blender = BlenderIntegration()
    
    if not blender.is_available():
        logger.warning("⚠️ Пропуск теста - Blender недоступен")
        return False
    
    # Тест куба
    logger.info("📦 Создание точного куба...")
    cube_result = blender.create_precise_object(
        object_type='cube',
        dimensions={'width': 100, 'height': 100, 'depth': 100},
        name='TestCube'
    )
    
    if cube_result['success']:
        logger.info(f"✅ Куб создан: {cube_result['filepath']}")
    else:
        logger.error(f"❌ Ошибка создания куба: {cube_result['error']}")
    
    # Тест цилиндра
    logger.info("🔵 Создание точного цилиндра...")
    cylinder_result = blender.create_precise_object(
        object_type='cylinder',
        dimensions={'radius': 50, 'height': 100},
        name='TestCylinder'
    )
    
    if cylinder_result['success']:
        logger.info(f"✅ Цилиндр создан: {cylinder_result['filepath']}")
    else:
        logger.error(f"❌ Ошибка создания цилиндра: {cylinder_result['error']}")
    
    # Тест сферы
    logger.info("⚪ Создание точной сферы...")
    sphere_result = blender.create_precise_object(
        object_type='sphere',
        dimensions={'radius': 40},
        name='TestSphere'
    )
    
    if sphere_result['success']:
        logger.info(f"✅ Сфера создана: {sphere_result['filepath']}")
    else:
        logger.error(f"❌ Ошибка создания сферы: {sphere_result['error']}")
    
    return all([
        cube_result['success'],
        cylinder_result['success'],
        sphere_result['success']
    ])

def test_batch_generation():
    """Тест пакетной генерации"""
    logger.info("\n🧪 Тест 4: Пакетная генерация")
    
    blender = BlenderIntegration()
    
    if not blender.is_available():
        logger.warning("⚠️ Пропуск теста - Blender недоступен")
        return False
    
    # Данные для пакетной генерации
    batch_data = [
        {
            'type': 'cube',
            'dimensions': {'width': 50, 'height': 50, 'depth': 50},
            'name': 'SmallCube'
        },
        {
            'type': 'sphere',
            'dimensions': {'radius': 30},
            'name': 'TestSphere'
        },
        {
            'type': 'organic_lamp',
            'base_radius': 40.0,
            'complexity': 0.8
        }
    ]
    
    logger.info(f"🔄 Запуск пакетной генерации {len(batch_data)} объектов...")
    results = blender.batch_generate(batch_data)
    
    success_count = sum(1 for r in results if r['success'])
    logger.info(f"✅ Пакетная генерация завершена: {success_count}/{len(results)} успешно")
    
    for i, result in enumerate(results):
        if result['success']:
            logger.info(f"  ✅ Объект {i+1}: {result.get('filepath', 'N/A')}")
        else:
            logger.error(f"  ❌ Объект {i+1}: {result['error']}")
    
    return success_count == len(results)

def test_integration_with_existing_system():
    """Тест интеграции с существующей системой"""
    logger.info("\n🧪 Тест 5: Интеграция с существующей системой")
    
    try:
        # Импортируем основную систему
        from core.life_management_system import LifeManagementSystem
        
        lms = LifeManagementSystem()
        
        # Проверяем, есть ли Blender интеграция
        if hasattr(lms, 'blender_integration'):
            logger.info("✅ Blender интеграция найдена в основной системе")
            
            # Тестируем генерацию через основную систему
            result = lms.generate_3d_object({
                'type': 'organic_lamp',
                'base_radius': 60.0,
                'complexity': 1.0
            })
            
            if result['success']:
                logger.info(f"✅ Генерация через основную систему: {result['filepath']}")
                return True
            else:
                logger.error(f"❌ Ошибка генерации через основную систему: {result['error']}")
                return False
        else:
            logger.warning("⚠️ Blender интеграция не найдена в основной системе")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта основной системы: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования интеграции: {e}")
        return False

def main():
    """Основная функция тестирования"""
    logger.info("🚀 Запуск тестирования Blender API интеграции")
    logger.info("=" * 60)
    
    # Счетчики результатов
    total_tests = 5
    passed_tests = 0
    
    # Тест 1: Доступность
    if test_blender_availability():
        passed_tests += 1
    
    # Тест 2: Органическая лампа
    if test_organic_lamp_generation():
        passed_tests += 1
    
    # Тест 3: Точные объекты
    if test_precise_objects():
        passed_tests += 1
    
    # Тест 4: Пакетная генерация
    if test_batch_generation():
        passed_tests += 1
    
    # Тест 5: Интеграция
    if test_integration_with_existing_system():
        passed_tests += 1
    
    # Итоговый отчет
    logger.info("\n" + "=" * 60)
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ")
    logger.info(f"✅ Пройдено тестов: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Blender API интеграция работает корректно")
    elif passed_tests > 0:
        logger.info("⚠️ Частично пройдено. Проверьте настройки Blender")
    else:
        logger.error("❌ ВСЕ ТЕСТЫ ПРОВАЛЕНЫ! Проверьте установку Blender")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main() 