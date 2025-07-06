#!/usr/bin/env python3
"""
Notion MCP Server с централизованными схемами
Восстановленная версия с интеграцией notion_database_schemas.py
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, UTC
import os
import time
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import sys

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

# Импорт централизованных схем
from notion_database_schemas import (
    DATABASE_SCHEMAS,
    get_database_schema,
    get_all_database_ids,
    get_status_options,
    get_select_options,
    get_multi_select_options,
    get_relations,
    validate_property_value
)

# Загрузка переменных окружения
env_path = find_dotenv()
load_dotenv(env_path, override=False)
print(f"[MCP] ENV файл загружен: {env_path}")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Добавляю отдельный handler для прогресса аналитики
progress_logger = logging.getLogger("notion_progress")
if not progress_logger.handlers:
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    progress_logger.addHandler(sh)
    progress_logger.setLevel(logging.INFO)

class NotionMCPServer:
    """MCP сервер для работы с Notion с централизованными схемами"""
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN не найден в переменных окружения")
            
        self.client = AsyncClient(auth=self.notion_token)
        logger.info(f"[MCP] NOTION_TOKEN loaded: {bool(self.notion_token)}")
        
        # Получаем все ID баз из схем
        self.database_ids = get_all_database_ids()
        logger.info(f"[MCP] Загружено {len(self.database_ids)} баз данных из схем")
        
        # Инициализация MCP сервера
        self.server = Server("notion-mcp-server-with-schemas")
        self.setup_tools()
    
    def setup_tools(self):
        """Настройка инструментов MCP с использованием схем"""
        
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
                            "database_name": {"type": "string", "description": "Имя базы (tasks, ideas, materials, etc.)"},
                            "filter_dict": {"type": "object", "description": "Фильтр для запроса"},
                            "page_size": {"type": "integer", "description": "Количество записей", "default": 10}
                        },
                        "required": ["database_name"]
                    }
                ),
                Tool(
                    name="create_page",
                    description="Создать новую страницу в Notion с валидацией схемы",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_name": {"type": "string", "description": "Имя базы данных"},
                            "title": {"type": "string", "description": "Заголовок страницы"},
                            "description": {"type": "string", "description": "Описание"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Теги"},
                            "status": {"type": "string", "description": "Статус"},
                            "properties": {"type": "object", "description": "Дополнительные свойства"}
                        },
                        "required": ["database_name", "title"]
                    }
                ),
                Tool(
                    name="get_database_info",
                    description="Получить информацию о базе данных из схемы",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_name": {"type": "string", "description": "Имя базы данных"}
                        },
                        "required": ["database_name"]
                    }
                ),
                Tool(
                    name="get_schema_options",
                    description="Получить доступные опции для поля базы данных",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_name": {"type": "string", "description": "Имя базы данных"},
                            "property_name": {"type": "string", "description": "Имя поля"}
                        },
                        "required": ["database_name", "property_name"]
                    }
                ),
                Tool(
                    name="validate_property",
                    description="Проверить валидность значения для поля",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database_name": {"type": "string", "description": "Имя базы данных"},
                            "property_name": {"type": "string", "description": "Имя поля"},
                            "value": {"type": "string", "description": "Значение для проверки"}
                        },
                        "required": ["database_name", "property_name", "value"]
                    }
                ),
                Tool(
                    name="list_databases",
                    description="Список всех доступных баз данных из схем",
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
                if name == "get_pages":
                    return await self.get_pages(arguments)
                elif name == "create_page":
                    return await self.create_page(arguments)
                elif name == "get_database_info":
                    return await self.get_database_info(arguments)
                elif name == "get_schema_options":
                    return await self.get_schema_options(arguments)
                elif name == "validate_property":
                    return await self.validate_property(arguments)
                elif name == "list_databases":
                    return await self.list_databases(arguments)
                else:
                    return TextContent(type="text", text=f"❌ Неизвестный инструмент: {name}")
            except Exception as e:
                logger.error(f"Ошибка выполнения инструмента {name}: {e}")
                return TextContent(type="text", text=f"❌ Ошибка: {str(e)}")
    
    async def get_pages(self, args: Dict[str, Any]) -> TextContent:
        """Получить страницы из базы данных с использованием схемы"""
        database_name = args.get("database_name")
        page_size = args.get("page_size", 10)
        
        if not database_name:
            return TextContent(type="text", text="❌ Не указано имя базы данных")
        
        schema = get_database_schema(database_name)
        if not schema:
            return TextContent(type="text", text=f"❌ База данных '{database_name}' не найдена в схемах")
        
        try:
            response = await self.client.databases.query(
                database_id=schema.database_id,
                page_size=page_size
            )
            
            pages = response.get("results", [])
            result = f"📋 Найдено {len(pages)} страниц в базе '{schema.name}':\n"
            
            for page in pages[:5]:  # Показываем первые 5
                page_id = page["id"]
                page_url = page["url"]
                result += f"- {page_id}: {page_url}\n"
            
            return TextContent(type="text", text=result)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Ошибка получения страниц: {str(e)}")
    
    async def create_page(self, args: Dict[str, Any]) -> TextContent:
        """Создать страницу с валидацией схемы"""
        database_name = args.get("database_name")
        title = args.get("title")
        
        if not database_name or not title:
            return TextContent(type="text", text="❌ Не указаны database_name или title")
        
        schema = get_database_schema(database_name)
        if not schema:
            return TextContent(type="text", text=f"❌ База данных '{database_name}' не найдена в схемах")
        
        # Строим свойства на основе схемы
        properties = {}
        
        # Заголовок
        title_prop = None
        for prop_name, prop_config in schema.properties.items():
            if prop_config.get("type") == "title":
                title_prop = prop_name
                break
        
        if title_prop:
            properties[title_prop] = {"title": [{"text": {"content": title}}]}
        
        # Дополнительные свойства
        additional_props = args.get("properties", {})
        for prop_name, value in additional_props.items():
            if prop_name in schema.properties:
                prop_type = schema.properties[prop_name].get("type")
                if prop_type == "rich_text":
                    properties[prop_name] = {"rich_text": [{"text": {"content": str(value)}}]}
                elif prop_type == "number":
                    properties[prop_name] = {"number": float(value)}
                elif prop_type == "url":
                    properties[prop_name] = {"url": str(value)}
                elif prop_type == "date":
                    properties[prop_name] = {"date": {"start": str(value)}}
                elif prop_type == "multi_select":
                    if isinstance(value, list):
                        properties[prop_name] = {"multi_select": [{"name": tag} for tag in value]}
                elif prop_type == "select":
                    properties[prop_name] = {"select": {"name": str(value)}}
        
        try:
            response = await self.client.pages.create(
                parent={"database_id": schema.database_id},
                properties=properties
            )
            
            return TextContent(type="text", text=f"✅ Страница создана: {response['id']}")
        except Exception as e:
            return TextContent(type="text", text=f"❌ Ошибка создания страницы: {str(e)}")
    
    async def get_database_info(self, args: Dict[str, Any]) -> TextContent:
        """Получить информацию о базе данных из схемы"""
        database_name = args.get("database_name")
        
        if not database_name:
            return TextContent(type="text", text="❌ Не указано имя базы данных")
        
        schema = get_database_schema(database_name)
        if not schema:
            return TextContent(type="text", text=f"❌ База данных '{database_name}' не найдена в схемах")
        
        result = f"📊 Информация о базе данных '{schema.name}':\n"
        result += f"- ID: {schema.database_id}\n"
        result += f"- Описание: {schema.description}\n"
        result += f"- Поля: {', '.join(schema.properties.keys())}\n"
        
        if schema.status_options:
            result += f"- Статусы: {', '.join(next(iter(schema.status_options.values())))}\n"
        
        if schema.multi_select_options:
            result += f"- Теги: {', '.join(next(iter(schema.multi_select_options.values())))}\n"
        
        return TextContent(type="text", text=result)
    
    async def get_schema_options(self, args: Dict[str, Any]) -> TextContent:
        """Получить доступные опции для поля"""
        database_name = args.get("database_name")
        property_name = args.get("property_name")
        
        if not database_name or not property_name:
            return TextContent(type="text", text="❌ Не указаны database_name или property_name")
        
        schema = get_database_schema(database_name)
        if not schema:
            return TextContent(type="text", text=f"❌ База данных '{database_name}' не найдена в схемах")
        
        if property_name not in schema.properties:
            return TextContent(type="text", text=f"❌ Поле '{property_name}' не найдено в схеме")
        
        prop_type = schema.properties[property_name].get("type")
        result = f"📋 Опции для поля '{property_name}' (тип: {prop_type}):\n"
        
        if prop_type == "status" and property_name in schema.status_options:
            options = schema.status_options[property_name]
            result += f"- Статусы: {', '.join(options)}\n"
        elif prop_type == "select" and property_name in schema.select_options:
            options = schema.select_options[property_name]
            result += f"- Выбор: {', '.join(options)}\n"
        elif prop_type == "multi_select" and property_name in schema.multi_select_options:
            options = schema.multi_select_options[property_name]
            result += f"- Теги: {', '.join(options)}\n"
        else:
            result += "- Нет предопределенных опций\n"
        
        return TextContent(type="text", text=result)
    
    async def validate_property(self, args: Dict[str, Any]) -> TextContent:
        """Проверить валидность значения для поля"""
        database_name = args.get("database_name")
        property_name = args.get("property_name")
        value = args.get("value")
        
        if not all([database_name, property_name, value]):
            return TextContent(type="text", text="❌ Не указаны database_name, property_name или value")
        
        is_valid = validate_property_value(database_name, property_name, value)
        
        if is_valid:
            return TextContent(type="text", text=f"✅ Значение '{value}' валидно для поля '{property_name}'")
        else:
            return TextContent(type="text", text=f"❌ Значение '{value}' невалидно для поля '{property_name}'")
    
    async def list_databases(self, args: Dict[str, Any]) -> TextContent:
        """Список всех доступных баз данных из схем"""
        result = "📊 Доступные базы данных:\n"
        
        for db_name, schema in DATABASE_SCHEMAS.items():
            result += f"- {db_name}: {schema.name} ({schema.database_id})\n"
        
        return TextContent(type="text", text=result)

async def main():
    """Главная функция"""
    logger.info("🚀 Запуск Notion MCP Server с централизованными схемами")
    
    server = NotionMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
        )

if __name__ == "__main__":
    asyncio.run(main()) 