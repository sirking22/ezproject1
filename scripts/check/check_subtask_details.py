#!/usr/bin/env python3
"""
Анализ структуры подзадач в Notion
"""

import json
import os
import sys
from notion_client import Client

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    """Загружаем переменные окружения"""
    from dotenv import load_dotenv
    load_dotenv()
    
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        raise ValueError("NOTION_TOKEN не найден в .env")
    
    return notion_token

def find_subtask_by_title(title: str):
    """Находим подзадачу по названию"""
    notion_token = load_env()
    client = Client(auth=notion_token)
    
    # ID базы подзадач
    subtasks_db_id = "9c5f4269d61449b6a7485579a3c21da3"
    
    try:
        response = client.databases.query(
            database_id=subtasks_db_id,
            filter={
                "property": "Подзадачи",
                "title": {
                    "contains": title
                }
            }
        )
        
        if response["results"]:
            return response["results"][0]
        return None
        
    except Exception as e:
        print(f"❌ Ошибка поиска подзадачи: {e}")
        return None

def main():
    print("🔍 ДЕТАЛИ ПОДЗАДАЧИ")
    print("=" * 40)
    
    # Ищем подзадачу с Арсентием
    subtask = find_subtask_by_title("Арс")
    if not subtask:
        print("❌ Подзадача с 'Арс' не найдена")
        return
    
    print(f"ID подзадачи: {subtask['id']}")
    
    # Название
    title_prop = subtask["properties"]["Подзадачи"]
    if title_prop.get("title"):
        title = title_prop["title"][0]["plain_text"]
        print(f"Название: {title}")
    
    # Проверим все свойства
    print("\n📋 ВСЕ СВОЙСТВА:")
    for prop_name, prop_value in subtask["properties"].items():
        print(f"\n{prop_name}:")
        print(f"  Тип: {prop_value.get('type', 'unknown')}")
        print(f"  Значение: {json.dumps(prop_value, indent=2, ensure_ascii=False)}")
    
    # Особое внимание к исполнителю
    if 'Исполнитель' in subtask["properties"]:
        assignee = subtask["properties"]["Исполнитель"]
        print(f"\n👤 ИСПОЛНИТЕЛЬ:")
        print(f"  Тип: {assignee.get('type')}")
        if assignee.get('people'):
            for person in assignee['people']:
                print(f"  - {person.get('name', 'Без имени')} (ID: {person.get('id')})")
                print(f"    Email: {person.get('person', {}).get('email', 'Не указан')}")
                print(f"    Тип: {person.get('type')}")
        else:
            print("  Нет исполнителя")
    
    # Статус
    if ' Статус' in subtask["properties"]:
        status = subtask["properties"][" Статус"]
        print(f"\n📊 СТАТУС:")
        print(f"  Тип: {status.get('type')}")
        if status.get('status'):
            print(f"  - {status['status']['name']} (ID: {status['status']['id']})")
        else:
            print("  Статус не установлен")

if __name__ == "__main__":
    main() 