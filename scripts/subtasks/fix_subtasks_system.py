#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ИСПРАВЛЕННАЯ СИСТЕМА ПОДЗАДАЧ
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

async def create_task_with_subtasks(guide_id: str, task_title: str):
    """Создает задачу с правильно связанными подзадачами"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"🔧 СОЗДАНИЕ ЗАДАЧИ С ПОДЗАДАЧАМИ")
    print("=" * 50)
    
    try:
        # 1. Находим подзадачи в гайде
        print(f"🔍 Поиск подзадач в гайде {guide_id}...")
        
        guide = await client.pages.retrieve(page_id=guide_id)
        guide_title = guide['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
        print(f"📚 Гайд: {guide_title}")
        
        # Получаем связанные подзадачи из поля "Дизайн подзадачи"
        subtasks_relation = guide['properties'].get('Дизайн подзадачи', {}).get('relation', [])
        print(f"📋 Найдено подзадач: {len(subtasks_relation)}")
        
        if not subtasks_relation:
            print("❌ Подзадачи не найдены в гайде")
            return None
        
        # 2. Создаем задачу
        print(f"📝 Создание задачи: {task_title}")
        
        task_properties = {
            "Задача": {
                "title": [
                    {
                        "text": {
                            "content": task_title
                        }
                    }
                ]
            },
            "📬 Гайды": {
                "relation": [
                    {
                        "id": guide_id
                    }
                ]
            },
            "Статус": {
                "select": {
                    "name": "Старт"
                }
            }
        }
        
        task = await client.pages.create(
            parent={"database_id": "d09df250ce7e4e0d9fbe4e036d320def"},  # Задачи
            properties=task_properties
        )
        
        task_id = task['id']
        print(f"✅ Задача создана: {task_id}")
        
        # 3. Создаем копии подзадач и связываем с задачей
        created_subtask_ids = []
        
        for i, subtask_ref in enumerate(subtasks_relation, 1):
            subtask_id = subtask_ref['id']
            
            # Получаем оригинальную подзадачу
            original_subtask = await client.pages.retrieve(page_id=subtask_id)
            subtask_title = original_subtask['properties'].get('Подзадачи', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            
            print(f"📋 Создание подзадачи {i}: {subtask_title}")
            
            # Создаем копию подзадачи в базе чеклистов
            new_subtask_properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": subtask_title
                            }
                        }
                    ]
                },
                "Статус": {
                    "select": {
                        "name": "Старт"
                    }
                },
                "Дизайн задачи": {
                    "relation": [
                        {
                            "id": task_id
                        }
                    ]
                }
            }
            
            new_subtask = await client.pages.create(
                parent={"database_id": "47c6086858d442ebaeceb4fad1b23ba3"},  # Чеклисты
                properties=new_subtask_properties
            )
            
            created_subtask_ids.append(new_subtask['id'])
            print(f"   ✅ Создана: {new_subtask['id']}")
        
        # 4. Обновляем задачу, добавляя связь с подзадачами
        print(f"🔗 Связывание подзадач с задачей...")
        
        # Получаем текущие подзадачи в задаче
        current_subtasks = task['properties'].get('Подзадачи', {}).get('relation', [])
        
        # Добавляем новые подзадачи
        all_subtask_relations = current_subtasks + [{"id": subtask_id} for subtask_id in created_subtask_ids]
        
        # Обновляем задачу
        await client.pages.update(
            page_id=task_id,
            properties={
                "Подзадачи": {
                    "relation": all_subtask_relations
                }
            }
        )
        
        print(f"✅ Задача обновлена с {len(created_subtask_ids)} подзадачами")
        
        # 5. Проверяем результат
        print(f"🔍 ПРОВЕРКА РЕЗУЛЬТАТА:")
        
        final_task = await client.pages.retrieve(page_id=task_id)
        final_subtasks = final_task['properties'].get('Подзадачи', {}).get('relation', [])
        
        print(f"📋 Задача: {task_title}")
        print(f"🆔 ID: {task_id}")
        print(f"📚 Гайды: {len(final_task['properties'].get('📬 Гайды', {}).get('relation', []))}")
        print(f"📋 Подзадачи: {len(final_subtasks)}")
        
        for i, subtask_ref in enumerate(final_subtasks, 1):
            subtask = await client.pages.retrieve(page_id=subtask_ref['id'])
            subtask_title = subtask['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            print(f"{i}. {subtask_title}")
        
        return task_id
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

# Пример использования
if __name__ == "__main__":
    # ID гайда с подзадачами
    guide_id = "47c60868-58d4-42eb-aece-b4fad1b23ba3"  # Замените на реальный ID гайда
    task_title = "Тестовая задача с подзадачами"
    
    asyncio.run(create_task_with_subtasks(guide_id, task_title)) 