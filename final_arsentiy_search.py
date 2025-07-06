#!/usr/bin/env python3
"""
Финальный поиск задач Arsentiy с правильной обработкой данных
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

def search_arsentiy_in_tasks():
    """Поиск Arsentiy в Tasks Database"""
    print("\n🔍 ПОИСК ARSENTIY В TASKS DATABASE")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем ВСЕ задачи (без лимита)
        all_tasks = []
        has_more = True
        start_cursor = None
        
        while has_more:
            response = client.databases.query(
                database_id=env_vars["tasks_db_id"],
                page_size=100,
                start_cursor=start_cursor
            )
            
            all_tasks.extend(response["results"])
            has_more = response["has_more"]
            start_cursor = response.get("next_cursor")
            
            print(f"📊 Загружено {len(all_tasks)} задач...")
        
        print(f"✅ Всего загружено {len(all_tasks)} задач")
        
        # Ищем Arsentiy
        arsentiy_tasks = []
        all_assignees = set()
        
        for task in all_tasks:
            # Участники - правильная обработка структуры
            assignees_prop = task["properties"]["Участники"]
            if "people" in assignees_prop:
                people = assignees_prop["people"]
                for person in people:
                    if "name" in person:
                        name = person["name"]
                        all_assignees.add(name)
                        if name == "Arsentiy":
                            # Название
                            title = task["properties"]["Задача"]["title"][0]["plain_text"] if task["properties"]["Задача"]["title"] else "Без названия"
                            # Статус
                            status = task["properties"]["Статус"]["status"]["name"] if task["properties"]["Статус"]["status"] else "Без статуса"
                            
                            arsentiy_tasks.append({
                                "title": title,
                                "status": status,
                                "url": task["url"]
                            })
        
        print(f"\n👥 Все исполнители в Tasks Database:")
        for assignee in sorted(all_assignees):
            print(f"  - {assignee}")
        
        print(f"\n🎯 Задачи Arsentiy: {len(arsentiy_tasks)}")
        for i, task in enumerate(arsentiy_tasks, 1):
            print(f"{i}. {task['title']} (Статус: {task['status']})")
            print(f"   Ссылка: {task['url']}")
        
        return len(arsentiy_tasks) > 0
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def search_arsentiy_in_subtasks():
    """Поиск Arsentiy в Subtasks Database"""
    print("\n🔍 ПОИСК ARSENTIY В SUBTASKS DATABASE")
    print("=" * 50)
    
    try:
        from notion_client import Client
        
        env_vars = load_env_vars()
        client = Client(auth=env_vars["token"])
        
        # Получаем ВСЕ подзадачи (без лимита)
        all_subtasks = []
        has_more = True
        start_cursor = None
        
        while has_more:
            response = client.databases.query(
                database_id=env_vars["subtasks_db_id"],
                page_size=100,
                start_cursor=start_cursor
            )
            
            all_subtasks.extend(response["results"])
            has_more = response["has_more"]
            start_cursor = response.get("next_cursor")
            
            print(f"📊 Загружено {len(all_subtasks)} подзадач...")
        
        print(f"✅ Всего загружено {len(all_subtasks)} подзадач")
        
        # Ищем Arsentiy
        arsentiy_subtasks = []
        all_assignees = set()
        
        for subtask in all_subtasks:
            # Исполнитель - правильная обработка структуры
            assignees_prop = subtask["properties"]["Исполнитель"]
            if "people" in assignees_prop:
                people = assignees_prop["people"]
                for person in people:
                    if "name" in person:
                        name = person["name"]
                        all_assignees.add(name)
                        if name == "Arsentiy":
                            # Название
                            title = subtask["properties"]["Подзадачи"]["title"][0]["plain_text"] if subtask["properties"]["Подзадачи"]["title"] else "Без названия"
                            # Статус (с пробелом!)
                            status = subtask["properties"][" Статус"]["status"]["name"] if subtask["properties"][" Статус"]["status"] else "Без статуса"
                            
                            arsentiy_subtasks.append({
                                "title": title,
                                "status": status,
                                "url": subtask["url"]
                            })
        
        print(f"\n👥 Все исполнители в Subtasks Database:")
        for assignee in sorted(all_assignees):
            print(f"  - {assignee}")
        
        print(f"\n📝 Подзадачи Arsentiy: {len(arsentiy_subtasks)}")
        for i, subtask in enumerate(arsentiy_subtasks, 1):
            print(f"{i}. {subtask['title']} (Статус: {subtask['status']})")
            print(f"   Ссылка: {subtask['url']}")
        
        return len(arsentiy_subtasks) > 0
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция"""
    print("🔍 ФИНАЛЬНЫЙ ПОИСК ARSENTIY")
    print("=" * 50)
    
    found_in_tasks = search_arsentiy_in_tasks()
    found_in_subtasks = search_arsentiy_in_subtasks()
    
    print(f"\n📊 ИТОГИ ПОИСКА:")
    print(f"   В Tasks Database: {'✅ Найден' if found_in_tasks else '❌ Не найден'}")
    print(f"   В Subtasks Database: {'✅ Найден' if found_in_subtasks else '❌ Не найден'}")
    
    if not found_in_tasks and not found_in_subtasks:
        print(f"\n🚨 Arsentiy НЕ НАЙДЕН НИГДЕ!")
        print("Возможные причины:")
        print("1. Arsentiy не добавлен как пользователь в Notion")
        print("2. Arsentiy не назначен ни на одну задачу/подзадачу")
        print("3. Имя написано по-другому")
        print("4. Arsentiy не работает в текущих проектах")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print("1. Добавить Arsentiy как пользователя в Notion")
        print("2. Назначить Arsentiy на задачи в статусе 'To do' или 'In Progress'")
        print("3. Проверить правильность написания имени")
    
    print(f"\n✅ Поиск завершен в {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main() 