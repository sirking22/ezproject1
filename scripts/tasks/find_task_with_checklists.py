#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Поиск задач с чеклистами и исправление отображения
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

# Загружаем переменные окружения
load_dotenv()

TASKS_DB = "d09df250ce7e4e0d9fbe4e036d320def"
CHECKLISTS_DB = "9c5f4269d61449b6a7485579a3c21da3"

async def find_and_fix_tasks_with_checklists():
    """Находит задачи с чеклистами и исправляет их отображение"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print("🔍 ПОИСК ЗАДАЧ С ЧЕКЛИСТАМИ И ИСПРАВЛЕНИЕ ОТОБРАЖЕНИЯ")
    print("=" * 60)
    
    try:
        # 1. Получаем все чеклисты
        print("1️⃣ Получение всех чеклистов...")
        
        checklists_response = await client.databases.query(
            database_id=CHECKLISTS_DB,
            page_size=100
        )
        
        checklists = checklists_response.get('results', [])
        print(f"✅ Найдено чеклистов: {len(checklists)}")
        
        # 2. Группируем чеклисты по задачам
        tasks_with_checklists = {}
        
        for checklist in checklists:
            task_relations = checklist['properties'].get('Задачи', {}).get('relation', [])
            for task_relation in task_relations:
                task_id = task_relation['id']
                if task_id not in tasks_with_checklists:
                    tasks_with_checklists[task_id] = []
                tasks_with_checklists[task_id].append(checklist)
        
        print(f"✅ Задач с чеклистами: {len(tasks_with_checklists)}")
        
        # 3. Обрабатываем каждую задачу
        for task_id, task_checklists in tasks_with_checklists.items():
            print(f"\n🎯 Обработка задачи: {task_id}")
            print(f"   📋 Чеклистов: {len(task_checklists)}")
            
            try:
                # Получаем информацию о задаче
                task = await client.pages.retrieve(page_id=task_id)
                task_title = task['properties'].get('Ф задачи', {}).get('url', 'Без названия')
                print(f"   📝 Название: {task_title}")
                
                # Проверяем, есть ли уже чеклисты в задаче
                task_blocks = await client.blocks.children.list(block_id=task_id)
                existing_checklists = [block for block in task_blocks.get('results', []) 
                                     if block['type'] == 'heading_2' and 
                                     '📋' in block['heading_2'].get('rich_text', [{}])[0].get('text', {}).get('content', '')]
                
                if existing_checklists:
                    print(f"   ⚠️ Чеклисты уже есть в задаче ({len(existing_checklists)})")
                    continue
                
                # Добавляем чеклисты в задачу
                print(f"   🔧 Добавление чеклистов...")
                
                for checklist in task_checklists:
                    checklist_title = checklist['properties'].get('Подзадачи', {}).get('title', [{}])[0].get('text', {}).get('content', 'Чеклист')
                    
                    # Получаем содержимое чеклиста
                    checklist_blocks = await client.blocks.children.list(block_id=checklist['id'])
                    
                    # Создаем блоки для задачи
                    task_blocks = [
                        {
                            "type": "heading_2",
                            "heading_2": {
                                "rich_text": [{"type": "text", "text": {"content": f"📋 {checklist_title}"}}]
                            }
                        }
                    ]
                    
                    # Добавляем чекбоксы из чеклиста
                    for block in checklist_blocks.get('results', []):
                        if block['type'] == 'to_do':
                            rich_text = block['to_do'].get('rich_text', [])
                            checked = block['to_do'].get('checked', False)
                            if rich_text:
                                task_blocks.append({
                                    "type": "to_do",
                                    "to_do": {
                                        "rich_text": [{"type": "text", "text": {"content": rich_text[0]['text']['content']}}],
                                        "checked": checked
                                    }
                                })
                    
                    # Добавляем разделитель
                    task_blocks.append({
                        "type": "divider",
                        "divider": {}
                    })
                    
                    # Добавляем блоки в задачу
                    await client.blocks.children.append(
                        block_id=task_id,
                        children=task_blocks
                    )
                
                print(f"   ✅ Чеклисты добавлены в задачу")
                print(f"   🔗 Ссылка: https://www.notion.so/dreamclub22/{task_id.replace('-', '')}")
                
            except Exception as e:
                print(f"   ❌ Ошибка обработки задачи: {e}")
        
        print(f"\n🎉 ОБРАБОТКА ЗАВЕРШЕНА!")
        print(f"✅ Обработано задач: {len(tasks_with_checklists)}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(find_and_fix_tasks_with_checklists()) 