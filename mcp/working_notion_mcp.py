#!/usr/bin/env python3
"""
Рабочий Notion MCP Server
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, UTC
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from notion_client import AsyncClient

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# Загрузка переменных окружения
env_path = find_dotenv()
load_dotenv(env_path, override=False)
print(f"[MCP] ENV файл загружен: {env_path}")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionMCPServer:
    """Рабочий MCP сервер для Notion"""
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.tasks_db_id = os.getenv("NOTION_TASKS_DB_ID")
        self.ideas_db_id = os.getenv("NOTION_IDEAS_DB_ID")
        self.materials_db_id = os.getenv("NOTION_MATERIALS_DB_ID")
        
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN не найден в переменных окружения")
            
        self.client = AsyncClient(auth=self.notion_token)
        logger.info(f"[MCP] NOTION_TOKEN loaded: {bool(self.notion_token)}")
        
        # Инициализация MCP сервера
        self.server = Server("notion-mcp-server")
        self.setup_tools()
    
    def setup_tools(self):
        """Настройка инструментов MCP"""
        
        @self.server.list_tools()
        async def handle_list_tools():
            """Список доступных инструментов"""
            return [
                Tool(
                    name="get_pages",
                    description="Получить страницы из базы данных Notion",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_id": {"type": "string", "description": "ID базы данных"},
                            "filter_dict": {"type": "object", "description": "Фильтр для запроса"}
                        }
                    }
                ),
                Tool(
                    name="get_database_info",
                    description="Получить информацию о базе данных",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_id": {"type": "string", "description": "ID базы данных"}
                        }
                    }
                ),
                Tool(
                    name="ping",
                    description="Проверить работоспособность сервера",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            """Выполнение инструмента"""
            try:
                if name == "ping":
                    return TextContent(type="text", text="✅ Сервер работает!")
                elif name == "get_pages":
                    return await self.get_pages(arguments)
                elif name == "get_database_info":
                    return await self.get_database_info(arguments)
                else:
                    return TextContent(type="text", text=f"❌ Неизвестный инструмент: {name}")
            except Exception as e:
                logger.error(f"Ошибка выполнения инструмента {name}: {e}")
                return TextContent(type="text", text=f"❌ Ошибка: {str(e)}")
    
    async def get_pages(self, args: Dict[str, Any]) -> TextContent:
        """Получить страницы из базы данных"""
        database_id = args.get("database_id", self.tasks_db_id)
        
        try:
            response = await self.client.databases.query(
                database_id=database_id,
                page_size=10
            )
            
            pages = response.get("results", [])
            result = f"📋 Найдено {len(pages)} страниц в базе {database_id}:\n"
            
            for page in pages[:5]:  # Показываем первые 5
                page_id = page["id"]
                page_url = page["url"]
                result += f"- {page_id}: {page_url}\n"
            
            return TextContent(type="text", text=result)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Ошибка получения страниц: {str(e)}")
    
    async def get_database_info(self, args: Dict[str, Any]) -> TextContent:
        """Получить информацию о базе данных"""
        database_id = args.get("database_id", self.tasks_db_id)
        
        try:
            response = await self.client.databases.retrieve(database_id=database_id)
            
            result = f"📊 Информация о базе данных {database_id}:\n"
            result += f"- Название: {response.get('title', [{}])[0].get('plain_text', 'N/A')}\n"
            result += f"- URL: {response.get('url', 'N/A')}\n"
            result += f"- Создана: {response.get('created_time', 'N/A')}\n"
            
            return TextContent(type="text", text=result)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Ошибка получения информации: {str(e)}")

async def main():
    """Главная функция"""
    logger.info("🚀 Запуск рабочего Notion MCP Server")
    
    server = NotionMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="notion-mcp-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(None, {}),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 