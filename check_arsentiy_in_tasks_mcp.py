#!/usr/bin/env python3
"""
Проверка Arsentiy через MCP сервер
Проверяем все задачи и подзадачи на наличие Arsentiy
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_env_vars():
    """Загрузка переменных окружения"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Проверяем критически важные переменные
    required_vars = [
        "NOTION_TOKEN",
        "NOTION_DESIGN_TASKS_DB_ID",  # Tasks Database
        "NOTION_SUBTASKS_DB_ID"       # Subtasks Database
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("Добавьте их в .env файл")
        sys.exit(1)
    
    token = os.getenv("NOTION_TOKEN")
    tasks_db_id = os.getenv("NOTION_DESIGN_TASKS_DB_ID")
    subtasks_db_id = os.getenv("NOTION_SUBTASKS_DB_ID")
    
    if not token or not tasks_db_id or not subtasks_db_id:
        print("❌ Критические переменные окружения не найдены")
        sys.exit(1)
    
    return {
        "token": token,
        "tasks_db_id": tasks_db_id,
        "subtasks_db_id": subtasks_db_id
    }

def check_mcp_server():
    """Проверка MCP сервера"""
    try:
        import mcp
        print("✅ MCP модуль доступен")
        return True
    except ImportError:
        print("❌ MCP модуль не установлен")
        return False

def analyze_tasks_database():
    """Анализ базы задач через MCP"""
    print("\n🔍 АНАЛИЗ TASKS DATABASE ЧЕРЕЗ MCP")
    print("=" * 50)
    
    # Используем MCP сервер для анализа
    try:
        # Импортируем MCP функции
        from notion_mcp_server import analyze_database
        
        # Анализируем Tasks Database
        tasks_db_id = os.getenv("NOTION_DESIGN_TASKS_DB_ID")
        print(f"📊 Анализ базы задач: {tasks_db_id}")
        
        # Получаем все задачи
        result = analyze_database(tasks_db_id)
        
        if result:
            print(f"✅ Найдено {len(result)} задач")
            
            # Ищем Arsentiy в исполнителях
            arsentiy_tasks = []
            all_assignees = set()
            
            for task in result:
                # Проверяем поле "Участники"
                if "Участники" in task:
                    assignees = task["Участники"]
                    if isinstance(assignees, list):
                        for assignee in assignees:
                            if isinstance(assignee, dict) and "name" in assignee:
                                all_assignees.add(assignee["name"])
                                if assignee["name"] == "Arsentiy":
                                    arsentiy_tasks.append(task)
            
            print(f"\n👥 Все исполнители в Tasks Database:")
            for assignee in sorted(all_assignees):
                print(f"  - {assignee}")
            
            print(f"\n🎯 Задачи Arsentiy: {len(arsentiy_tasks)}")
            for i, task in enumerate(arsentiy_tasks, 1):
                title = task.get("Задача", "Без названия")
                status = task.get("Статус", "Без статуса")
                print(f"{i}. {title} (Статус: {status})")
                
        else:
            print("❌ Не удалось получить данные из Tasks Database")
            
    except Exception as e:
        print(f"❌ Ошибка анализа Tasks Database: {e}")

def analyze_subtasks_database():
    """Анализ базы подзадач через MCP"""
    print("\n🔍 АНАЛИЗ SUBTASKS DATABASE ЧЕРЕЗ MCP")
    print("=" * 50)
    
    try:
        # Импортируем MCP функции
        from notion_mcp_server import analyze_database
        
        # Анализируем Subtasks Database
        subtasks_db_id = os.getenv("NOTION_SUBTASKS_DB_ID")
        print(f"📊 Анализ базы подзадач: {subtasks_db_id}")
        
        # Получаем все подзадачи
        result = analyze_database(subtasks_db_id)
        
        if result:
            print(f"✅ Найдено {len(result)} подзадач")
            
            # Ищем Arsentiy в исполнителях
            arsentiy_subtasks = []
            all_assignees = set()
            
            for subtask in result:
                # Проверяем поле "Исполнитель"
                if "Исполнитель" in subtask:
                    assignees = subtask["Исполнитель"]
                    if isinstance(assignees, list):
                        for assignee in assignees:
                            if isinstance(assignee, dict) and "name" in assignee:
                                all_assignees.add(assignee["name"])
                                if assignee["name"] == "Arsentiy":
                                    arsentiy_subtasks.append(subtask)
            
            print(f"\n👥 Все исполнители в Subtasks Database:")
            for assignee in sorted(all_assignees):
                print(f"  - {assignee}")
            
            print(f"\n📝 Подзадачи Arsentiy: {len(arsentiy_subtasks)}")
            for i, subtask in enumerate(arsentiy_subtasks, 1):
                title = subtask.get("Подзадачи", "Без названия")
                status = subtask.get(" Статус", "Без статуса")  # с пробелом!
                print(f"{i}. {title} (Статус: {status})")
                
        else:
            print("❌ Не удалось получить данные из Subtasks Database")
            
    except Exception as e:
        print(f"❌ Ошибка анализа Subtasks Database: {e}")

def main():
    """Основная функция"""
    print("🔍 ПРОВЕРКА ARSENTIY ЧЕРЕЗ MCP СЕРВЕР")
    print("=" * 50)
    
    # Загружаем переменные окружения
    env_vars = load_env_vars()
    
    # Проверяем MCP сервер
    if not check_mcp_server():
        print("❌ MCP сервер недоступен")
        return
    
    # Анализируем базы данных
    analyze_tasks_database()
    analyze_subtasks_database()
    
    print(f"\n✅ Анализ завершен в {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main() 