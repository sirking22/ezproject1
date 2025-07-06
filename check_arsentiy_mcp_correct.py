#!/usr/bin/env python3
"""
Проверка Arsentiy через MCP сервер
Использует правильные MCP функции
"""

import os
import sys
import json
import asyncio
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

async def check_arsentiy_in_tasks():
    """Проверка Arsentiy в Tasks Database через MCP"""
    print("\n🔍 ПРОВЕРКА ARSENTIY В TASKS DATABASE")
    print("=" * 50)
    
    try:
        # Импортируем MCP сервер
        from notion_mcp_server import NotionMCPServer
        
        # Создаем экземпляр сервера
        server = NotionMCPServer()
        
        # Получаем данные из Tasks Database
        tasks_db_id = os.getenv("NOTION_DESIGN_TASKS_DB_ID")
        print(f"📊 Анализ базы задач: {tasks_db_id}")
        
        # Используем MCP функцию get_pages
        arguments = {
            "database_id": tasks_db_id,
            "page_size": 1000  # Получаем все задачи
        }
        
        result = await server.get_pages(arguments)
        
        if result and len(result) > 0:
            # Парсим результат
            content = result[0].text
            tasks_data = json.loads(content)
            
            print(f"✅ Найдено {len(tasks_data)} задач")
            
            # Ищем Arsentiy в исполнителях
            arsentiy_tasks = []
            all_assignees = set()
            
            for task in tasks_data:
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

async def check_arsentiy_in_subtasks():
    """Проверка Arsentiy в Subtasks Database через MCP"""
    print("\n🔍 ПРОВЕРКА ARSENTIY В SUBTASKS DATABASE")
    print("=" * 50)
    
    try:
        # Импортируем MCP сервер
        from notion_mcp_server import NotionMCPServer
        
        # Создаем экземпляр сервера
        server = NotionMCPServer()
        
        # Получаем данные из Subtasks Database
        subtasks_db_id = os.getenv("NOTION_SUBTASKS_DB_ID")
        print(f"📊 Анализ базы подзадач: {subtasks_db_id}")
        
        # Используем MCP функцию get_pages
        arguments = {
            "database_id": subtasks_db_id,
            "page_size": 1000  # Получаем все подзадачи
        }
        
        result = await server.get_pages(arguments)
        
        if result and len(result) > 0:
            # Парсим результат
            content = result[0].text
            subtasks_data = json.loads(content)
            
            print(f"✅ Найдено {len(subtasks_data)} подзадач")
            
            # Ищем Arsentiy в исполнителях
            arsentiy_subtasks = []
            all_assignees = set()
            
            for subtask in subtasks_data:
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

async def main():
    """Основная функция"""
    print("🔍 ПРОВЕРКА ARSENTIY ЧЕРЕЗ MCP СЕРВЕР")
    print("=" * 50)
    
    # Загружаем переменные окружения
    env_vars = load_env_vars()
    
    # Проверяем базы данных
    await check_arsentiy_in_tasks()
    await check_arsentiy_in_subtasks()
    
    print(f"\n✅ Анализ завершен в {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main()) 