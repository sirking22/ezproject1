#!/usr/bin/env python3
"""
Поиск всех задач Арсения в любом статусе
"""

import asyncio
import json
import logging
from notion_mcp_server import NotionMCPServer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_all_arseniy_tasks():
    """Найти все задачи Арсения"""
    
    # Создаем экземпляр MCP сервера
    server = NotionMCPServer()
    
    logger.info("🔍 Ищем все задачи Арсения...")
    
    # Получаем все задачи
    tasks_result = await server.get_pages({
        "database_id": "d09df250ce7e4e0d9fbe4e036d320def",
        "page_size": 100
    })
    
    if not tasks_result:
        logger.error("❌ Не удалось получить задачи")
        return
    
    # Парсим результат
    tasks_data = json.loads(tasks_result[0].text)
    tasks = tasks_data.get("results", [])
    
    logger.info(f"📋 Всего задач: {len(tasks)}")
    
    arseniy_tasks = []
    
    for task in tasks:
        task_id = task["id"]
        task_title = ""
        task_status = ""
        participants = []
        
        # Извлекаем название задачи, статус и участников
        for prop_name, prop_value in task["properties"].items():
            if prop_name == "Задача" and prop_value.get("type") == "title" and prop_value.get("title"):
                task_title = prop_value["title"][0]["plain_text"]
            elif prop_name == "Статус" and prop_value.get("status"):
                task_status = prop_value["status"]["name"]
            elif prop_name == "Участники" and prop_value.get("people"):
                participants = [p.get("name", "") for p in prop_value["people"]]
        
        # Проверяем, есть ли Арсений среди участников
        if "Arsentiy" in participants or any("арс" in p.lower() for p in participants):
            arseniy_tasks.append({
                "title": task_title,
                "status": task_status,
                "id": task_id,
                "participants": participants
            })
    
    logger.info(f"🎯 Задач Арсения: {len(arseniy_tasks)}")
    
    for i, task in enumerate(arseniy_tasks, 1):
        logger.info(f"{i}. {task['title']}")
        logger.info(f"   Статус: {task['status']}")
        logger.info(f"   Участники: {', '.join(task['participants'])}")
        logger.info(f"   ID: {task['id']}")
        logger.info(f"   URL: https://notion.so/{task['id'].replace('-', '')}")
        logger.info("")

async def main():
    """Основная функция"""
    try:
        await find_all_arseniy_tasks()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 