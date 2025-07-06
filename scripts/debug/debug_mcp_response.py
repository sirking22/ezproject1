#!/usr/bin/env python3
"""
Отладка ответа MCP сервера
"""

import asyncio
import json
import logging
from notion_mcp_server import NotionMCPServer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_mcp_response():
    """Отладить ответ MCP сервера"""
    
    # Создаем экземпляр MCP сервера
    server = NotionMCPServer()
    
    logger.info("🔍 Отладка MCP сервера...")
    
    # Получаем задачи без фильтров
    tasks_result = await server.get_pages({
        "database_id": "d09df250ce7e4e0d9fbe4e036d320def"
    })
    
    if not tasks_result:
        logger.error("❌ Нет ответа от MCP сервера")
        return
    
    logger.info(f"📋 Получен ответ от MCP сервера")
    logger.info(f"Тип ответа: {type(tasks_result)}")
    logger.info(f"Количество элементов: {len(tasks_result)}")
    
    # Выводим первый элемент
    if tasks_result:
        first_result = tasks_result[0]
        logger.info(f"Первый элемент: {type(first_result)}")
        logger.info(f"Текст: {first_result.text[:500]}...")
        
        try:
            data = json.loads(first_result.text)
            logger.info(f"JSON парсинг успешен")
            logger.info(f"Ключи: {list(data.keys())}")
            
            if "results" in data:
                results = data["results"]
                logger.info(f"Количество результатов: {len(results)}")
                
                if results:
                    first_task = results[0]
                    logger.info(f"Первая задача: {type(first_task)}")
                    logger.info(f"Ключи задачи: {list(first_task.keys())}")
                    
                    if "properties" in first_task:
                        props = first_task["properties"]
                        logger.info(f"Свойства задачи: {list(props.keys())}")
                        
                        # Ищем поле "Задача"
                        for prop_name, prop_value in props.items():
                            if prop_name == "Задача":
                                logger.info(f"Поле 'Задача': {prop_value}")
                                break
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")

async def main():
    """Основная функция"""
    try:
        await debug_mcp_response()
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 