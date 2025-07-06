#!/usr/bin/env python3
"""
Минимальный MCP сервер для Notion
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List

import mcp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Notion клиента
try:
    from notion_client import Client
    notion = Client(auth=os.getenv("NOTION_TOKEN"))
    logger.info("✅ Notion клиент инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Notion: {e}")
    notion = None

# ID баз данных
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"
RDT_DB = "195ace03d9ff80c1a1b0d236ec3564d2"

# Создаем сервер
server = Server("notion-mcp-server")

@server.list_tools()
async def handle_list_tools():
    """Список доступных инструментов"""
    return [
        Tool(
            name="create_kpi_record",
            description="Создать KPI запись для сотрудника",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "kpi_type": {"type": "string"},
                    "target_value": {"type": "number"},
                    "employee_id": {"type": "string"},
                    "period_start": {"type": "string"},
                    "period_end": {"type": "string"},
                    "comment": {"type": "string"}
                },
                "required": ["name", "kpi_type", "target_value", "employee_id"]
            }
        ),
        Tool(
            name="get_employee_id",
            description="Получить ID сотрудника по имени",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_name": {"type": "string"}
                },
                "required": ["employee_name"]
            }
        ),
        Tool(
            name="list_kpi_records",
            description="Получить список KPI записей",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_size": {"type": "integer", "default": 10}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]):
    """Выполнение инструмента"""
    try:
        if name == "create_kpi_record":
            return await create_kpi_record(arguments)
        elif name == "get_employee_id":
            return await get_employee_id(arguments)
        elif name == "list_kpi_records":
            return await list_kpi_records(arguments)
        else:
            return [TextContent(type="text", text=f"Неизвестный инструмент: {name}")]
    except Exception as e:
        logger.error(f"Ошибка выполнения инструмента {name}: {e}")
        return [TextContent(type="text", text=f"Ошибка: {str(e)}")]

async def create_kpi_record(args: Dict[str, Any]):
    """Создать KPI запись"""
    name = args.get("name")
    kpi_type = args.get("kpi_type")
    target_value = args.get("target_value")
    employee_id = args.get("employee_id")
    period_start = args.get("period_start", "2025-07-01")
    period_end = args.get("period_end", "2025-07-31")
    comment = args.get("comment", "")
    
    properties = {
        "Name": {"title": [{"text": {"content": name}}]},
        "Тип KPI": {"select": {"name": kpi_type}},
        "Целевое значение": {"number": target_value},
        "Сотрудники": {"relation": [{"id": employee_id}]},
        "Период": {"date": {"start": period_start, "end": period_end}},
        "Комментарий": {"rich_text": [{"text": {"content": comment}}]}
    }
    
    try:
        response = notion.pages.create(
            parent={"database_id": KPI_DB},
            properties=properties
        )
        return [TextContent(type="text", text=f"✅ KPI создан: {response['id']}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Ошибка создания KPI: {str(e)}")]

async def get_employee_id(args: Dict[str, Any]):
    """Получить ID сотрудника"""
    employee_name = args.get("employee_name", "").lower()
    
    try:
        response = notion.databases.query(
            database_id=RDT_DB,
            page_size=100
        )
        
        for page in response.get("results", []):
            props = page.get("properties", {})
            title = props.get("Сотрудник", {}).get("title", [])
            if title:
                name = title[0]["plain_text"].lower()
                if employee_name in name or name in employee_name:
                    return [TextContent(type="text", text=f"ID сотрудника {employee_name}: {page['id']}")]
        
        return [TextContent(type="text", text=f"Сотрудник {employee_name} не найден")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Ошибка поиска сотрудника: {str(e)}")]

async def list_kpi_records(args: Dict[str, Any]):
    """Получить список KPI записей"""
    page_size = args.get("page_size", 10)
    
    try:
        response = notion.databases.query(
            database_id=KPI_DB,
            page_size=page_size
        )
        
        records = []
        for page in response.get("results", []):
            page_id = page["id"]
            page_url = page["url"]
            records.append(f"- {page_id}: {page_url}")
        
        return [TextContent(type="text", text=f"📋 KPI записи:\n" + "\n".join(records))]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Ошибка получения KPI: {str(e)}")]

async def main():
    """Главная функция"""
    logger.info("🚀 Запуск минимального MCP Notion Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
        )

if __name__ == "__main__":
    asyncio.run(main()) 