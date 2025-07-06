#!/usr/bin/env python3
"""
Выводит все задачи по дизайнеру с разбивкой по статусу
"""

import asyncio
import sys
import json
from notion_mcp_server import NotionMCPServer
import os
from typing import Optional

async def get_user_uuid(server, designer_name: str) -> Optional[str]:
    """Получить UUID пользователя по имени"""
    try:
        users = await server.get_users()
        for user in users:
            name = user.get('name', '')
            if designer_name in name:
                user_id = user.get('id')
                print(f"✅ Найден пользователь: {name} (UUID: {user_id})")
                return user_id
        print(f"❌ Пользователь '{designer_name}' не найден")
        return None
    except Exception as e:
        print(f"❌ Ошибка при получении пользователей: {e}")
        return None

async def get_all_users_with_uuid(server):
    """Получить всех пользователей с их UUID"""
    try:
        users = await server.get_users()
        user_map = {}
        for user in users:
            name = user.get('name', '')
            user_id = user.get('id')
            user_map[name] = user_id
            print(f"👤 {name} (UUID: {user_id})")
        return user_map
    except Exception as e:
        print(f"❌ Ошибка при получении пользователей: {e}")
        return {}

async def get_designer_uuid_from_tasks(server, tasks_db_id, designer_name):
    """Получить UUID дизайнера из задач"""
    try:
        # Получаю небольшое количество задач для поиска UUID
        filter_dict = {
            "property": "Участники",
            "people": {
                "is_not_empty": True
            }
        }
        
        tasks = await server.get_pages(tasks_db_id, filter_dict)
        
        # Ищу UUID дизайнера в задачах
        for task in tasks[:50]:  # Проверяю первые 50 задач
            properties = task.get('properties', {})
            participants = properties.get('Участники', {})
            people = participants.get('people', []) if isinstance(participants, dict) else []
            
            for person in people:
                name = person.get('name', '')
                if designer_name.lower() in name.lower():
                    user_id = person.get('id')
                    print(f"✅ Найден дизайнер: {name} (UUID: {user_id})")
                    return user_id
        
        print(f"❌ Дизайнер '{designer_name}' не найден в задачах")
        return None
        
    except Exception as e:
        print(f"❌ Ошибка при поиске UUID дизайнера: {e}")
        return None

async def list_tasks_by_designer(designer_name: str):
    server = NotionMCPServer()
    
    tasks_db_id = getattr(server, 'TASKS_DB', None) or os.getenv('NOTION_TASKS_DB_ID')
    if not tasks_db_id:
        print("❌ Ошибка: не найден ID базы задач")
        return
        
    print(f"🔍 Получение задач для {designer_name} из базы: {tasks_db_id}")
    
    # Получаю UUID дизайнера из задач
    designer_uuid = await get_designer_uuid_from_tasks(server, tasks_db_id, designer_name)
    
    if not designer_uuid:
        print(f"❌ Не удалось найти UUID для '{designer_name}'")
        return
    
    # Создаю фильтр по UUID
    filter_dict = {
        "property": "Участники",
        "people": {
            "contains": designer_uuid
        }
    }
    
    result = await server.get_pages(tasks_db_id, filter_dict)
    tasks = result  # result — это уже отфильтрованный список страниц
    
    print(f"\n📊 Найдено {len(tasks)} задач для {designer_name}")
    
    # Статистика по статусам
    status_counts = {}
    for task in tasks:
        properties = task.get('properties', {})
        status = properties.get('Статус', '')
        status_name = 'unknown'
        if isinstance(status, dict) and 'status' in status:
            status_name = status['status'].get('name', 'unknown')
        elif isinstance(status, str):
            try:
                status_data = json.loads(status.replace("'", '"'))
                if 'status' in status_data:
                    status_name = status_data['status'].get('name', 'unknown')
            except:
                status_name = 'unknown'
        status_counts[status_name] = status_counts.get(status_name, 0) + 1
    
    print("\nСуммарно по статусам:")
    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count}")

if __name__ == "__main__":
    designer = sys.argv[1] if len(sys.argv) > 1 else "Анна Когут"
    asyncio.run(list_tasks_by_designer(designer)) 