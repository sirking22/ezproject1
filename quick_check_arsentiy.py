#!/usr/bin/env python3
"""
Быстрая проверка Arsentiy через прямой API вызов
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

def check_tasks_database():
    """Проверка Tasks Database"""
    print("\n🔍 ПРОВЕРКА TASKS DATABASE")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем все задачи
        response = client.databases.query(
            database_id=env_vars["tasks_db_id"],
            page_size=100
        )
        
        print(f"✅ Найдено {len(response['results'])} задач")
        
        # Проверяем первые 10 задач на наличие Arsentiy
        arsentiy_found = False
        all_assignees = set()
        
        for i, page in enumerate(response["results"][:10]):
            print(f"\nЗадача {i+1}:")
            
            # Название
            title = page["properties"]["Задача"]["title"][0]["plain_text"] if page["properties"]["Задача"]["title"] else "Без названия"
            print(f"  Название: {title}")
            
            # Статус
            status = page["properties"]["Статус"]["status"]["name"] if page["properties"]["Статус"]["status"] else "Без статуса"
            print(f"  Статус: {status}")
            
            # Участники
            assignees = page["properties"]["Участники"]["people"]
            assignee_names = [person["name"] for person in assignees]
            print(f"  Участники: {assignee_names}")
            
            # Собираем всех исполнителей
            for name in assignee_names:
                all_assignees.add(name)
                if name == "Arsentiy":
                    arsentiy_found = True
                    print(f"  🎯 НАЙДЕН ARSENTIY!")
        
        print(f"\n👥 Все исполнители в первых 10 задачах:")
        for assignee in sorted(all_assignees):
            print(f"  - {assignee}")
        
        if arsentiy_found:
            print("\n✅ Arsentiy найден в Tasks Database!")
        else:
            print("\n❌ Arsentiy НЕ найден в первых 10 задачах")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_subtasks_database():
    """Проверка Subtasks Database"""
    print("\n🔍 ПРОВЕРКА SUBTASKS DATABASE")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем все подзадачи
        response = client.databases.query(
            database_id=env_vars["subtasks_db_id"],
            page_size=100
        )
        
        print(f"✅ Найдено {len(response['results'])} подзадач")
        
        # Проверяем первые 10 подзадач на наличие Arsentiy
        arsentiy_found = False
        all_assignees = set()
        
        for i, page in enumerate(response["results"][:10]):
            print(f"\nПодзадача {i+1}:")
            
            # Название
            title = page["properties"]["Подзадачи"]["title"][0]["plain_text"] if page["properties"]["Подзадачи"]["title"] else "Без названия"
            print(f"  Название: {title}")
            
            # Статус (с пробелом!)
            status = page["properties"][" Статус"]["status"]["name"] if page["properties"][" Статус"]["status"] else "Без статуса"
            print(f"  Статус: {status}")
            
            # Исполнитель
            assignees = page["properties"]["Исполнитель"]["people"]
            assignee_names = [person["name"] for person in assignees]
            print(f"  Исполнитель: {assignee_names}")
            
            # Собираем всех исполнителей
            for name in assignee_names:
                all_assignees.add(name)
                if name == "Arsentiy":
                    arsentiy_found = True
                    print(f"  🎯 НАЙДЕН ARSENTIY!")
        
        print(f"\n👥 Все исполнители в первых 10 подзадачах:")
        for assignee in sorted(all_assignees):
            print(f"  - {assignee}")
        
        if arsentiy_found:
            print("\n✅ Arsentiy найден в Subtasks Database!")
        else:
            print("\n❌ Arsentiy НЕ найден в первых 10 подзадачах")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Основная функция"""
    print("🔍 БЫСТРАЯ ПРОВЕРКА ARSENTIY")
    print("=" * 50)
    
    check_tasks_database()
    check_subtasks_database()
    
    print(f"\n✅ Проверка завершена в {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main() 