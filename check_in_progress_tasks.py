#!/usr/bin/env python3
"""
Проверка задач в статусе In Progress
"""

import asyncio
import json
import logging
from notion_mcp_server import NotionMCPServer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_in_progress_tasks():
    """Проверить задачи в статусе In Progress"""
    
    # Создаем экземпляр MCP сервера
    server = NotionMCPServer()
    
    logger.info("🔍 Ищем задачи в статусе In Progress...")
    
    # Получаем все задачи в статусе In Progress
    tasks_result = await server.get_pages({
        "database_id": "d09df250ce7e4e0d9fbe4e036d320def",
        "filter": {
            "property": "Статус",
            "status": {
                "equals": "In Progress"
            }
        }
    })
    
    if not tasks_result:
        logger.error("❌ Не удалось получить задачи")
        return
    
    # Парсим результат
    tasks_data = json.loads(tasks_result[0].text)
    tasks = tasks_data.get("results", [])
    
    logger.info(f"📋 Найдено задач в статусе In Progress: {len(tasks)}")
    
    for i, task in enumerate(tasks, 1):
        task_id = task["id"]
        task_title = ""
        
        # Извлекаем название задачи
        for prop_name, prop_value in task["properties"].items():
            if prop_value.get("type") == "title" and prop_value.get("title"):
                task_title = prop_value["title"][0]["plain_text"]
                break
        
        logger.info(f"{i}. {task_title}")
        logger.info(f"   ID: {task_id}")
        logger.info(f"   URL: https://notion.so/{task_id.replace('-', '')}")
        logger.info("")

async def main():
    """Основная функция"""
    try:
        await check_in_progress_tasks()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 