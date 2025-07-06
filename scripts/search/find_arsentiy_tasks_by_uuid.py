#!/usr/bin/env python3
"""
Поиск задач Arsentiy с получением UUID пользователя
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_env_vars():
    """Загрузка переменных окружения"""
    from dotenv import load_dotenv
    load_dotenv()
    
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

def get_arsentiy_uuid():
    """Получение UUID пользователя Arsentiy"""
    print("\n🔍 ПОЛУЧЕНИЕ UUID ARSENTIY")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем всех пользователей
        users = client.users.list()
        
        arsentiy_uuid = None
        for user in users["results"]:
            if user["name"] == "Arsentiy":
                arsentiy_uuid = user["id"]
                print(f"✅ Найден Arsentiy: {user['name']} (ID: {user['id']})")
                break
        
        if not arsentiy_uuid:
            print("❌ Arsentiy не найден в списке пользователей Notion")
            print("Возможные причины:")
            print("1. Arsentiy не добавлен как пользователь в Notion")
            print("2. Имя написано по-другому")
            print("3. Arsentiy работает через другой аккаунт")
            
            print(f"\n👥 Доступные пользователи:")
            for user in users["results"]:
                print(f"  - {user['name']} (ID: {user['id']})")
        
        return arsentiy_uuid
            
    except Exception as e:
        print(f"❌ Ошибка получения UUID: {e}")
        return None

def find_arsentiy_tasks_by_uuid(arsentiy_uuid: str):
    """Поиск задач Arsentiy по UUID в статусе To do или In Progress"""
    print(f"\n🔍 ПОИСК ЗАДАЧ ARSENTIY ПО UUID")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем задачи Arsentiy
        response = client.databases.query(
            database_id=env_vars["tasks_db_id"],
            filter={
                "and": [
                    {
                        "property": "Участники",
                        "people": {
                            "contains": arsentiy_uuid
                        }
                    },
                    {
                        "or": [
                            {
                                "property": "Статус",
                                "status": {
                                    "equals": "To do"
                                }
                            },
                            {
                                "property": "Статус",
                                "status": {
                                    "equals": "In Progress"
                                }
                            }
                        ]
                    }
                ]
            },
            page_size=100
        )
        
        tasks = response["results"]
        print(f"✅ Найдено {len(tasks)} задач Arsentiy в статусе To do / In Progress")
        
        if tasks:
            print(f"\n🎯 ЗАДАЧИ ARSENTIY:")
            for i, task in enumerate(tasks, 1):
                # Название
                title = task["properties"]["Задача"]["title"][0]["plain_text"] if task["properties"]["Задача"]["title"] else "Без названия"
                # Статус
                status = task["properties"]["Статус"]["status"]["name"] if task["properties"]["Статус"]["status"] else "Без статуса"
                # Участники
                assignees = task["properties"]["Участники"]["people"]
                assignee_names = [person["name"] for person in assignees]
                
                print(f"{i}. {title}")
                print(f"   Статус: {status}")
                print(f"   Участники: {', '.join(assignee_names)}")
                print(f"   Ссылка: {task['url']}")
                print()
        else:
            print("❌ Задачи Arsentiy в статусе To do / In Progress не найдены")
            
        return tasks
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def find_arsentiy_subtasks_by_uuid(arsentiy_uuid: str):
    """Поиск подзадач Arsentiy по UUID в статусе To do или In Progress"""
    print(f"\n🔍 ПОИСК ПОДЗАДАЧ ARSENTIY ПО UUID")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем подзадачи Arsentiy
        response = client.databases.query(
            database_id=env_vars["subtasks_db_id"],
            filter={
                "and": [
                    {
                        "property": "Исполнитель",
                        "people": {
                            "contains": arsentiy_uuid
                        }
                    },
                    {
                        "or": [
                            {
                                "property": " Статус",
                                "status": {
                                    "equals": "To do"
                                }
                            },
                            {
                                "property": " Статус",
                                "status": {
                                    "equals": "In Progress"
                                }
                            }
                        ]
                    }
                ]
            },
            page_size=100
        )
        
        subtasks = response["results"]
        print(f"✅ Найдено {len(subtasks)} подзадач Arsentiy в статусе To do / In Progress")
        
        if subtasks:
            print(f"\n📝 ПОДЗАДАЧИ ARSENTIY:")
            for i, subtask in enumerate(subtasks, 1):
                # Название
                title = subtask["properties"]["Подзадачи"]["title"][0]["plain_text"] if subtask["properties"]["Подзадачи"]["title"] else "Без названия"
                # Статус (с пробелом!)
                status = subtask["properties"][" Статус"]["status"]["name"] if subtask["properties"][" Статус"]["status"] else "Без статуса"
                # Исполнитель
                assignees = subtask["properties"]["Исполнитель"]["people"]
                assignee_names = [person["name"] for person in assignees]
                
                print(f"{i}. {title}")
                print(f"   Статус: {status}")
                print(f"   Исполнитель: {', '.join(assignee_names)}")
                print(f"   Ссылка: {subtask['url']}")
                print()
        else:
            print("❌ Подзадачи Arsentiy в статусе To do / In Progress не найдены")
            
        return subtasks
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def main():
    """Основная функция"""
    print("🔍 ПОИСК ЗАДАЧ ARSENTIY ПО UUID")
    print("=" * 50)
    
    # Получаем UUID Arsentiy
    arsentiy_uuid = get_arsentiy_uuid()
    
    if not arsentiy_uuid:
        print("\n❌ Невозможно найти задачи без UUID пользователя")
        return
    
    # Ищем задачи и подзадачи
    tasks = find_arsentiy_tasks_by_uuid(arsentiy_uuid)
    subtasks = find_arsentiy_subtasks_by_uuid(arsentiy_uuid)
    
    print(f"\n📊 ИТОГИ ПОИСКА:")
    print(f"   Задачи To do / In Progress: {len(tasks)}")
    print(f"   Подзадачи To do / In Progress: {len(subtasks)}")
    
    if not tasks and not subtasks:
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print("1. Arsentiy может быть занят другими задачами")
        print("2. Проверьте статусы задач (Backlog, Done)")
        print("3. Возможно, нужно назначить новые задачи")
        print("4. Arsentiy может работать через другой аккаунт")
    
    print(f"\n✅ Поиск завершен в {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main() 