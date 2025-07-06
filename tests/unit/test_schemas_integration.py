"""
Тест интеграции с централизованными схемами баз данных
Проверяет корректность работы с notion_database_schemas.py
"""

import os
import json
from notion_database_schemas import (
    get_database_schema,
    get_all_schemas,
    get_database_id,
    get_status_options,
    get_select_options,
    get_multi_select_options,
    get_relations,
    validate_property_value
)

def test_schema_retrieval():
    """Тест получения схем баз данных"""
    print("🔍 Тест получения схем баз данных")
    
    databases = ["tasks", "subtasks", "projects", "ideas", "materials", "kpi", "epics", "guides", "superguide", "marketing", "smm"]
    
    for db_name in databases:
        schema = get_database_schema(db_name)
        if schema:
            print(f"✅ {db_name}: {schema.name} (ID: {schema.database_id})")
        else:
            print(f"❌ {db_name}: схема не найдена")
    
    print()

def test_database_ids():
    """Тест получения ID баз данных"""
    print("🆔 Тест получения ID баз данных")
    
    expected_ids = {
        "tasks": "d09df250ce7e4e0d9fbe4e036d320def",
        "subtasks": "9c5f4269d61449b6a7485579a3c21da3",
        "projects": "342f18c67a5e41fead73dcec00770f4e",
        "ideas": "ad92a6e21485428c84de8587706b3be1",
        "materials": "1d9ace03d9ff804191a4d35aeedcbbd4",
        "kpi": "1d6ace03d9ff80bfb809ed21dfd2150c",
        "epics": "6fc4322e6d0c45a6b37ac49b818a063a",
        "guides": "47c6086858d442ebaeceb4fad1b23ba3",
        "superguide": "3e6a5838b4044a87a8433c3664995c5b",
        "marketing": "231b91aa-831d-470c-9dda-a3dd45037594",
        "smm": "65a90504-cb5b-4a08-a721-e91df3c57d82"
    }
    
    for db_name, expected_id in expected_ids.items():
        actual_id = get_database_id(db_name)
        if actual_id == expected_id:
            print(f"✅ {db_name}: {actual_id}")
        else:
            print(f"❌ {db_name}: ожидалось {expected_id}, получено {actual_id}")
    
    print()

def test_status_options():
    """Тест получения вариантов статусов"""
    print("📊 Тест получения вариантов статусов")
    
    test_cases = [
        ("tasks", "Статус", ["To do", "In Progress", "Done", "Backlog", "Regular"]),
        ("subtasks", " Статус", ["needs review", "in progress", "complete", "To do", "In progress"]),
        ("projects", "Статус", ["Regular", "Backlog", "Paused", "Planning", "In Progress", "Review", "In Production", "Done", "Canceled", "Archived"]),
        ("ideas", "Статус", ["To do", "Обсудить", "In progress", "+\\-", "Ок", "Архив"]),
        ("materials", "Статус", ["Backlog", "To do", "In progress", "+\\-", "К релизу", "Ок", "Сторонние", "Архив"])
    ]
    
    for db_name, property_name, expected_options in test_cases:
        actual_options = get_status_options(db_name, property_name)
        if actual_options == expected_options:
            print(f"✅ {db_name}.{property_name}: {len(actual_options)} вариантов")
        else:
            print(f"❌ {db_name}.{property_name}: несоответствие")
            print(f"   Ожидалось: {expected_options}")
            print(f"   Получено: {actual_options}")
    
    print()

def test_select_options():
    """Тест получения вариантов выбора"""
    print("🎯 Тест получения вариантов выбора")
    
    test_cases = [
        ("tasks", "! Задачи", ["!!!", "!!", "!", ".", "тест"]),
        ("subtasks", "Приоритет", ["!!!", "!!", "!", ".", ">>", ">", "Средний"]),
        ("projects", "Приоритет", ["!!!", "!!", "!", "."]),
        ("ideas", "Формат", ["Идея", "Совет", "Best Practice", "Статья", "Видео"]),
        ("kpi", "Тип KPI", ["% выполнено", "Охват", "Вовлечённость", "Количество", "Среднее значение"])
    ]
    
    for db_name, property_name, expected_options in test_cases:
        actual_options = get_select_options(db_name, property_name)
        if actual_options == expected_options:
            print(f"✅ {db_name}.{property_name}: {len(actual_options)} вариантов")
        else:
            print(f"❌ {db_name}.{property_name}: несоответствие")
    
    print()

def test_multi_select_options():
    """Тест получения вариантов множественного выбора"""
    print("🏷️ Тест получения вариантов множественного выбора")
    
    test_cases = [
        ("tasks", "Категория", ["Полиграфия", "Маркет", "Видео", "Активности", "Веб", "Бренд", "Копирайт", "SMM", "Фото", "Дизайн", "Стратегия", "Орг", "Материалы", "Аналитика", "Полиграфия товаров"]),
        ("subtasks", "Направление", ["Продукт", "Бренд", "Маркет", "Соц сети", "Видео", "Фото", "Дизайн", "Веб", "Стратегия", "Аналитика", "Копирайт", "Орг"]),
        ("projects", " Теги", ["Полиграфия товаров", "Полиграфия", "Маркет", "Бренд", "Веб", "SMM", "Видео", "Фото", "Орг", "Активности", "Копирайт", "Дизайн", "Стратегия", "Материалы"])
    ]
    
    for db_name, property_name, expected_options in test_cases:
        actual_options = get_multi_select_options(db_name, property_name)
        if actual_options == expected_options:
            print(f"✅ {db_name}.{property_name}: {len(actual_options)} вариантов")
        else:
            print(f"❌ {db_name}.{property_name}: несоответствие")
    
    print()

def test_validation():
    """Тест валидации значений"""
    print("✅ Тест валидации значений")
    
    test_cases = [
        ("tasks", "Статус", "To do", True),
        ("tasks", "Статус", "Invalid Status", False),
        ("subtasks", "Приоритет", "!!!", True),
        ("subtasks", "Приоритет", "Invalid Priority", False),
        ("ideas", "Формат", "Идея", True),
        ("ideas", "Формат", "Invalid Format", False)
    ]
    
    for db_name, property_name, value, expected_valid in test_cases:
        actual_valid = validate_property_value(db_name, property_name, value)
        if actual_valid == expected_valid:
            print(f"✅ {db_name}.{property_name} = '{value}': {'корректно' if actual_valid else 'некорректно'}")
        else:
            print(f"❌ {db_name}.{property_name} = '{value}': ожидалось {expected_valid}, получено {actual_valid}")
    
    print()

def test_relations():
    """Тест получения связей"""
    print("🔗 Тест получения связей")
    
    test_cases = [
        ("tasks", {"Проект": "342f18c67a5e41fead73dcec00770f4e", "Под задачи": "9c5f4269d61449b6a7485579a3c21da3", "Материалы": "1d9ace03d9ff804191a4d35aeedcbbd4"}),
        ("subtasks", {"Задачи": "d09df250ce7e4e0d9fbe4e036d320def"}),
        ("projects", {"Эпик": "6fc4322e6d0c45a6b37ac49b818a063a", "Дизайн": "d09df250ce7e4e0d9fbe4e036d320def", "СММ": "65a90504-cb5b-4a08-a721-e91df3c57d82", "Маркет": "231b91aa-831d-470c-9dda-a3dd45037594"})
    ]
    
    for db_name, expected_relations in test_cases:
        actual_relations = get_relations(db_name)
        if actual_relations == expected_relations:
            print(f"✅ {db_name}: {len(actual_relations)} связей")
        else:
            print(f"❌ {db_name}: несоответствие связей")
    
    print()

def generate_schema_documentation():
    """Генерация документации схем"""
    print("📚 Генерация документации схем")
    
    all_schemas = get_all_schemas()
    
    documentation = {
        "title": "Централизованные схемы баз данных Notion",
        "description": "Единственный источник истины для всех параметров, статусов, тегов и связей",
        "databases": {}
    }
    
    for db_name, schema in all_schemas.items():
        doc = {
            "name": schema.name,
            "database_id": schema.database_id,
            "description": schema.description,
            "properties": schema.properties,
            "status_options": schema.status_options,
            "select_options": schema.select_options,
            "multi_select_options": schema.multi_select_options,
            "relations": schema.relations
        }
        documentation["databases"][db_name] = doc
    
    # Сохранение документации
    with open("notion_schemas_documentation.json", "w", encoding="utf-8") as f:
        json.dump(documentation, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Документация сохранена в notion_schemas_documentation.json")
    print()

def main():
    """Главная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ ЦЕНТРАЛИЗОВАННЫХ СХЕМ БАЗ ДАННЫХ")
    print("=" * 60)
    
    # Проверка переменных окружения
    if not os.getenv("NOTION_TOKEN"):
        print("❌ NOTION_TOKEN не найден в переменных окружения")
        return
    
    # Запуск тестов
    test_schema_retrieval()
    test_database_ids()
    test_status_options()
    test_select_options()
    test_multi_select_options()
    test_validation()
    test_relations()
    generate_schema_documentation()
    
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    main() 