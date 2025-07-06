#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ ФИНАЛЬНАЯ ПРАВИЛЬНАЯ СИСТЕМА: КОПИРОВАНИЕ ПОДЗАДАЧ ИЗ ПОЛЯ "ДИЗАЙН ПОДЗАДАЧИ" ГАЙДА
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"
CHECKLISTS_DB = "47c6086858d442ebaeceb4fad1b23ba3"

async def create_task_with_guide_subtasks(guide_id: str, task_title: str, task_url: str = None):
    """
    ПРАВИЛЬНО: Создает задачу и копирует подзадачи из поля "Дизайн подзадачи" гайда
    
    Args:
        guide_id: ID гайда в Notion
        task_title: Название новой задачи
        task_url: URL задачи (опционально)
    
    Returns:
        dict с результатом или None при ошибке
    """
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    try:
        # 1. Получаем гайд
        guide = await client.pages.retrieve(page_id=guide_id)
        guide_title = guide['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Неизвестный гайд')
        
        print(f"📚 Гайд: {guide_title}")
        print(f"📋 Создаем задачу: {task_title}")
        
        # 2. НАХОДИМ подзадачи в поле "Дизайн подзадачи" гайда
        print("🔍 Ищем подзадачи в поле 'Дизайн подзадачи' гайда...")
        
        guide_subtasks = guide['properties'].get('Дизайн подзадачи', {}).get('relation', [])
        print(f"📋 Найдено объектов в гайде: {len(guide_subtasks)}")
        
        if not guide_subtasks:
            print("❌ Подзадачи не найдены в гайде")
            return None
        
        # Фильтруем только подзадачи (исключаем гайды)
        actual_subtasks = []
        for relation in guide_subtasks:
            subtask_id = relation['id']
            try:
                # Получаем объект для проверки типа
                subtask_obj = await client.pages.retrieve(page_id=subtask_id)
                
                # Проверяем, что это подзадача из правильной базы данных
                parent_type = subtask_obj.get('parent', {}).get('type', '')
                parent_id = subtask_obj.get('parent', {}).get('database_id', '')
                
                # Если это подзадача из базы подзадач (не чеклистов)
                if parent_type == 'database_id' and parent_id == "9c5f4269-d614-49b6-a748-5579a3c21da3":
                    actual_subtasks.append(relation)
                    print(f"✅ Найдена подзадача: {subtask_id}")
                else:
                    print(f"❌ Исключен объект (не подзадача): {subtask_id}")
                    
            except Exception as e:
                print(f"❌ Ошибка проверки объекта {subtask_id}: {e}")
        
        print(f"📋 Отфильтровано подзадач: {len(actual_subtasks)}")
        
        if not actual_subtasks:
            print("❌ Подзадачи не найдены после фильтрации")
            return None
        
        # 3. Создаем задачу
        task_data = {
            "parent": {"database_id": TASKS_DB},
            "properties": {
                "Задача": {
                    "title": [{
                        "type": "text",
                        "text": {"content": task_title}
                    }]
                },
                "📬 Гайды": {
                    "relation": [{"id": guide_id}]
                },
                "Статус": {
                    "status": {"name": "In Progress"}
                }
            }
        }
        
        if task_url:
            task_data["properties"]["Ф задачи"] = {"url": task_url}
        
        new_task = await client.pages.create(**task_data)
        task_id = new_task['id']
        
        print(f"✅ Задача создана: {task_id}")
        
        # 4. КОПИРУЕМ подзадачи из гайда
        copied_subtasks = []
        for guide_subtask_relation in actual_subtasks:
            try:
                subtask_id = guide_subtask_relation['id']
                
                # Получаем информацию о подзадаче гайда
                guide_subtask = await client.pages.retrieve(page_id=subtask_id)
                
                # Безопасное получение названия из поля "Подзадачи"
                subtasks_prop = guide_subtask['properties'].get('Подзадачи', {})
                if subtasks_prop and subtasks_prop.get('type') == 'title':
                    subtasks_array = subtasks_prop.get('title', [])
                    subtask_title = subtasks_array[0].get('text', {}).get('content', 'Без названия') if subtasks_array else 'Без названия'
                else:
                    subtask_title = f"Подзадача {subtask_id[:8]}"
                
                # Безопасное получение статуса - используем "Старт" по умолчанию
                subtask_status = "Старт"
                
                # Безопасное получение описания
                description_array = guide_subtask['properties'].get('Описание', {}).get('rich_text', [])
                subtask_description = description_array[0].get('text', {}).get('content', '') if description_array else ''
                
                print(f"📋 Копируем подзадачу: {subtask_title}")
                
                # Создаем копию подзадачи
                new_subtask_data = {
                    "parent": {"database_id": CHECKLISTS_DB},
                    "properties": {
                        "Name": {
                            "title": [{
                                "type": "text",
                                "text": {"content": subtask_title}
                            }]
                        },
                        "Статус": {
                            "status": {"name": subtask_status}
                        },
                        "Дизайн задачи": {
                            "relation": [{"id": task_id}]
                        }
                    }
                }
                
                if subtask_description:
                    new_subtask_data["properties"]["Описание"] = {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": subtask_description}
                        }]
                    }
                
                new_subtask = await client.pages.create(**new_subtask_data)
                
                copied_subtasks.append({
                    'id': new_subtask['id'],
                    'title': subtask_title,
                    'status': subtask_status
                })
                
                print(f"✅ Скопирована подзадача: {subtask_title}")
                
            except Exception as e:
                print(f"❌ Ошибка копирования подзадачи: {e}")
        
        task_url = f"https://www.notion.so/dreamclub22/{task_id.replace('-', '')}"
        guide_url = f"https://www.notion.so/dreamclub22/{guide_id.replace('-', '')}"
        
        return {
            'task_id': task_id,
            'task_url': task_url,
            'guide_url': guide_url,
            'guide_title': guide_title,
            'copied_subtasks': copied_subtasks,
            'subtasks_count': len(copied_subtasks)
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

# Пример использования
if __name__ == "__main__":
    # Гайд упаковки
    guide_id = "20face03-d9ff-8176-9357-ee1f5c52e5a5"
    
    result = asyncio.run(create_task_with_guide_subtasks(
        guide_id=guide_id,
        task_title="Задача с копированием подзадач из гайда",
        task_url="https://example.com/task"
    ))
    
    if result:
        print(f"\n✅ УСПЕХ!")
        print(f"📋 Задача: {result['task_url']}")
        print(f"📚 Гайд: {result['guide_url']}")
        print(f"📋 Скопировано подзадач: {result['subtasks_count']}")
        print(f"📚 Название гайда: {result['guide_title']}")
        print(f"📋 Скопированные подзадачи:")
        for subtask in result['copied_subtasks']:
            print(f"   • {subtask['title']} ({subtask['status']})")
    else:
        print("❌ ОШИБКА!") 