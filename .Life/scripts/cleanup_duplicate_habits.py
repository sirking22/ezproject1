#!/usr/bin/env python3
"""
Скрипт для полной очистки дублирующихся привычек
Удаляет:
1. Привычки с датами в названиях (старые)
2. Привычки без связей с ритуалами
3. Дублирующиеся записи
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

# ID базы привычек
HABITS_DB_ID = "1fddb2b98a1b8053a54aedf250530798"

def cleanup_duplicate_habits():
    """Полная очистка дублирующихся привычек"""
    
    client = Client(auth=os.getenv("NOTION_TOKEN"))
    
    print("🔍 Получаю все привычки...")
    
    # Получаем все привычки
    habits = client.databases.query(database_id=HABITS_DB_ID)
    
    print(f"📊 Найдено {len(habits['results'])} привычек")
    
    # Анализируем привычки
    to_delete = []
    keep_habits = []
    
    for habit in habits['results']:
        habit_name = habit.get('properties', {}).get('Привычка', {}).get('title', [{}])[0].get('plain_text', '')
        ritual_relation = habit.get('properties', {}).get('Ритуалы', {}).get('relation', [])
        
        # Проверяем критерии для удаления
        should_delete = False
        reason = ""
        
        # 1. Привычки с датами в названиях
        if any(date_str in habit_name for date_str in ['2025-07-']):
            should_delete = True
            reason = "дата в названии"
        
        # 2. Привычки без связей с ритуалами
        elif not ritual_relation:
            should_delete = True
            reason = "нет связи с ритуалом"
        
        # 3. Пустые привычки
        elif not habit_name.strip():
            should_delete = True
            reason = "пустое название"
        
        if should_delete:
            to_delete.append({
                'id': habit['id'],
                'name': habit_name,
                'reason': reason
            })
        else:
            keep_habits.append({
                'id': habit['id'],
                'name': habit_name,
                'ritual_count': len(ritual_relation)
            })
    
    print(f"\n🗑️  Привычки для удаления ({len(to_delete)}):")
    for habit in to_delete:
        print(f"  - {habit['name']} ({habit['reason']})")
    
    print(f"\n✅ Привычки для сохранения ({len(keep_habits)}):")
    for habit in keep_habits:
        print(f"  - {habit['name']} (ритуалов: {habit['ritual_count']})")
    
    if not to_delete:
        print("\n✨ Нет привычек для удаления!")
        return
    
    # Подтверждение удаления
    confirm = input(f"\n❓ Удалить {len(to_delete)} привычек? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Удаление отменено")
        return
    
    # Удаляем привычки
    print("\n🗑️  Удаляю привычки...")
    deleted_count = 0
    
    for habit in to_delete:
        try:
            client.pages.update(page_id=habit['id'], archived=True)
            print(f"  ✅ Удалена: {habit['name']}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Ошибка удаления {habit['name']}: {e}")
    
    print(f"\n🎉 Удалено {deleted_count} из {len(to_delete)} привычек")
    
    # Проверяем результат
    print("\n🔍 Проверяю результат...")
    remaining_habits = client.databases.query(database_id=HABITS_DB_ID)
    print(f"📊 Осталось привычек: {len(remaining_habits['results'])}")
    
    # Показываем оставшиеся привычки
    print("\n📋 Оставшиеся привычки:")
    for habit in remaining_habits['results']:
        habit_name = habit.get('properties', {}).get('Привычка', {}).get('title', [{}])[0].get('plain_text', '')
        ritual_relation = habit.get('properties', {}).get('Ритуалы', {}).get('relation', [])
        print(f"  - {habit_name} (ритуалов: {len(ritual_relation)})")

if __name__ == "__main__":
    cleanup_duplicate_habits() 