#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ПОИСК ГАЙДА С ПОДЗАДАЧАМИ
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

async def find_guide_with_subtasks():
    """Находит гайд с подзадачами"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"🔍 ПОИСК ГАЙДА С ПОДЗАДАЧАМИ")
    print("=" * 50)
    
    try:
        # Ищем в базе гайдов
        guides_query = await client.databases.query(
            database_id="47c60868-58d4-42eb-aece-b4fad1b23ba3",  # Гайды
            filter={
                "property": "Дизайн подзадачи",
                "relation": {
                    "is_not_empty": True
                }
            }
        )
        
        guides = guides_query.get('results', [])
        print(f"📚 Найдено гайдов с подзадачами: {len(guides)}")
        
        for i, guide in enumerate(guides, 1):
            guide_id = guide['id']
            guide_title = guide['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            
            # Получаем количество подзадач
            subtasks_relation = guide['properties'].get('Дизайн подзадачи', {}).get('relation', [])
            
            print(f"{i}. {guide_title}")
            print(f"   🆔 ID: {guide_id}")
            print(f"   📋 Подзадач: {len(subtasks_relation)}")
            
            # Показываем первые 3 подзадачи
            for j, subtask_ref in enumerate(subtasks_relation[:3], 1):
                try:
                    subtask = await client.pages.retrieve(page_id=subtask_ref['id'])
                    subtask_title = subtask['properties'].get('Подзадачи', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
                    print(f"      {j}. {subtask_title}")
                except:
                    print(f"      {j}. Ошибка получения подзадачи")
            
            if len(subtasks_relation) > 3:
                print(f"      ... и еще {len(subtasks_relation) - 3}")
            
            print()
        
        if guides:
            # Возвращаем первый гайд для тестирования
            first_guide = guides[0]
            guide_id = first_guide['id']
            guide_title = first_guide['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            
            print(f"🎯 ДЛЯ ТЕСТИРОВАНИЯ:")
            print(f"📚 Гайд: {guide_title}")
            print(f"🆔 ID: {guide_id}")
            
            return guide_id
        else:
            print("❌ Гайды с подзадачами не найдены")
            return None
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

# Пример использования
if __name__ == "__main__":
    asyncio.run(find_guide_with_subtasks()) 