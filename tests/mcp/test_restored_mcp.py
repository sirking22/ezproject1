#!/usr/bin/env python3
"""
Тест восстановленного MCP сервера с централизованными схемами
"""

import asyncio
from notion_mcp_server_with_schemas import NotionMCPServer

async def test_mcp_server():
    """Тестирование MCP сервера"""
    print("🧪 Тестирование восстановленного MCP сервера...")
    
    try:
        # Создаем сервер
        server = NotionMCPServer()
        print("✅ MCP сервер создан успешно")
        
        # Тестируем получение информации о базах
        result = await server.list_databases({})
        print(f"📊 Список баз данных:\n{result.text}")
        
        # Тестируем получение информации о конкретной базе
        result = await server.get_database_info({"database_name": "tasks"})
        print(f"📋 Информация о базе tasks:\n{result.text}")
        
        # Тестируем получение опций для поля
        result = await server.get_schema_options({"database_name": "tasks", "property_name": "Статус"})
        print(f"⚙️ Опции для поля Статус:\n{result.text}")
        
        print("✅ Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 