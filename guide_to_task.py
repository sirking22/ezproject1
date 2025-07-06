#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ ПРАВИЛЬНАЯ СИСТЕМА: ГАЙД → ЗАДАЧА + ДУБЛИРОВАННЫЕ ПОДЗАДАЧИ
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"
CHECKLISTS_DB = "47c6086858d442ebaeceb4fad1b23ba3"  # База гайдов/чеклистов

async def create_task_from_guide(guide_id: str, task_title: str, task_url: str = None):
    """
    ПРАВИЛЬНО: Создает задачу и дублирует подзадачи как отдельные страницы
    
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
        
        # 2. Находим подзадачи в гайде
        guide_blocks = await client.blocks.children.list(block_id=guide_id)
        blocks = guide_blocks.get('results', [])
        
        subtasks = []
        for block in blocks:
            if block.get('type') == 'to_do':
                content = block['to_do']['rich_text'][0]['text']['content'] if block['to_do']['rich_text'] else 'Без текста'
                checked = block['to_do']['checked']
                subtasks.append({
                    'content': content,
                    'checked': checked
                })
        
        if not subtasks:
            print("❌ Подзадачи не найдены в гайде")
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
        
        # 4. ДУБЛИРУЕМ подзадачи как отдельные страницы в базе гайдов
        checklist_pages = []
        for i, subtask in enumerate(subtasks, 1):
            checklist_data = {
                "parent": {"database_id": CHECKLISTS_DB},
                "properties": {
                    "Name": {
                        "title": [{
                            "type": "text",
                            "text": {"content": f"{i}. {subtask['content']}"}
                        }]
                    },
                    "Статус": {
                        "status": {"name": "Готов" if subtask['checked'] else "Старт"}
                    },
                    "Дизайн задачи": {
                        "relation": [{"id": task_id}]
                    }
                }
            }
            
            checklist_page = await client.pages.create(**checklist_data)
            checklist_pages.append(checklist_page['id'])
        
        task_url = f"https://www.notion.so/dreamclub22/{task_id.replace('-', '')}"
        guide_url = f"https://www.notion.so/dreamclub22/{guide_id.replace('-', '')}"
        
        return {
            'task_id': task_id,
            'task_url': task_url,
            'guide_url': guide_url,
            'guide_title': guide_title,
            'checklist_pages': checklist_pages,
            'subtasks_count': len(subtasks)
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

# Пример использования
if __name__ == "__main__":
    # Гайд упаковки
    guide_id = "20face03-d9ff-8176-9357-ee1f5c52e5a5"
    
    result = asyncio.run(create_task_from_guide(
        guide_id=guide_id,
        task_title="Новая задача из гайда упаковки",
        task_url="https://example.com/task"
    ))
    
    if result:
        print(f"✅ УСПЕХ!")
        print(f"📋 Задача: {result['task_url']}")
        print(f"📚 Гайд: {result['guide_url']}")
        print(f"📋 Дублированных подзадач: {result['subtasks_count']}")
        print(f"📚 Название гайда: {result['guide_title']}")
    else:
        print("❌ ОШИБКА!") 