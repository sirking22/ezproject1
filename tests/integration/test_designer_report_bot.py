"""
Тестирование системы отчётов дизайнеров
Проверка парсинга, валидации и интеграции с Notion
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

# Добавить корень проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.designer_report_service import service, WorkReport
from config.designer_bot_config import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """Тест конфигурации"""
    print("🔧 Тестирование конфигурации...")
    
    if not config.validate():
        print("❌ Ошибки в конфигурации")
        return False
    
    print("✅ Конфигурация корректна")
    print(f"📋 Базы данных:")
    print(f"  - Задачи: {config.notion.tasks_database_id}")
    print(f"  - Материалы: {config.notion.materials_database_id}")
    print(f"  - Проекты: {config.notion.projects_database_id}")
    
    return True

def test_quick_report_parsing():
    """Тест парсинга быстрых отчётов"""
    print("\n📝 Тестирование парсинга быстрых отчётов...")
    
    test_cases = [
        "Коробки мультиварки RMP04 - верстка 2 часа",
        "Брендинг логотипа 3.5 часа",
        "Дизайн сайта - адаптивка 1.5 часа",
        "RMP04 верстка 2ч",
        "Коробки мультиварки RMP04 - верстка 2 часа + добавил комментарии",
        "Неверный формат отчёта"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Тест: '{text}'")
        
        report = service.parse_quick_report(text)
        
        if report:
            print(f"✅ Парсинг успешен:")
            print(f"   Проект: {report.project_name}")
            print(f"   Задача: {report.task_name}")
            print(f"   Время: {report.time_spent_hours} ч")
            print(f"   Описание: {report.work_description}")
        else:
            print("❌ Парсинг не удался")
    
    return True

def test_report_validation():
    """Тест валидации отчётов"""
    print("\n✅ Тестирование валидации отчётов...")
    
    # Валидный отчёт
    valid_report = WorkReport(
        designer_name="Арсений",
        project_name="Коробки мультиварки RMP04",
        task_name="Верстка",
        work_description="Создал адаптивную верстку",
        time_spent_hours=2.0
    )
    
    is_valid, error_msg = service.validate_report(valid_report)
    print(f"Валидный отчёт: {'✅' if is_valid else '❌'} {error_msg}")
    
    # Невалидный отчёт
    invalid_report = WorkReport(
        designer_name="",
        project_name="",
        task_name="",
        work_description="",
        time_spent_hours=0
    )
    
    is_valid, error_msg = service.validate_report(invalid_report)
    print(f"Невалидный отчёт: {'✅' if is_valid else '❌'} {error_msg}")
    
    return True

def test_notion_integration():
    """Тест интеграции с Notion"""
    print("\n🔗 Тестирование интеграции с Notion...")
    
    try:
        # Получить активные проекты
        projects = service.get_active_projects()
        print(f"✅ Активные проекты ({len(projects)}):")
        for project in projects[:5]:
            print(f"   - {project}")
        
        # Получить задачи для первого проекта
        if projects:
            tasks = service.get_tasks_for_project(projects[0])
            print(f"✅ Задачи для проекта '{projects[0]}' ({len(tasks)}):")
            for task in tasks[:3]:
                print(f"   - {task}")
        
        return True
    
    except Exception as e:
        print(f"❌ Ошибка интеграции с Notion: {e}")
        return False

def test_link_extraction():
    """Тест извлечения ссылок"""
    print("\n🔗 Тестирование извлечения ссылок...")
    
    test_texts = [
        "Создал макет в Figma: https://figma.com/file/abc123",
        "Загрузил файл на Google Drive: https://drive.google.com/file/d/xyz",
        "Сохранил на Яндекс.Диск: https://disk.yandex.ru/d/123",
        "Добавил изображение: image.jpg и видео: video.mp4",
        "Текст без ссылок"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Текст: '{text}'")
        
        links = service.extract_links_from_text(text)
        materials = service.extract_materials_from_text(text)
        
        print(f"   Ссылки: {links}")
        print(f"   Материалы: {materials}")
    
    return True

def test_report_processing():
    """Тест обработки отчёта"""
    print("\n⚙️ Тестирование обработки отчёта...")
    
    # Создать тестовый отчёт
    report = WorkReport(
        designer_name="Арсений",
        project_name="Коробки мультиварки RMP04",
        task_name="Верстка",
        work_description="Создал адаптивную верстку в Figma: https://figma.com/file/abc123",
        time_spent_hours=2.0
    )
    
    print(f"📋 Отчёт:")
    print(f"   Дизайнер: {report.designer_name}")
    print(f"   Проект: {report.project_name}")
    print(f"   Задача: {report.task_name}")
    print(f"   Время: {report.time_spent_hours} ч")
    print(f"   Описание: {report.work_description}")
    
    # Обработать отчёт
    success, message = service.process_report(report)
    
    print(f"\nРезультат обработки: {'✅' if success else '❌'} {message}")
    
    return success

def run_all_tests():
    """Запустить все тесты"""
    print("🧪 ЗАПУСК ТЕСТОВ СИСТЕМЫ ОТЧЁТОВ ДИЗАЙНЕРОВ")
    print("=" * 50)
    
    tests = [
        ("Конфигурация", test_config),
        ("Парсинг быстрых отчётов", test_quick_report_parsing),
        ("Валидация отчётов", test_report_validation),
        ("Интеграция с Notion", test_notion_integration),
        ("Извлечение ссылок", test_link_extraction),
        ("Обработка отчётов", test_report_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчёт
    print(f"\n{'='*50}")
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nРезультат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return True
    else:
        print("⚠️ ЕСТЬ ПРОБЛЕМЫ В СИСТЕМЕ")
        return False

def demo_quick_reports():
    """Демонстрация быстрых отчётов"""
    print("\n🎯 ДЕМОНСТРАЦИЯ БЫСТРЫХ ОТЧЁТОВ")
    print("=" * 40)
    
    examples = [
        "Коробки мультиварки RMP04 - верстка 2 часа",
        "Брендинг логотипа 3.5 часа",
        "Дизайн сайта - адаптивка 1.5 часа",
        "RMP04 верстка 2ч",
        "Коробки мультиварки RMP04 - верстка 2 часа + добавил комментарии к макету"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. Пример: '{example}'")
        
        report = service.parse_quick_report(example)
        
        if report:
            print(f"   📋 Проект: {report.project_name}")
            print(f"   📝 Задача: {report.task_name}")
            print(f"   ⏱️ Время: {report.time_spent_hours} ч")
            print(f"   📄 Описание: {report.work_description}")
            
            # Извлечь ссылки и материалы
            if report.work_description:
                links = service.extract_links_from_text(report.work_description)
                materials = service.extract_materials_from_text(report.work_description)
                
                if links:
                    print(f"   🔗 Ссылки: {links}")
                if materials:
                    print(f"   📎 Материалы: {materials}")
        else:
            print("   ❌ Не удалось распарсить")

if __name__ == "__main__":
    # Проверить переменные окружения
    required_env_vars = ["NOTION_TOKEN", "TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {missing_vars}")
        print("Создайте .env файл с необходимыми токенами")
        sys.exit(1)
    
    # Запустить тесты
    success = run_all_tests()
    
    if success:
        # Показать демонстрацию
        demo_quick_reports()
        
        print("\n🚀 Система готова к использованию!")
        print("Запустите бота: python designer_report_bot.py")
    else:
        print("\n⚠️ Требуется исправление проблем перед запуском") 