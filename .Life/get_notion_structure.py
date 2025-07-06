#!/usr/bin/env python3
"""
📝 ПОЛУЧЕНИЕ СТРУКТУРЫ БАЗЫ ДАННЫХ NOTION
"""

import os
import requests
from dotenv import load_dotenv

def get_database_structure():
    """Получает структуру базы данных Notion"""
    load_dotenv()
    
    token = os.getenv("NOTION_TOKEN")
    tasks_db_id = os.getenv("NOTION_TASKS_DB")
    
    if not token:
        print("❌ NOTION_TOKEN не найден")
        return None
    
    if not tasks_db_id:
        print("❌ NOTION_TASKS_DB не найден")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28"
        }
        
        # Получаем информацию о базе данных
        url = f"https://api.notion.com/v1/databases/{tasks_db_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            db_info = response.json()
            properties = db_info.get("properties", {})
            
            print("📋 СТРУКТУРА БАЗЫ ДАННЫХ:")
            print("="*50)
            
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type", "unknown")
                print(f"📝 {prop_name}: {prop_type}")
                
                # Показываем опции для select/multi_select
                if prop_type in ["select", "multi_select"]:
                    options = prop_info.get(prop_type, {}).get("options", [])
                    if options:
                        print(f"   Варианты: {[opt.get('name') for opt in options]}")
            
            return properties
        else:
            print(f"❌ Ошибка получения структуры: {response.status_code}")
            print(f"Ответ: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def create_test_task_with_structure(properties):
    """Создает тестовую задачу с учетом реальной структуры"""
    load_dotenv()
    
    token = os.getenv("NOTION_TOKEN")
    tasks_db_id = os.getenv("NOTION_TASKS_DB")
    
    if not token or not tasks_db_id:
        print("❌ Не настроены токены")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        # Создаем payload на основе реальной структуры
        payload = {
            "parent": {"database_id": tasks_db_id},
            "properties": {}
        }
        
        # Добавляем только существующие поля
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type")
            
            if prop_type == "title":
                payload["properties"][prop_name] = {
                    "title": [
                        {
                            "text": {
                                "content": "🧪 Тестовая задача от Quick Voice Assistant"
                            }
                        }
                    ]
                }
            elif prop_type == "select":
                # Берем первый доступный вариант
                options = prop_info.get("select", {}).get("options", [])
                if options:
                    payload["properties"][prop_name] = {
                        "select": {
                            "name": options[0]["name"]
                        }
                    }
            elif prop_type == "date":
                from datetime import datetime
                payload["properties"][prop_name] = {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            elif prop_type == "number":
                payload["properties"][prop_name] = {
                    "number": 1
                }
            elif prop_type == "checkbox":
                payload["properties"][prop_name] = {
                    "checkbox": False
                }
        
        # Создаем задачу
        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Тестовая задача создана успешно!")
            return True
        else:
            print(f"❌ Ошибка создания: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка создания задачи: {e}")
        return False

def main():
    """Основная функция"""
    print("📝" + "="*50)
    print("🎯 ПОЛУЧЕНИЕ СТРУКТУРЫ NOTION БАЗЫ ДАННЫХ")
    print("="*52)
    
    # Получаем структуру
    properties = get_database_structure()
    
    if properties:
        print(f"\n📊 Найдено полей: {len(properties)}")
        
        # Создаем тестовую задачу
        print("\n🧪 Создание тестовой задачи...")
        if create_test_task_with_structure(properties):
            print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print("🚀 Система готова к использованию!")
        else:
            print("\n❌ Ошибка создания задачи")
            print("📝 Проверь права доступа интеграции к базе данных")
    else:
        print("\n❌ Не удалось получить структуру базы данных")

if __name__ == "__main__":
    main() 