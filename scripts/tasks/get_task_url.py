#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 ПОЛУЧЕНИЕ ССЫЛКИ НА ЗАДАЧУ
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

async def get_task_url(task_id: str):
    """Получает ссылку на задачу"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    try:
        # Получаем задачу
        task = await client.pages.retrieve(page_id=task_id)
        task_title = task['properties'].get('Задача', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
        
        # Формируем ссылку
        task_url = f"https://www.notion.so/dreamclub22/{task_id.replace('-', '')}"
        
        print(f"📋 Задача: {task_title}")
        print(f"🆔 ID: {task_id}")
        print(f"🔗 Ссылка: {task_url}")
        
        return task_url
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

# Пример использования
if __name__ == "__main__":
    # Последняя созданная задача
    task_id = "21dace03-d9ff-8191-bcb0-ce64de65980e"
    
    url = asyncio.run(get_task_url(task_id))
    
    if url:
        print(f"\n✅ Ссылка на задачу: {url}")
    else:
        print("❌ Не удалось получить ссылку") 