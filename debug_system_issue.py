#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ОТЛАДКА ПРОБЛЕМЫ СИСТЕМЫ
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

async def debug_system_issue():
    """Отлаживает проблему с системой"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"🔍 ОТЛАДКА ПРОБЛЕМЫ СИСТЕМЫ")
    print("=" * 50)
    
    # Проверяем последнюю созданную задачу
    task_id = "21dace03-d9ff-8191-bcb0-ce64de65980e"
    
    try:
        # 1. Получаем задачу
        task = await client.pages.retrieve(page_id=task_id)
        task_title = task['properties'].get('Задача', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
        
        print(f"📋 Задача: {task_title}")
        print(f"🆔 ID: {task_id}")
        
        # 2. Проверяем связи с гайдами
        guides_relation = task['properties'].get('📬 Гайды', {}).get('relation', [])
        print(f"📚 Связано с гайдами: {len(guides_relation)}")
        
        for i, guide in enumerate(guides_relation, 1):
            guide_id = guide.get('id', 'N/A')
            print(f"{i}. ID: {guide_id}")
            
            # Проверяем, что это за объект
            try:
                obj = await client.pages.retrieve(page_id=guide_id)
                parent_type = obj.get('parent', {}).get('type', '')
                parent_id = obj.get('parent', {}).get('database_id', '')
                
                if parent_type == 'database_id':
                    if parent_id == "47c60868-58d4-42eb-aece-b4fad1b23ba3":  # Гайды
                        obj_type = "ГАЙД"
                    elif parent_id == "47c6086858d442ebaeceb4fad1b23ba3":  # Чеклисты
                        obj_type = "ПОДЗАДАЧА"
                    else:
                        obj_type = f"ДРУГОЕ ({parent_id})"
                else:
                    obj_type = "НЕ БАЗА ДАННЫХ"
                
                # Получаем название
                name_prop = obj.get('properties', {}).get('Name', {})
                if name_prop and name_prop.get('type') == 'title':
                    title_array = name_prop.get('title', [])
                    if title_array:
                        title = title_array[0].get('text', {}).get('content', 'Без названия')
                    else:
                        title = 'Без названия'
                else:
                    title = 'Без названия'
                
                print(f"   Тип: {obj_type}")
                print(f"   Название: {title}")
                print()
                
            except Exception as e:
                print(f"   Ошибка получения объекта: {e}")
                print()
        
        # 3. Проверяем, есть ли подзадачи в правильном поле
        print(f"🔍 ПРОВЕРЯЕМ ПОДЗАДАЧИ В БАЗЕ ЧЕКЛИСТОВ:")
        
        subtasks_query = await client.databases.query(
            database_id="47c6086858d442ebaeceb4fad1b23ba3",  # Чеклисты
            filter={
                "property": "Дизайн задачи",
                "relation": {
                    "contains": task_id
                }
            }
        )
        
        task_subtasks = subtasks_query.get('results', [])
        print(f"📋 Найдено подзадач: {len(task_subtasks)}")
        
        for i, subtask in enumerate(task_subtasks, 1):
            title = subtask['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            print(f"{i}. {title}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Пример использования
if __name__ == "__main__":
    asyncio.run(debug_system_issue()) 