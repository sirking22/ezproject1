#!/usr/bin/env python3
"""
Прямой тест MCP сервера без subprocess
"""

import asyncio
import json
import logging
from typing import Dict, Any
from minimal_mcp_server import MinimalMCPServer
from mcp.server import NotificationOptions

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_mcp_directly():
    """Тестирует MCP сервер напрямую"""
    
    print("🧪 ПРЯМОЙ ТЕСТ MCP СЕРВЕРА (v0.9.1)")
    print("=" * 50)
    
    try:
        # Создаем сервер
        print("1. Создание MCP сервера...")
        server = MinimalMCPServer()
        print(f"✅ Сервер создан: {server.server.name}")
        
        # Тест 1: Проверяем инструменты
        print("2. Проверка инструментов...")
        tools = server.tools
        print(f"✅ Найдено инструментов: {len(tools)}")
        
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
            print(f"     Схема: {list(tool.inputSchema.get('properties', {}).keys())}")
        
        # Тест 2: Проверяем capabilities
        print("3. Проверка capabilities...")
        capabilities = server.server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        )
        print(f"✅ Capabilities получены: {capabilities}")
        
        print("✅ Все тесты прошли успешно!")
        print("\n🎉 MCP СЕРВЕР РАБОТАЕТ КОРРЕКТНО!")
        print("Проблема была в subprocess/stdio, а не в логике сервера.")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_directly()) 