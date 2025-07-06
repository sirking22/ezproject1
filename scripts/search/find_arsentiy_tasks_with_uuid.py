#!/usr/bin/env python3
"""
Поиск задач Arsentiy с получением UUID пользователя
Использует правила из DATA_STRUCTURE_GUIDE.md
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from notion_client import Client
except ImportError:
    print("❌ Ошибка: notion-client не установлен")
    print("Установите: pip install notion-client")
    sys.exit(1)

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

def init_notion_client(token: str) -> Client:
    """Инициализация Notion клиента"""
    try:
        client = Client(auth=token)
        # Проверяем подключение
        client.users.me()
        print("✅ Notion клиент инициализирован")
        return client
    except Exception as e:
        print(f"❌ Ошибка инициализации Notion: {e}")
        sys.exit(1)

def get_user_uuid_by_name(client: Client, user_name: str) -> str | None:
    """Получение UUID пользователя по имени"""
    print(f"\n🔍 Поиск UUID для пользователя '{user_name}'...")
    
    try:
        # Получаем всех пользователей
        response = client.users.list()
        
        for user in response["results"]:
            if user["type"] == "person" and user["name"] == user_name:
                user_uuid = user["id"]
                print(f"✅ Найден UUID для '{user_name}': {user_uuid}")
                return user_uuid
        
        print(f"❌ Пользователь '{user_name}' не найден")
        print("Доступные пользователи:")
        for user in response["results"]:
            if user["type"] == "person":
                print(f"  - {user['name']} (ID: {user['id']})")
        
        return None
        
    except Exception as e:
        print(f"❌ Ошибка получения пользователей: {e}")
        return None

def find_tasks_by_assignee_uuid(client: Client, db_id: str, user_uuid: str, status_filter: List[str] | None = None) -> List[Dict]:
    """Поиск задач по UUID исполнителя в Tasks Database"""
    print(f"\n🔍 Поиск задач для UUID '{user_uuid}' в Tasks Database...")
    
    # Правильные поля из DATA_STRUCTURE_GUIDE.md
    filter_conditions = {
        "property": "Участники",
        "people": {
            "contains": user_uuid
        }
    }
    
    # Добавляем фильтр по статусу если указан
    if status_filter:
        filter_conditions = {
            "and": [
                filter_conditions,
                {
                    "property": "Статус",
                    "status": {
                        "in": status_filter
                    }
                }
            ]
        }
    
    try:
        response = client.databases.query(
            database_id=db_id,
            filter=filter_conditions
        )
        
        tasks = []
        for page in response["results"]:
            task = {
                "id": page["id"],
                "title": page["properties"]["Задача"]["title"][0]["plain_text"] if page["properties"]["Задача"]["title"] else "Без названия",
                "status": page["properties"]["Статус"]["status"]["name"] if page["properties"]["Статус"]["status"] else "Без статуса",
                "assignees": [person["name"] for person in page["properties"]["Участники"]["people"]],
                "url": page["url"]
            }
            tasks.append(task)
        
        print(f"✅ Найдено {len(tasks)} задач в Tasks Database")
        return tasks
        
    except Exception as e:
        print(f"❌ Ошибка поиска в Tasks Database: {e}")
        return []

def find_subtasks_by_assignee_uuid(client: Client, db_id: str, user_uuid: str, status_filter: List[str] | None = None) -> List[Dict]:
    """Поиск подзадач по UUID исполнителя в Subtasks Database"""
    print(f"\n🔍 Поиск подзадач для UUID '{user_uuid}' в Subtasks Database...")
    
    # Правильные поля из DATA_STRUCTURE_GUIDE.md (с пробелом в статусе!)
    filter_conditions = {
        "property": "Исполнитель",
        "people": {
            "contains": user_uuid
        }
    }
    
    # Добавляем фильтр по статусу если указан
    if status_filter:
        filter_conditions = {
            "and": [
                filter_conditions,
                {
                    "property": " Статус",  # с пробелом в начале!
                    "status": {
                        "in": status_filter
                    }
                }
            ]
        }
    
    try:
        response = client.databases.query(
            database_id=db_id,
            filter=filter_conditions
        )
        
        subtasks = []
        for page in response["results"]:
            subtask = {
                "id": page["id"],
                "title": page["properties"]["Подзадачи"]["title"][0]["plain_text"] if page["properties"]["Подзадачи"]["title"] else "Без названия",
                "status": page["properties"][" Статус"]["status"]["name"] if page["properties"][" Статус"]["status"] else "Без статуса",
                "assignee": [person["name"] for person in page["properties"]["Исполнитель"]["people"]],
                "url": page["url"]
            }
            subtasks.append(subtask)
        
        print(f"✅ Найдено {len(subtasks)} подзадач в Subtasks Database")
        return subtasks
        
    except Exception as e:
        print(f"❌ Ошибка поиска в Subtasks Database: {e}")
        return []

def print_results(tasks: List[Dict], subtasks: List[Dict], assignee_name: str):
    """Вывод результатов"""
    print(f"\n📊 РЕЗУЛЬТАТЫ ДЛЯ '{assignee_name}'")
    print("=" * 50)
    
    # Задачи
    if tasks:
        print(f"\n🎯 ЗАДАЧИ ({len(tasks)}):")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['title']}")
            print(f"   Статус: {task['status']}")
            print(f"   Исполнители: {', '.join(task['assignees'])}")
            print(f"   Ссылка: {task['url']}")
            print()
    else:
        print("\n🎯 ЗАДАЧИ: Нет задач")
    
    # Подзадачи
    if subtasks:
        print(f"\n📝 ПОДЗАДАЧИ ({len(subtasks)}):")
        for i, subtask in enumerate(subtasks, 1):
            print(f"{i}. {subtask['title']}")
            print(f"   Статус: {subtask['status']}")
            print(f"   Исполнитель: {', '.join(subtask['assignee'])}")
            print(f"   Ссылка: {subtask['url']}")
            print()
    else:
        print("\n📝 ПОДЗАДАЧИ: Нет подзадач")
    
    # Статистика
    print(f"\n📈 СТАТИСТИКА:")
    print(f"   Всего задач: {len(tasks)}")
    print(f"   Всего подзадач: {len(subtasks)}")
    print(f"   Общий объем: {len(tasks) + len(subtasks)}")

def main():
    """Основная функция"""
    print("🔍 ПОИСК ЗАДАЧ ARSENTIY (С UUID)")
    print("=" * 50)
    
    # Загружаем переменные окружения
    env_vars = load_env_vars()
    
    # Инициализируем Notion клиент
    client = init_notion_client(env_vars["token"])
    
    # Правильное имя из DATA_STRUCTURE_GUIDE.md
    assignee_name = "Arsentiy"
    
    # Получаем UUID пользователя
    user_uuid = get_user_uuid_by_name(client, assignee_name)
    if not user_uuid:
        print(f"❌ Не удалось найти UUID для '{assignee_name}'")
        return
    
    # Ищем задачи в статусах To do и In Progress
    status_filter = ["To do", "In Progress"]
    
    # Поиск в Tasks Database
    tasks = find_tasks_by_assignee_uuid(
        client, 
        env_vars["tasks_db_id"], 
        user_uuid, 
        status_filter
    )
    
    # Поиск в Subtasks Database
    subtasks = find_subtasks_by_assignee_uuid(
        client, 
        env_vars["subtasks_db_id"], 
        user_uuid, 
        status_filter
    )
    
    # Выводим результаты
    print_results(tasks, subtasks, assignee_name)
    
    print(f"\n✅ Поиск завершен в {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main() 