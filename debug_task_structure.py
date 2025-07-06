#!/usr/bin/env python3
"""
Отладка структуры задач в Notion
"""

import asyncio
import json
from mcp_notion_server import NotionMCPServer

async def debug_task_structure():
    """Отладка структуры задач"""
    try:
        server = NotionMCPServer()
        tasks_db_id = server.tasks_db_id or "d09df250ce7e4e0d9fbe4e036d320def"
        
        print(f"🔍 Получение задач из базы: {tasks_db_id}")
        tasks_response = await server.get_database_pages(tasks_db_id)
        
        if not tasks_response.get('success'):
            print(f"❌ Ошибка: {tasks_response.get('error')}")
            return
        
        tasks = tasks_response.get('pages', [])
        print(f"📊 Всего задач: {len(tasks)}")
        
        # Берем первые 3 задачи для анализа
        for i, task in enumerate(tasks[:3]):
            print(f"\n{'='*60}")
            print(f"🔍 ЗАДАЧА {i+1}")
            print(f"{'='*60}")
            
            properties = task.get('properties', {})
            
            # Выводим все свойства
            for prop_name, prop_value in properties.items():
                print(f"\n📋 {prop_name}:")
                print(f"   Тип: {type(prop_value)}")
                print(f"   Значение: {json.dumps(prop_value, ensure_ascii=False, indent=2)}")
            
            print(f"\n🆔 ID задачи: {task.get('id')}")
            
            # Специально смотрим на участников и статус
            participants = properties.get('Участники', {})
            status = properties.get('Статус', {})
            
            print(f"\n🎯 УЧАСТНИКИ (детально):")
            print(f"   Тип: {type(participants)}")
            if isinstance(participants, dict):
                if 'people' in participants:
                    people = participants['people']
                    print(f"   Список людей: {len(people) if people else 0}")
                    for person in people:
                        print(f"     - {person}")
            
            print(f"\n📊 СТАТУС (детально):")
            print(f"   Тип: {type(status)}")
            if isinstance(status, dict):
                if 'status' in status:
                    status_info = status['status']
                    print(f"   Статус: {status_info}")
                    if isinstance(status_info, dict):
                        print(f"     - ID: {status_info.get('id')}")
                        print(f"     - Название: {status_info.get('name')}")
                        print(f"     - Цвет: {status_info.get('color')}")
            
            if i == 2:  # Только первые 3 задачи
                break
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_task_structure()) 