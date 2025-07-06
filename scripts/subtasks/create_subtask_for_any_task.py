#!/usr/bin/env python3
"""
Создание подзадачи к любой существующей задаче
"""

import asyncio
import json
import logging
from notion_mcp_server import NotionMCPServer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_subtask_for_any_task():
    """Создать подзадачу к любой задаче"""
    
    # Создаем экземпляр MCP сервера
    server = NotionMCPServer()
    
    logger.info("🔍 Ищем любую задачу для создания подзадачи...")
    
    # Получаем любую задачу
    tasks_result = await server.get_pages({
        "database_id": "d09df250ce7e4e0d9fbe4e036d320def",
        "page_size": 1
    })
    
    if not tasks_result:
        logger.error("❌ Не удалось получить задачи")
        return
    
    # Парсим результат
    tasks_data = json.loads(tasks_result[0].text)
    tasks = tasks_data.get("results", [])
    
    if not tasks:
        logger.error("❌ Нет задач в базе")
        return
    
    task = tasks[0]
    task_id = task["id"]
    task_title = ""
    
    # Извлекаем название задачи
    for prop_name, prop_value in task["properties"].items():
        if prop_name == "Задача" and prop_value.get("type") == "title" and prop_value.get("title"):
            task_title = prop_value["title"][0]["plain_text"]
            break
    
    logger.info(f"✅ Найдена задача: {task_title} (ID: {task_id})")
    
    # Создаем подзадачу
    logger.info("📝 Создаем подзадачу...")
    
    subtask_properties = {
        "Подзадачи": {
            "title": [
                {
                    "text": {
                        "content": "Доделать логотип"
                    }
                }
            ]
        },
        " Статус": {
            "status": {
                "name": "To do"
            }
        },
        "Задачи": {
            "relation": [
                {
                    "id": task_id
                }
            ]
        },
        "Часы": {
            "number": 0.5
        }
    }
    
    subtask_result = await server.create_page({
        "database_id": "9c5f4269d61449b6a7485579a3c21da3",
        "properties": subtask_properties
    })
    
    if not subtask_result:
        logger.error("❌ Не удалось создать подзадачу")
        return
    
    # Парсим результат создания
    subtask_data = json.loads(subtask_result[0].text)
    subtask_id = subtask_data.get("page_id")
    subtask_url = subtask_data.get("url")
    
    logger.info(f"✅ Создана подзадача: Доделать логотип")
    logger.info(f"   ID подзадачи: {subtask_id}")
    logger.info(f"   Часы: 0.5")
    
    # Выводим ссылки
    logger.info("\n🔗 ССЫЛКИ:")
    task_url = f"https://notion.so/{task_id.replace('-', '')}"
    logger.info(f"   📋 Задача: {task_url}")
    logger.info(f"   📝 Подзадача: {subtask_url}")
    
    logger.info("\n📝 ИНСТРУКЦИЯ:")
    logger.info("   1. Откройте ссылку на подзадачу")
    logger.info("   2. В поле 'Исполнитель' добавьте 'Arsentiy'")
    logger.info("   3. Проверьте, что в поле 'Часы' указано 0.5")
    logger.info("   4. Сохраните изменения")
    
    logger.info("\n✅ Готово! Подзадача создана с правильными параметрами.")

async def main():
    """Основная функция"""
    try:
        await create_subtask_for_any_task()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 