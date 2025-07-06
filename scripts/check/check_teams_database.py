#!/usr/bin/env python3
"""
Анализ базы сотрудников Teams в Notion
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

def get_all_teams_members():
    """Получаем всех сотрудников из базы Teams"""
    notion_token = load_env()
    client = Client(auth=notion_token)
    
    # ID базы Teams
    teams_db_id = "1d6ace03d9ff805787b9ec31f5b4dde7"
    
    try:
        response = client.databases.query(
            database_id=teams_db_id,
            page_size=100
        )
        
        return response["results"]
        
    except Exception as e:
        print(f"❌ Ошибка получения сотрудников: {e}")
        return []

def main():
    print("🔍 АНАЛИЗ БАЗЫ СОТРУДНИКОВ (TEAMS)")
    print("=" * 50)
    
    teams_members = get_all_teams_members()
    
    if not teams_members:
        print("❌ Не удалось получить сотрудников")
        return
    
    print(f"📊 Всего сотрудников: {len(teams_members)}")
    
    # Анализируем каждого сотрудника
    for i, member in enumerate(teams_members, 1):
        print(f"\n👤 СОТРУДНИК {i}:")
        print(f"ID: {member['id']}")
        
        properties = member.get("properties", {})
        
        # Название
        name_prop = properties.get("Name", {})
        if name_prop.get("title"):
            name = name_prop["title"][0]["plain_text"]
            print(f"Имя: {name}")
        
        # Email
        email_prop = properties.get("Email", {})
        if email_prop.get("email"):
            email = email_prop["email"]
            print(f"Email: {email}")
        
        # Роль
        role_prop = properties.get("Role", {})
        if role_prop.get("select"):
            role = role_prop["select"]["name"]
            print(f"Роль: {role}")
        
        # Статус
        status_prop = properties.get("Status", {})
        if status_prop.get("status"):
            status = status_prop["status"]["name"]
            print(f"Статус: {status}")
        
        # Другие поля
        print("📋 Все поля:")
        for prop_name, prop_value in properties.items():
            print(f"  {prop_name}: {prop_value.get('type', 'unknown')}")
            if prop_value.get('type') == 'people':
                people = prop_value.get('people', [])
                for person in people:
                    print(f"    - {person.get('name', 'Без имени')} (ID: {person.get('id')})")
            elif prop_value.get('type') == 'select' and prop_value.get('select'):
                print(f"    - {prop_value['select']['name']}")
            elif prop_value.get('type') == 'status' and prop_value.get('status'):
                print(f"    - {prop_value['status']['name']}")
        
        print("-" * 40)

if __name__ == "__main__":
    main() 