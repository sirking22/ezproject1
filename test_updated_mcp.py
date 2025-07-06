#!/usr/bin/env python3
"""
Тест обновленного MCP сервера с интеграцией схем
"""

import asyncio
from notion_mcp_server import NotionMCPServer

async def test_updated_mcp():
    """Тестирование обновленного MCP сервера"""
    print("🧪 Тестирование обновленного MCP сервера с интеграцией схем...")
    
    try:
        # Создаем сервер
        server = NotionMCPServer()
        print("✅ MCP сервер создан успешно")
        
        # Тестируем новые инструменты с интеграцией схем
        print("\n📊 Тестирование инструментов с интеграцией схем:")
        
        # 1. Список баз данных из схем
        result = await server.list_schema_databases({})
        print(f"📋 Список баз данных: {len(result[0]['databases'])} баз")
        
        # 2. Информация о конкретной базе
        result = await server.get_schema_database_info({"database_name": "tasks"})
        if result[0]["success"]:
            print(f"✅ Информация о базе tasks получена")
            print(f"   - Поля: {len(result[0]['properties'])}")
            print(f"   - Статусы: {len(result[0]['status_options'])}")
        else:
            print(f"❌ Ошибка: {result[0]['error']}")
        
        # 3. Опции для поля
        result = await server.get_schema_options({"database_name": "tasks", "property_name": "Статус"})
        if result[0]["success"]:
            print(f"✅ Опции для поля Статус получены")
            print(f"   - Тип: {result[0]['property_type']}")
            print(f"   - Опции: {result[0]['options']}")
        else:
            print(f"❌ Ошибка: {result[0]['error']}")
        
        # 4. Валидация значения
        result = await server.validate_schema_property({"database_name": "tasks", "property_name": "Статус", "value": "To do"})
        if result[0]["success"]:
            print(f"✅ Валидация значения: {result[0]['is_valid']}")
        else:
            print(f"❌ Ошибка: {result[0]['error']}")
        
        print("\n✅ Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    asyncio.run(test_updated_mcp()) 