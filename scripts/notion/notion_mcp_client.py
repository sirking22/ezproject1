#!/usr/bin/env python3
"""
Notion MCP Client для интеграции с проектом
Клиент для работы с Notion через Model Context Protocol
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import subprocess
import sys
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionMCPClient:
    def __init__(self, server_path: str = "notion_mcp_server.py"):
        self.server_path = server_path
        self.process = None
        self.connected = False
        
    async def start_server(self):
        """Запуск MCP сервера"""
        try:
            # Запускаем сервер как подпроцесс
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Ждем инициализации
            await asyncio.sleep(2)
            self.connected = True
            logger.info("✅ Notion MCP сервер запущен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска MCP сервера: {e}")
            raise
    
    async def stop_server(self):
        """Остановка MCP сервера"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.connected = False
            logger.info("🛑 Notion MCP сервер остановлен")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Вызов инструмента MCP"""
        if not self.connected:
            await self.start_server()
        
        try:
            # Формируем запрос
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            logger.info(f"MCP REQUEST: {json.dumps(request, ensure_ascii=False)}")
            
            # Отправляем запрос
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Читаем ответ
            response_line = await self.process.stdout.readline()
            logger.info(f"MCP RESPONSE RAW: {response_line}")
            response = json.loads(response_line.decode())
            logger.info(f"MCP RESPONSE: {json.dumps(response, ensure_ascii=False)}")
            
            if "result" in response:
                content = response["result"]["content"]
                if content and len(content) > 0:
                    return content[0]["text"]
                return "Пустой ответ"
            else:
                error = response.get("error", {})
                return f"Ошибка: {error.get('message', 'Неизвестная ошибка')}"
                
        except Exception as e:
            logger.error(f"❌ Ошибка вызова инструмента {tool_name}: {e}")
            return f"Ошибка: {str(e)}"
    
    async def get_pages(self, database_id: str, limit: int = 50) -> str:
        """Получить страницы из базы данных"""
        return await self.call_tool("notion_get_pages", {
            "database_id": database_id,
            "limit": limit
        })
    
    async def create_page(self, database_id: str, title: str, **kwargs) -> str:
        """Создать новую страницу"""
        args = {
            "database_id": database_id,
            "title": title,
            **kwargs
        }
        return await self.call_tool("notion_create_page", args)
    
    async def update_page(self, page_id: str, **kwargs) -> str:
        """Обновить страницу"""
        args = {"page_id": page_id, **kwargs}
        return await self.call_tool("notion_update_page", args)
    
    async def search_pages(self, query: str, database_id: Optional[str] = None, limit: int = 20) -> str:
        """Поиск страниц"""
        args = {"query": query, "limit": limit}
        if database_id:
            args["database_id"] = database_id
        return await self.call_tool("notion_search_pages", args)
    
    async def get_database_info(self, database_id: str) -> str:
        """Получить информацию о базе данных"""
        return await self.call_tool("notion_get_database_info", {
            "database_id": database_id
        })
    
    async def bulk_update(self, database_id: str, updates: List[Dict[str, Any]]) -> str:
        """Массовое обновление страниц"""
        return await self.call_tool("notion_bulk_update", {
            "database_id": database_id,
            "updates": updates
        })

# Утилиты для работы с обложками
class NotionCoverManager:
    def __init__(self, mcp_client: NotionMCPClient):
        self.mcp_client = mcp_client
        
    async def apply_covers_from_yandex(self, database_id: str, yandex_folder: str = "Telegram Import"):
        """Применить обложки из Яндекс.Диска"""
        # Получаем все страницы без обложек
        pages_result = await self.mcp_client.get_pages(database_id, limit=100)
        logger.info("📄 Получены страницы для обработки обложек")
        
        # Здесь будет логика поиска и применения обложек
        # Пока возвращаем базовую информацию
        return f"Обработка обложек для базы {database_id} из папки {yandex_folder}"

async def test_mcp_client():
    """Тестирование MCP клиента"""
    client = NotionMCPClient()
    
    try:
        await client.start_server()
        
        # Тестируем получение информации о базе данных
        database_id = os.getenv("NOTION_DATABASE_ID")
        if database_id:
            result = await client.get_database_info(database_id)
            print("📊 Информация о базе данных:")
            print(result)
            
            # Тестируем поиск
            search_result = await client.search_pages("дизайн", limit=5)
            print("\n🔍 Результаты поиска:")
            print(search_result)
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
    finally:
        await client.stop_server()

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(test_mcp_client()) 