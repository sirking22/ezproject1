#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Исправление отображения чеклистов в задаче
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

# Загружаем переменные окружения
load_dotenv()

TASK_ID = "21dace03d9ff813e8926de1ce4ecde41"  # ID задачи из ссылки
CHECKLISTS_DB = "9c5f4269d61449b6a7485579a3c21da3"

async def fix_checklist_display():
    """Добавляет чеклисты как дочерние блоки в задачу"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print("🔧 ИСПРАВЛЕНИЕ ОТОБРАЖЕНИЯ ЧЕКЛИСТОВ В ЗАДАЧЕ")
    print("=" * 60)
    print(f"🆔 ID задачи: {TASK_ID}")
    
    try:
        # 1. Находим чеклисты, связанные с этой задачей
        print("1️⃣ Поиск связанных чеклистов...")
        
        response = await client.databases.query(
            database_id=CHECKLISTS_DB,
            filter={
                "property": "Задачи",
                "relation": {
                    "contains": TASK_ID
                }
            }
        )
        
        checklists = response.get('results', [])
        print(f"✅ Найдено чеклистов: {len(checklists)}")
        
        if not checklists:
            print("❌ Чеклисты не найдены")
            return
        
        # 2. Добавляем чеклисты как дочерние блоки в задачу
        print("\n2️⃣ Добавление чеклистов в задачу...")
        
        for i, checklist in enumerate(checklists):
            checklist_title = checklist['properties'].get('Подзадачи', {}).get('title', [{}])[0].get('text', {}).get('content', 'Чеклист')
            
            print(f"   📋 Добавляем: {checklist_title}")
            
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
                block_id=TASK_ID,
                children=task_blocks
            )
            
            print(f"   ✅ Добавлен чеклист {i+1}")
        
        print(f"\n🎉 ГОТОВО! Добавлено чеклистов: {len(checklists)}")
        print(f"🔗 Ссылка на задачу: https://www.notion.so/dreamclub22/{TASK_ID.replace('-', '')}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(fix_checklist_display()) 