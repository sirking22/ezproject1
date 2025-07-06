#!/usr/bin/env python3
"""
Скрипт для проверки реального содержимого базы привычек с логом:
- Активные привычки (archived=False)
- Архивные привычки (archived=True)
- Количество и названия
"""

import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

# Правильный ID базы привычек
HABITS_DB_ID = "1fddb2b98a1b8053a54aedf250530798"

def check_real_habits():
    """Проверяю реальное содержимое базы привычек"""
    
    client = Client(auth=os.getenv("NOTION_TOKEN"))
    
    print("🔍 Проверяю реальное содержимое базы привычек...")
    print(f"📋 ID базы: {HABITS_DB_ID}")
    
    try:
        # Получаем все привычки (Notion API всегда возвращает все, включая архивные)
        habits = client.databases.query(database_id=HABITS_DB_ID)
        all_habits = habits['results']
        active = [h for h in all_habits if not h.get('archived', False)]
        archived = [h for h in all_habits if h.get('archived', False)]
        print(f"\n=== ЛОГ ===")
        print(f"Всего привычек (API): {len(all_habits)}")
        print(f"Активных (archived=False): {len(active)}")
        print(f"Архивных (archived=True): {len(archived)}")
        print(f"\n--- Активные привычки ---")
        for i, habit in enumerate(active, 1):
            name = habit.get('properties', {}).get('Привычка', {}).get('title', [{}])[0].get('plain_text', 'БЕЗ НАЗВАНИЯ')
            print(f"  {i}. {name}")
        print(f"\n--- Архивные привычки ---")
        for i, habit in enumerate(archived, 1):
            name = habit.get('properties', {}).get('Привычка', {}).get('title', [{}])[0].get('plain_text', 'БЕЗ НАЗВАНИЯ')
            print(f"  {i}. {name}")
        print(f"\n=== КОНЕЦ ЛОГА ===\n")
        
        # Проверяем свойства базы
        print("🔧 Свойства базы:")
        db_info = client.databases.retrieve(database_id=HABITS_DB_ID)
        for prop_name, prop_info in db_info['properties'].items():
            print(f"  - {prop_name}: {prop_info['type']}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_real_habits() 