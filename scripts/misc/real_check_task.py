#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 РЕАЛЬНАЯ ПРОВЕРКА СОЗДАННОЙ ЗАДАЧИ
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"
CHECKLISTS_DB = "47c6086858d442ebaeceb4fad1b23ba3"

async def real_check_task(task_id: str):
    """Реально проверяет созданную задачу"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"🔍 РЕАЛЬНАЯ ПРОВЕРКА ЗАДАЧИ")
    print("=" * 50)
    
    try:
        # 1. Получаем задачу
        task = await client.pages.retrieve(page_id=task_id)
        task_title = task['properties'].get('Задача', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
        
        print(f"📋 Задача: {task_title}")
        print(f"🆔 ID: {task_id}")
        
        # 2. Проверяем связи с гайдами
        guides_relation = task['properties'].get('📬 Гайды', {}).get('relation', [])
        print(f"📚 Связано с гайдами: {len(guides_relation)}")
        for guide in guides_relation:
            print(f"   • {guide.get('id', 'N/A')}")
        
        # 3. Ищем подзадачи, связанные с этой задачей
        print(f"\n🔍 ПОИСК ПОДЗАДАЧ ЗАДАЧИ:")
        subtasks_query = await client.databases.query(
            database_id=CHECKLISTS_DB,
            filter={
                "property": "Дизайн задачи",
                "relation": {
                    "contains": task_id
                }
            }
        )
        
        task_subtasks = subtasks_query.get('results', [])
        print(f"📋 Найдено подзадач: {len(task_subtasks)}")
        
        if task_subtasks:
            for i, subtask in enumerate(task_subtasks, 1):
                title = subtask['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
                status = subtask['properties'].get('Статус', {}).get('status', {}).get('name', 'Неизвестно')
                
                print(f"{i}. {title}")
                print(f"   Статус: {status}")
                print(f"   ID: {subtask['id']}")
                print()
        else:
            print("❌ ПОДЗАДАЧИ НЕ НАЙДЕНЫ!")
        
        return {
            'task_title': task_title,
            'guides_count': len(guides_relation),
            'subtasks_count': len(task_subtasks)
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

# Пример использования
if __name__ == "__main__":
    # Проверяем последнюю созданную задачу
    task_id = "21dace03-d9ff-8191-bcb0-ce64de65980e"
    
    result = asyncio.run(real_check_task(task_id))
    
    if result:
        print(f"\n📊 РЕАЛЬНЫЕ ИТОГИ:")
        print(f"📋 Задача: {result['task_title']}")
        print(f"📚 Связано с гайдами: {result['guides_count']}")
        print(f"📋 Подзадач у задачи: {result['subtasks_count']}")
        
        if result['subtasks_count'] == 0:
            print("❌ ПРОБЛЕМА: У задачи нет подзадач!")
        else:
            print("✅ У задачи есть подзадачи")
    else:
        print("❌ ОШИБКА ПРОВЕРКИ!") 