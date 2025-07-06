#!/usr/bin/env python3
"""
🚨 БЫСТРЫЙ ЧЕК-ЛИСТ ДЛЯ ПРОВЕРКИ СТРУКТУРЫ ДАННЫХ
Используется перед любым анализом Notion баз
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_data_structure():
    """Проверка структуры данных перед анализом"""
    
    print("🔍 БЫСТРАЯ ПРОВЕРКА СТРУКТУРЫ ДАННЫХ")
    print("=" * 50)
    
    # Проверяем переменные окружения
    print("\n📋 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:")
    env_vars = {
        "NOTION_TOKEN": os.getenv("NOTION_TOKEN"),
        "NOTION_DESIGN_TASKS_DB_ID": os.getenv("NOTION_DESIGN_TASKS_DB_ID"),
        "NOTION_SUBTASKS_DB_ID": os.getenv("NOTION_SUBTASKS_DB_ID"),
        "NOTION_PROJECTS_DB_ID": os.getenv("NOTION_PROJECTS_DB_ID"),
        "NOTION_MATERIALS_DB_ID": os.getenv("NOTION_MATERIALS_DB_ID"),
        "NOTION_IDEAS_DB_ID": os.getenv("NOTION_IDEAS_DB_ID"),
    }
    
    for var, value in env_vars.items():
        status = "✅" if value else "❌"
        print(f"   {status} {var}: {value[:20] if value else 'НЕ НАЙДЕН'}")
    
    # Проверяем правильные ID
    print("\n🎯 ПРАВИЛЬНЫЕ ID БАЗ:")
    correct_ids = {
        "Задачи (TASKS)": "d09df250ce7e4e0d9fbe4e036d320def",
        "Подзадачи (SUBTASKS)": "9c5f4269d61449b6a7485579a3c21da3",
        "Проекты (PROJECTS)": "342f18c67a5e41fead73dcec00770f4e",
        "Материалы (MATERIALS)": "1d9ace03d9ff804191a4d35aeedcbbd4",
        "Идеи (IDEAS)": "ad92a6e21485428c84de8587706b3be1",
    }
    
    for name, correct_id in correct_ids.items():
        env_id = env_vars.get(f"NOTION_{name.split()[0].upper()}_DB_ID")
        status = "✅" if env_id == correct_id else "❌"
        print(f"   {status} {name}: {correct_id}")
        if env_id != correct_id:
            print(f"      ⚠️  Ожидалось: {correct_id}")
            print(f"      ⚠️  Получено: {env_id}")
    
    # Чек-лист перед анализом
    print("\n🔧 ЧЕК-ЛИСТ ПЕРЕД АНАЛИЗОМ:")
    checklist = [
        "Проверить ID базы данных",
        "Убедиться, что анализирую правильную иерархию",
        "Использовать MCP сервер вместо сырого API",
        "Проверить названия полей в базе",
        "Документировать результаты в ERRORS_SOLUTIONS.md"
    ]
    
    for i, item in enumerate(checklist, 1):
        print(f"   {i}. {item}")
    
    # Критические правила
    print("\n🚨 КРИТИЧЕСКИЕ ПРАВИЛА:")
    rules = [
        "ВСЕГДА использовать MCP сервер вместо сырых API",
        "ВСЕГДА проверять ID базы данных перед анализом",
        "ВСЕГДА понимать иерархию: Проекты → Задачи → Подзадачи",
        "НЕ ПУТАТЬ задачи и подзадачи - это разные базы!",
        "Использовать правильные поля: 'Задача' vs 'Подзадачи'"
    ]
    
    for rule in rules:
        print(f"   ⚠️  {rule}")
    
    # Полезные команды
    print("\n💡 ПОЛЕЗНЫЕ КОМАНДЫ:")
    commands = [
        "python correct_tasks_analysis.py  # Анализ задач через MCP",
        "python final_todo_count.py        # Подсчет ToDo задач",
        "python quick_data_check.py        # Эта проверка"
    ]
    
    for cmd in commands:
        print(f"   $ {cmd}")
    
    print("\n✅ Проверка завершена!")
    print("📖 Подробности в docs/DATA_STRUCTURE_GUIDE.md")

if __name__ == "__main__":
    check_data_structure() 