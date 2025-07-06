#!/usr/bin/env python3
"""
Отладка структуры данных исполнителей
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

def debug_tasks_assignees():
    """Отладка структуры исполнителей в Tasks Database"""
    print("\n🔍 ОТЛАДКА TASKS DATABASE")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем первые 5 задач
        response = client.databases.query(
            database_id=env_vars["tasks_db_id"],
            page_size=5
        )
        
        print(f"✅ Найдено {len(response['results'])} задач")
        
        for i, task in enumerate(response["results"], 1):
            print(f"\n--- Задача {i} ---")
            
            # Название
            title = task["properties"]["Задача"]["title"][0]["plain_text"] if task["properties"]["Задача"]["title"] else "Без названия"
            print(f"Название: {title}")
            
            # Статус
            status = task["properties"]["Статус"]["status"]["name"] if task["properties"]["Статус"]["status"] else "Без статуса"
            print(f"Статус: {status}")
            
            # Участники - полная структура
            assignees_prop = task["properties"]["Участники"]
            print(f"Тип поля Участники: {type(assignees_prop)}")
            print(f"Содержимое Участники: {json.dumps(assignees_prop, indent=2, ensure_ascii=False)}")
            
            # Пытаемся извлечь имена
            if "people" in assignees_prop:
                people = assignees_prop["people"]
                print(f"Количество людей: {len(people)}")
                
                for j, person in enumerate(people):
                    print(f"  Человек {j+1}: {json.dumps(person, indent=4, ensure_ascii=False)}")
                    
                    # Проверяем все возможные поля
                    if "name" in person:
                        print(f"    Имя: {person['name']}")
                    if "id" in person:
                        print(f"    ID: {person['id']}")
                    if "type" in person:
                        print(f"    Тип: {person['type']}")
                    if "avatar_url" in person:
                        print(f"    Аватар: {person['avatar_url']}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def debug_subtasks_assignees():
    """Отладка структуры исполнителей в Subtasks Database"""
    print("\n🔍 ОТЛАДКА SUBTASKS DATABASE")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем первые 5 подзадач
        response = client.databases.query(
            database_id=env_vars["subtasks_db_id"],
            page_size=5
        )
        
        print(f"✅ Найдено {len(response['results'])} подзадач")
        
        for i, subtask in enumerate(response["results"], 1):
            print(f"\n--- Подзадача {i} ---")
            
            # Название
            title = subtask["properties"]["Подзадачи"]["title"][0]["plain_text"] if subtask["properties"]["Подзадачи"]["title"] else "Без названия"
            print(f"Название: {title}")
            
            # Статус (с пробелом!)
            status = subtask["properties"][" Статус"]["status"]["name"] if subtask["properties"][" Статус"]["status"] else "Без статуса"
            print(f"Статус: {status}")
            
            # Исполнитель - полная структура
            assignees_prop = subtask["properties"]["Исполнитель"]
            print(f"Тип поля Исполнитель: {type(assignees_prop)}")
            print(f"Содержимое Исполнитель: {json.dumps(assignees_prop, indent=2, ensure_ascii=False)}")
            
            # Пытаемся извлечь имена
            if "people" in assignees_prop:
                people = assignees_prop["people"]
                print(f"Количество людей: {len(people)}")
                
                for j, person in enumerate(people):
                    print(f"  Человек {j+1}: {json.dumps(person, indent=4, ensure_ascii=False)}")
                    
                    # Проверяем все возможные поля
                    if "name" in person:
                        print(f"    Имя: {person['name']}")
                    if "id" in person:
                        print(f"    ID: {person['id']}")
                    if "type" in person:
                        print(f"    Тип: {person['type']}")
                    if "avatar_url" in person:
                        print(f"    Аватар: {person['avatar_url']}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Основная функция"""
    print("🔍 ОТЛАДКА СТРУКТУРЫ ИСПОЛНИТЕЛЕЙ")
    print("=" * 50)
    
    debug_tasks_assignees()
    debug_subtasks_assignees()
    
    print(f"\n✅ Отладка завершена в {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main() 