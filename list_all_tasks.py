#!/usr/bin/env python3
"""
Вывод всех задач из базы
"""

import asyncio
import json
import logging
from notion_mcp_server import NotionMCPServer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def list_all_tasks():
    """Вывести все задачи"""
    
    # Создаем экземпляр MCP сервера
    server = NotionMCPServer()
    
    logger.info("📋 Получаем все задачи...")
    
    # Получаем все задачи (первые 50)
    tasks_result = await server.get_pages({
        "database_id": "d09df250ce7e4e0d9fbe4e036d320def",
        "page_size": 50
    })
    
    if not tasks_result:
        logger.error("❌ Не удалось получить задачи")
        return
    
    # Парсим результат
    tasks_data = json.loads(tasks_result[0].text)
    tasks = tasks_data.get("results", [])
    
    logger.info(f"📋 Всего задач: {len(tasks)}")
    
    for i, task in enumerate(tasks, 1):
        task_id = task["id"]
        task_title = ""
        task_status = ""
        
        # Извлекаем название задачи и статус
        for prop_name, prop_value in task["properties"].items():
            if prop_name == "Задача" and prop_value.get("type") == "title" and prop_value.get("title"):
                task_title = prop_value["title"][0]["plain_text"]
            elif prop_name == "Статус" and prop_value.get("status"):
                task_status = prop_value["status"]["name"]
        
        logger.info(f"{i}. {task_title}")
        logger.info(f"   Статус: {task_status}")
        logger.info(f"   ID: {task_id}")
        logger.info("")

async def main():
    """Основная функция"""
    try:
        await list_all_tasks()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 