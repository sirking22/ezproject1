#!/usr/bin/env python3
"""
Notion MCP Server для интеграции с проектом
Позволяет работать с Notion через Model Context Protocol
Версия: 0.9.1
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
import yaml
import pytz
from src.utils.date_utils import parse_notion_date

# Импорт централизованных схем
from notion_database_schemas import (
    DATABASE_SCHEMAS,
    get_database_schema,
    get_all_database_ids,
    get_status_options,
    get_select_options,
    get_multi_select_options,
    get_relations,
    validate_property_value,
    get_database_id
)

# Импорт безопасных операций
from safe_database_operations import SafeDatabaseOperations

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

# первоначальный вызов без пути
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

# ---------------------------------------------------------
# Дополнительная попытка загрузить .env из корня проекта (если нужно)
# ---------------------------------------------------------

if not os.getenv("NOTION_TOKEN"):
    possible_roots = [
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
    ]
    for env_path in possible_roots:
        if env_path.exists():
            loaded = load_dotenv(env_path, override=False)
            logger.info(f"[MCP] dotenv extra load={loaded} path={env_path}")
            if os.getenv("NOTION_TOKEN"):
                break

class NotionMCPServer:
    """Универсальный сервер для работы с Notion и Яндексом через MCP"""
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.tasks_db_id = os.getenv("NOTION_TASKS_DB_ID")
        self.ideas_db_id = os.getenv("NOTION_IDEAS_DB_ID")
        self.materials_db_id = os.getenv("NOTION_MATERIALS_DB_ID")
        self.projects_db_id = os.getenv("NOTION_PROJECTS_DB_ID")
        self.kpi_db_id = os.getenv("NOTION_KPI_DB_ID")
        self.epics_db_id = os.getenv("NOTION_EPICS_DB_ID")
        self.guides_db_id = os.getenv("NOTION_GUIDES_DB_ID")
        self.super_guides_db_id = os.getenv("NOTION_SUPER_GUIDES_DB_ID")
        self.marketing_tasks_db_id = os.getenv("NOTION_MARKETING_TASKS_DB_ID")
        self.smm_tasks_db_id = os.getenv("NOTION_SMM_TASKS_DB_ID")
        
        # Валидация критически важных переменных
        required_vars = {
            "NOTION_TOKEN": self.notion_token,
            "NOTION_TASKS_DB_ID": self.tasks_db_id,
            "NOTION_IDEAS_DB_ID": self.ideas_db_id,
            "NOTION_MATERIALS_DB_ID": self.materials_db_id,
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
        
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN не найден в переменных окружения")
        
        self.client = AsyncClient(auth=self.notion_token)
        logger.info(f"[MCP] NOTION_TOKEN loaded: {bool(self.notion_token)}")
        logger.info(f"[MCP] TASKS_DB_ID: {self.tasks_db_id}")
        # --- FIX: инициализация кэша схем ---
        self.database_cache = {}
        self.cache_timestamp = {}
        self.cache_ttl = 3600  # 1 час по умолчанию
        from pathlib import Path
        self.schema_cache_dir = Path(".notion_schema_cache")
        self.schema_cache_dir.mkdir(exist_ok=True)
        
        # Инициализация MCP сервера
        self.server = Server("notion-mcp-server")
        
        # Получаем все ID баз из схем
        self.database_ids = get_all_database_ids()
        logger.info(f"[MCP] Загружено {len(self.database_ids)} баз данных из схем")

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """Список доступных инструментов MCP"""
        tools = [
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
                name="create_page",
                description="Создать новую страницу в Notion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string", "description": "ID базы данных"},
                        "title": {"type": "string", "description": "Заголовок страницы"},
                        "description": {"type": "string", "description": "Описание"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Теги"},
                        "properties": {"type": "object", "description": "Дополнительные свойства"}
                    }
                }
            ),
            Tool(
                name="update_page",
                description="Обновить страницу в Notion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {"type": "string", "description": "ID страницы"},
                        "properties": {"type": "object", "description": "Свойства для обновления"}
                    }
                }
            ),
            Tool(
                name="search_pages",
                description="Поиск страниц в Notion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Поисковый запрос"},
                        "database_id": {"type": "string", "description": "ID базы данных"}
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
                name="get_notion_schema",
                description="Получить схему базы данных",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string", "description": "ID базы данных"},
                        "force_refresh": {"type": "boolean", "description": "Принудительное обновление"}
                    }
                }
            ),
            Tool(
                name="get_schema_database_info",
                description="Получить информацию о базе данных из централизованных схем",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_name": {"type": "string", "description": "Имя базы (tasks, ideas, materials, etc.)"}
                    },
                    "required": ["database_name"]
                }
            ),
            Tool(
                name="get_schema_options",
                description="Получить доступные опции для поля из схемы",
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
                name="validate_schema_property",
                description="Проверить валидность значения для поля по схеме",
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
                name="list_schema_databases",
                description="Список всех доступных баз данных из централизованных схем",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_kpi_metrics",
                description="Получить KPI метрики по сотруднику/периоду/типу",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "employee_name": {"type": "string", "description": "Имя сотрудника"},
                        "kpi_type": {"type": "string", "description": "Тип KPI (полиграфия/контент/дизайн/общие)"},
                        "period_start": {"type": "string", "description": "Начало периода (YYYY-MM-DD)"},
                        "period_end": {"type": "string", "description": "Конец периода (YYYY-MM-DD)"},
                        "include_formulas": {"type": "boolean", "description": "Включить формулы расчёта", "default": True}
                    }
                }
            ),
            Tool(
                name="calculate_bonus",
                description="Рассчитать бонус по формуле эффективности",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "employee_name": {"type": "string", "description": "Имя сотрудника"},
                        "base_salary": {"type": "number", "description": "Базовая зарплата", "default": 100000},
                        "period": {"type": "string", "description": "Период расчёта (месяц/квартал)"}
                    },
                    "required": ["employee_name"]
                }
            ),
            Tool(
                name="get_performance_data",
                description="Получить данные эффективности по проектам/материалам",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string", "description": "Тип контента (карточки/YouTube/соцсети/полиграфия/концепты)"},
                        "metric_type": {"type": "string", "description": "Тип метрики (просмотры/конверсия/время/качество)"},
                        "date_from": {"type": "string", "description": "Дата начала (YYYY-MM-DD)"},
                        "date_to": {"type": "string", "description": "Дата окончания (YYYY-MM-DD)"}
                    }
                }
            ),
            Tool(
                name="update_kpi_record",
                description="Обновить или создать KPI запись",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "kpi_name": {"type": "string", "description": "Название KPI"},
                        "kpi_type": {"type": "string", "description": "Тип KPI"},
                        "target_value": {"type": "number", "description": "Целевое значение"},
                        "current_value": {"type": "number", "description": "Текущее значение"},
                        "content_type": {"type": "string", "description": "Тип контента"},
                        "period": {"type": "string", "description": "Период (YYYY-MM-DD)"},
                        "comment": {"type": "string", "description": "Комментарий"}
                    },
                    "required": ["kpi_name", "kpi_type", "target_value"]
                }
            ),
            Tool(
                name="add_select_option",
                description="Добавить новое значение в select поле",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string", "description": "ID базы данных"},
                        "property_name": {"type": "string", "description": "Имя поля"},
                        "new_option": {"type": "string", "description": "Новое значение для добавления"}
                    },
                    "required": ["database_id", "property_name", "new_option"]
                }
            ),
            Tool(
                name="add_multi_select_option",
                description="Добавить новое значение в multi_select поле",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string", "description": "ID базы данных"},
                        "property_name": {"type": "string", "description": "Имя поля"},
                        "new_option": {"type": "string", "description": "Новое значение для добавления"}
                    },
                    "required": ["database_id", "property_name", "new_option"]
                }
            ),
            Tool(
                name="safe_create_with_auto_options",
                description="Создать запись с автоматическим добавлением новых значений в select/multi_select поля",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string", "description": "ID базы данных"},
                        "properties": {"type": "object", "description": "Свойства записи"}
                    },
                    "required": ["database_id", "properties"]
                }
            ),
            Tool(
                name="add_multiple_options",
                description="Добавить несколько новых значений в select или multi_select поле",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string", "description": "ID базы данных"},
                        "property_name": {"type": "string", "description": "Имя поля"},
                        "new_options": {"type": "array", "items": {"type": "string"}, "description": "Список новых значений"},
                        "field_type": {"type": "string", "description": "Тип поля (select/multi_select)", "default": "select"}
                    },
                    "required": ["database_id", "property_name", "new_options"]
                }
            )
        ]
        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Вызов инструмента MCP"""
        try:
            tool_name = request.name
            arguments = request.arguments or {}
            
            if tool_name == "get_pages":
                result = await self.get_pages(
                    arguments.get("database_id", self.tasks_db_id),
                    arguments.get("filter_dict")
                )
            elif tool_name == "create_page":
                    result = await self.create_page(arguments)
            elif tool_name == "update_page":
                    result = await self.update_page(arguments)
            elif tool_name == "search_pages":
                    result = await self.search_pages(arguments)
            elif tool_name == "get_database_info":
                    result = await self.get_database_info(arguments)
            elif tool_name == "get_notion_schema":
                    result = await self.get_notion_schema(arguments)
            elif tool_name == "get_schema_database_info":
                result = await self.get_schema_database_info(arguments)
            elif tool_name == "get_schema_options":
                result = await self.get_schema_options(arguments)
            elif tool_name == "validate_schema_property":
                result = await self.validate_schema_property(arguments)
            elif tool_name == "list_schema_databases":
                result = await self.list_schema_databases(arguments)
            elif tool_name == "get_kpi_metrics":
                result = await self.get_kpi_metrics(arguments)
            elif tool_name == "calculate_bonus":
                result = await self.calculate_bonus(arguments)
            elif tool_name == "get_performance_data":
                result = await self.get_performance_data(arguments)
            elif tool_name == "update_kpi_record":
                result = await self.update_kpi_record(arguments)
            elif tool_name == "add_select_option":
                result = await self.add_select_option(arguments)
            elif tool_name == "add_multi_select_option":
                result = await self.add_multi_select_option(arguments)
            elif tool_name == "safe_create_with_auto_options":
                result = await self.safe_create_with_auto_options(arguments)
            elif tool_name == "add_multiple_options":
                result = await self.add_multiple_options(arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Неизвестный инструмент: {tool_name}")]
                )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
            )
            
        except Exception as e:
            logger.error(f"[MCP] Ошибка вызова инструмента {request.name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Ошибка: {str(e)}")]
            )

    async def get_pages(self, database_id: str, filter_dict: Optional[dict] = None, limit: Optional[int] = None) -> List[dict]:
        """Получить страницы из базы данных с опциональным фильтром и лимитом"""
        try:
            kwargs = {"database_id": database_id}
            if filter_dict:
                kwargs["filter"] = filter_dict
            if limit:
                kwargs["page_size"] = limit
            
            response = await self.client.databases.query(**kwargs)
            pages = response.get("results", [])
            
            # Пагинация для получения всех страниц (только если не указан лимит)
            if not limit:
                while response.get("has_more"):
                    next_kwargs = {
                        "database_id": database_id,
                        "start_cursor": response.get("next_cursor")
                    }
                    if filter_dict:
                        next_kwargs["filter"] = filter_dict
                    
                    response = await self.client.databases.query(**next_kwargs)
                    pages.extend(response.get("results", []))
            
            logger.info(f"[MCP] Получено {len(pages)} страниц из базы {database_id}")
            return pages
            
        except Exception as e:
            logger.error(f"[MCP] Ошибка при получении страниц: {e}")
            return []

    async def create_page(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Создать новую страницу с автозаполнением и валидацией по схеме базы"""
        logger.info(f"[MCP] CREATE_PAGE: {arguments}")
        database_id = arguments.get("database_id", self.tasks_db_id)
        try:
            schema = await self._get_database_schema(database_id)
            props_schema = schema.get("properties", {})
            # Автозаполнение пропущенных полей дефолтами (если есть)
            properties = arguments.get("properties", {})
            for k, v in props_schema.items():
                if k not in properties:
                    # Можно добавить дефолты по типу, если нужно
                    if v["type"] == "title":
                        properties[k] = {"title": [{"text": {"content": ""}}]}
                    elif v["type"] == "rich_text":
                        properties[k] = {"rich_text": []}
                    elif v["type"] == "number":
                        properties[k] = {"number": None}
                    elif v["type"] == "multi_select":
                        properties[k] = {"multi_select": []}
                    elif v["type"] == "select":
                        properties[k] = {"select": None}
                    elif v["type"] == "date":
                        properties[k] = {"date": None}
                    # ... другие типы по необходимости
            # Валидация: убираем поля, которых нет в схеме
            properties = {k: v for k, v in properties.items() if k in props_schema}
            arguments["properties"] = properties
        except Exception as e:
            logger.warning(f"[MCP] CREATE_PAGE: schema validation failed: {e}")
        # Дальше стандартная логика создания
        
        try:
            title = arguments.get("title", "Новая страница")
            
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
            
            # Добавляем описание если есть
            if "description" in arguments:
                properties["Описание"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": arguments["description"]
                            }
                        }
                    ]
                }
            
            # Добавляем теги если есть
            if "tags" in arguments and arguments["tags"]:
                properties["Теги"] = {
                    "multi_select": [{"name": tag} for tag in arguments["tags"]]
                }
            
            # Добавляем статус если есть
            if "status" in arguments:
                properties["Статус"] = {
                    "select": {
                        "name": arguments["status"]
                    }
                }
            
            # Добавляем важность если есть
            if "importance" in arguments:
                properties["Важность"] = {
                    "number": arguments["importance"]
                }
            
            # Добавляем URL если есть
            if "url" in arguments:
                properties["URL"] = {
                    "url": arguments["url"]
                }
            
            # Добавляем дату выполнения если есть
            if "due_date" in arguments:
                properties["Date"] = {
                    "date": {
                        "start": arguments["due_date"]
                    }
                }
            
            response = await self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            result = {
                "success": True,
                "page_id": response["id"],
                "url": response["url"],
                "title": title
            }
            
            return [result]
        except Exception as e:
            logger.error(f"[MCP] ERROR CREATE_PAGE: {e}")
            return [{"success": False, "error": str(e)}]

    async def update_page(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Обновить страницу с автозаполнением и валидацией по схеме базы"""
        logger.info(f"[MCP] UPDATE_PAGE: {arguments}")
        try:
            page_id = arguments["page_id"]
            # Получаем id базы через саму страницу (Notion API)
            page = await self.client.pages.retrieve(page_id=page_id)
            database_id = page["parent"]["database_id"]
            schema = await self._get_database_schema(database_id)
            props_schema = schema.get("properties", {})
            properties = arguments.get("properties", {})
            # Валидация: убираем поля, которых нет в схеме
            properties = {k: v for k, v in properties.items() if k in props_schema}
            arguments["properties"] = properties
        except Exception as e:
            logger.warning(f"[MCP] UPDATE_PAGE: schema validation failed: {e}")
        # Дальше стандартная логика обновления
        
        try:
            response = await self.client.pages.update(page_id=page_id, properties=properties)
            
            result = {
                "success": True,
                "page_id": page_id,
                "url": response["url"]
            }
            
            return [result]
        except Exception as e:
            logger.error(f"[MCP] ERROR UPDATE_PAGE: {e}")
            return [{"success": False, "error": str(e)}]

    async def search_pages(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Поиск страниц по тексту"""
        logger.info(f"[MCP] SEARCH_PAGES: {arguments}")
        
        try:
            query = arguments["query"]
            database_id = arguments.get("database_id")
            limit = arguments.get("limit", 10)
            
            filter_params = {}
            if database_id:
                filter_params["filter"] = {
                    "property": "database_id",
                    "database": {
                        "equals": database_id
                    }
                }
            
            response = await self.client.search(
                query=query,
                page_size=limit,
                **filter_params
            )
            
            results = response.get("results", [])
            
            result = {
                "query": query,
                "results_count": len(results),
                "results": results[:5]  # Ограничиваем для читаемости
            }
            
            return [result]
        except Exception as e:
            logger.error(f"[MCP] ERROR SEARCH_PAGES: {e}")
            return [{"success": False, "error": str(e)}]

    async def get_database_info(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить информацию о базе данных"""
        logger.info(f"[MCP] GET_DATABASE_INFO: {arguments}")
        
        try:
            database_id = arguments["database_id"]
            schema = await self._get_database_schema(database_id)

            result = {
                "database_id": database_id,
                "title": schema.get("title", []),
                "properties": list(schema.get("properties", {}).keys()),
                "url": schema.get("url"),
                "cached": True,
            }

            return [result]
        except Exception as e:
            logger.error(f"[MCP] ERROR GET_DATABASE_INFO: {e}")
            return [{"success": False, "error": str(e)}]

    async def bulk_update(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Массовое обновление страниц"""
        logger.info(f"[MCP] BULK_UPDATE: {arguments}")
        return [{"success": False, "error": "Bulk update not implemented yet"}]

    async def delete_page(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Удалить страницу"""
        logger.info(f"[MCP] DELETE_PAGE: {arguments}")
        
        try:
            page_id = arguments["page_id"]
            
            # Удаляем страницу через Notion API
            await self.client.pages.update(
                page_id=page_id,
                archived=True  # Архивируем вместо удаления
            )
            
            result = {
                "success": True,
                "page_id": page_id,
                "message": "Страница успешно архивирована"
            }
            
            return [result]
            
        except Exception as e:
            logger.error(f"[MCP] ERROR DELETE_PAGE: {e}")
            return [{"success": False, "error": str(e)}]

    async def get_page_content(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить содержимое страницы"""
        logger.info(f"[MCP] GET_PAGE_CONTENT: {arguments}")
        return [{"success": False, "error": "Get page content not implemented yet"}]

    async def add_comment(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Добавить комментарий к странице"""
        logger.info(f"[MCP] ADD_COMMENT: {arguments}")
        return [{"success": False, "error": "Add comment not implemented yet"}]

    async def get_comments(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить комментарии страницы"""
        logger.info(f"[MCP] GET_COMMENTS: {arguments}")
        return [{"success": False, "error": "Get comments not implemented yet"}]

    async def upload_file(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Загрузить файл"""
        logger.info(f"[MCP] UPLOAD_FILE: {arguments}")
        return [{"success": False, "error": "Upload file not implemented yet"}]

    async def get_file(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить файл"""
        file_id = arguments.get("file_id")
        logger.info(f"[MCP] GET_FILE: file_id={file_id}")
        
        try:
            # Используем правильный API для получения файла
            response = await self.client.pages.retrieve(page_id=file_id)
            return [response]
        except Exception as e:
            logger.error(f"[MCP] ERROR GET_FILE: {e}")
            return [{"success": False, "error": str(e)}]

    async def analyze_content(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Анализ контента с помощью LLM"""
        database_id = arguments.get("database_id")
        analysis_type = arguments.get("analysis_type", "categorization")
        limit = arguments.get("limit", 10)
        
        logger.info(f"[MCP] ANALYZE_CONTENT: database_id={database_id}, type={analysis_type}")
        
        try:
            # Проверяем что database_id не None
            if not database_id:
                return [{"success": False, "error": "Error: database_id is required"}]
            
            # Получаем страницы для анализа
            pages = []
            next_cursor = None
            while True:
                kwargs = dict(database_id=database_id, page_size=100)
                if next_cursor:
                    kwargs["start_cursor"] = next_cursor
                response = await self.client.databases.query(**kwargs)
                batch = response.get("results", [])
                pages.extend(batch)
                if not response.get("has_more"):
                    break
                next_cursor = response.get("next_cursor")
            
            result = {
                "database_id": database_id,
                "analysis_type": analysis_type,
                "pages_analyzed": len(pages),
                "analysis": f"Анализ {analysis_type} для {len(pages)} страниц"
            }
            
            return [result]
        except Exception as e:
            logger.error(f"[MCP] ERROR ANALYZE_CONTENT: {e}")
            return [{"success": False, "error": str(e)}]

    async def analyze_notion_completeness(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Аналитика базы: completeness, freshness, orphan, дубли, топ-теги/направления"""
        database_id = arguments.get("database_id", self.tasks_db_id)
        freshness_days = arguments.get("freshness_days", 14)
        logger.info(f"[MCP] ANALYZE_COMPLETENESS: db={database_id}, freshness_days={freshness_days}")
        try:
            pages = []
            next_cursor = None
            batch_num = 0
            while True:
                kwargs = dict(database_id=database_id, page_size=100)
                if next_cursor:
                    kwargs["start_cursor"] = next_cursor
                response = await self.client.databases.query(**kwargs)
                batch = response.get("results", [])
                pages.extend(batch)
                batch_num += 1
                progress_logger.info(f"[MCP] Загрузка: {len(pages)} страниц (батч {batch_num})...")
                if not response.get("has_more"):
                    break
                next_cursor = response.get("next_cursor")
            now = datetime.now(UTC)
            total = len(pages)
            filled = 0
            fresh = 0
            orphans = 0
            dups = 0
            seen_titles = set()
            tag_counter = {}
            status_counter = {}
            category_counter = {}
            for idx, page in enumerate(pages, 1):
                try:
                    if not isinstance(page, dict):
                        logger.warning(f"[MCP] Skipping non-dict page: {page}")
                        continue
                    props = page.get("properties", {})
                    if not isinstance(props, dict):
                        logger.warning(f"[MCP] Skipping page with non-dict properties: {page}")
                        continue
                    title = ""
                    # Notion title property detection
                    for k, v in props.items():
                        if isinstance(v, dict) and v.get("type") == "title":
                            title = "".join([t.get("plain_text", "") for t in v.get("title", []) if isinstance(t, dict)])
                            break
                    desc = ""
                    for k, v in props.items():
                        if isinstance(v, dict) and v.get("type") == "rich_text":
                            desc = "".join([t.get("plain_text", "") for t in v.get("rich_text", []) if isinstance(t, dict)])
                            break
                    if title and desc:
                        filled += 1
                    # Freshness by last_edited_time
                    last_edited = page.get("last_edited_time")
                    if last_edited:
                        try:
                            dt = datetime.fromisoformat(last_edited.replace("Z", "+00:00")).astimezone(UTC)
                            if (now - dt).days <= freshness_days:
                                fresh += 1
                        except Exception as e:
                            logger.warning(f"[MCP] Bad date: {last_edited} {e}")
                    # Orphan: нет ссылок/тегов/статуса
                    tags = []
                    for k, v in props.items():
                        if isinstance(v, dict) and v.get("type") == "multi_select":
                            tags = v.get("multi_select", [])
                            for tag in tags:
                                if isinstance(tag, dict):
                                    tag_name = tag.get("name")
                                    if tag_name:
                                        tag_counter[tag_name] = tag_counter.get(tag_name, 0) + 1
                            break
                    status = None
                    for k, v in props.items():
                        if isinstance(v, dict) and v.get("type") == "select":
                            status_val = v.get("select", {})
                            if isinstance(status_val, dict):
                                status = status_val.get("name")
                                if status:
                                    status_counter[status] = status_counter.get(status, 0) + 1
                            break
                    # Категории/направления (если есть поле category/direction/topic/area)
                    for k, v in props.items():
                        if (
                            isinstance(v, dict)
                            and k.lower() in ("category", "категория", "direction", "topic", "area", "направление")
                            and v.get("type") in ("select", "multi_select")
                        ):
                            vals = []
                            if v.get("type") == "select":
                                val = v.get("select", {})
                                if isinstance(val, dict):
                                    name = val.get("name")
                                    if name:
                                        vals = [name]
                            else:
                                vals = [x.get("name") for x in v.get("multi_select", []) if isinstance(x, dict) and x.get("name")]
                            for cat in vals:
                                category_counter[cat] = category_counter.get(cat, 0) + 1
                    if not tags and not status:
                        orphans += 1
                    # Дубли по title
                    if title in seen_titles:
                        dups += 1
                    else:
                        seen_titles.add(title)
                    if idx % 200 == 0:
                        progress_logger.info(f"[MCP] Анализировано {idx} страниц из {total}...")
                except Exception as e:
                    logger.warning(f"[MCP] Skipping page due to error: {e} | page: {page}")
            def top_n(counter, n=5):
                return sorted(counter.items(), key=lambda x: -x[1])[:n]
            summary = {
                "database_id": database_id,
                "total": total,
                "filled": filled,
                "filled_percent": round(100*filled/total,1) if total else 0,
                "fresh": fresh,
                "fresh_percent": round(100*fresh/total,1) if total else 0,
                "orphans": orphans,
                "orphans_percent": round(100*orphans/total,1) if total else 0,
                "dups": dups,
                "dups_percent": round(100*dups/total,1) if total else 0,
                "top_tags": top_n(tag_counter),
                "top_status": top_n(status_counter),
                "top_categories": top_n(category_counter),
            }
            md = f"""
# 📊 Аналитика базы {database_id}
- Всего записей: {total}
- Заполнено (title+desc): {filled} ({summary['filled_percent']}%)
- Свежих (изм. < {freshness_days}д): {fresh} ({summary['fresh_percent']}%)
- Orphan (нет тегов/статуса): {orphans} ({summary['orphans_percent']}%)
- Дубли по title: {dups} ({summary['dups_percent']}%)
- Топ теги: {summary['top_tags']}
- Топ статусы: {summary['top_status']}
- Топ категории/направления: {summary['top_categories']}
"""
            return [{"success": True, "analysis": md.strip()}]
        except Exception as e:
            logger.error(f"[MCP] ERROR ANALYZE_COMPLETENESS: {e}")
            return [{"success": False, "error": str(e)}]

    async def clean_notion_ideas(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Автоматическая чистка и улучшение базы идей"""
        database_id = arguments.get("database_id", self.tasks_db_id)
        logger.info(f"[MCP] CLEAN_IDEAS: database_id={database_id}")
        pages = []
        next_cursor = None
        seen_titles = set()
        dups, orphans, improved, reviewed, archived = 0, 0, 0, 0, 0
        batch_num = 0
        # 1. Сбор всех страниц
        while True:
            kwargs = dict(database_id=database_id, page_size=100)
            if next_cursor:
                kwargs["start_cursor"] = next_cursor
            response = await self.client.databases.query(**kwargs)
            batch = response.get("results", [])
            pages.extend(batch)
            batch_num += 1
            progress_logger.info(f"[MCP] CLEAN: загружено {len(pages)} страниц (батч {batch_num})...")
            if not response.get("has_more"):
                break
            next_cursor = response.get("next_cursor")
        # 2. Обработка
        for idx, page in enumerate(pages, 1):
            if not isinstance(page, dict):
                progress_logger.warning(f"[MCP] CLEAN: битая страница idx={idx}, page={page}")
                continue
            props = page.get("properties")
            if not isinstance(props, dict):
                progress_logger.warning(f"[MCP] CLEAN: битые properties idx={idx}, page_id={page.get('id')}")
                continue
            page_id = page.get("id")
            title = ""
            desc = ""
            tags = []
            status = None
            # Title
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "title":
                    title = "".join([t.get("plain_text", "") for t in v.get("title", []) if isinstance(t, dict)])
                    break
            # Desc
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "rich_text":
                    desc = "".join([t.get("plain_text", "") for t in v.get("rich_text", []) if isinstance(t, dict)])
                    break
            # Tags
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "multi_select":
                    tags = [tag.get("name") for tag in v.get("multi_select", []) if isinstance(tag, dict)]
                    break
            # Status
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "select":
                    sel = v.get("select")
                    if isinstance(sel, dict):
                        status = sel.get("name")
                    break
            # Дубликаты
            norm_title = title.strip().lower()
            if norm_title and norm_title in seen_titles:
                dups += 1
                # Архивируем дубли
                await self.update_page({"page_id": page_id, "status": "Архив", "tags": ["#dup"]})
                continue
            if norm_title:
                seen_titles.add(norm_title)
            # Orphan
            if not tags and not status:
                orphans += 1
                await self.update_page({"page_id": page_id, "status": "Архив", "tags": ["#orphan"]})
                continue
            # Мусорные title
            if not title or title.lower().startswith(("img_", "https://", "file", "photo", "video", "отправлено", "переслано")):
                if desc:
                    title = desc[:40].strip()
                    improved += 1
                    await self.update_page({"page_id": page_id, "title": title})
                else:
                    archived += 1
                    await self.update_page({"page_id": page_id, "status": "Архив", "tags": ["#bad_title"]})
                    continue
            # Очистка desc
            if desc:
                import re
                clean_desc = re.sub(r"[#@][\w-]+", "", desc)
                clean_desc = re.sub(r"https?://\S+", "", clean_desc)
                clean_desc = re.sub(r"[\s\n]+", " ", clean_desc).strip()
                if clean_desc != desc:
                    improved += 1
                    await self.update_page({"page_id": page_id, "description": clean_desc})
            # Автотеги
            auto_tags = set(tags)
            for word, tag in [("instagram", "Instagram"), ("smm", "SMM"), ("бренд", "Бренд"), ("дизайн", "Дизайн"), ("видео", "Видео"), ("фото", "Фото")]:
                if word in (title+desc).lower() and tag not in auto_tags:
                    auto_tags.add(tag)
            if set(tags) != auto_tags:
                await self.update_page({"page_id": page_id, "tags": list(auto_tags)})
            # Статусы
            if status is None:
                await self.update_page({"page_id": page_id, "status": "Идея"})
            # Сложные случаи
            if not title or not desc:
                reviewed += 1
                await self.update_page({"page_id": page_id, "tags": ["#review"]})
        summary = f"# MCP CLEAN IDEAS\nВсего: {len(pages)}\nДубли: {dups}\nOrphan: {orphans}\nУлучшено: {improved}\nВ архив: {archived}\nТребует доработки: {reviewed}"
        progress_logger.info(summary)
        return [{"success": True, "clean_summary": summary}]

    async def restore_idea_duplicates(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Восстановление дублей из архива (убрать тег #dup, вернуть статус Идея)"""
        database_id = arguments.get("database_id", self.tasks_db_id)
        logger.info(f"[MCP] RESTORE_DUPLICATES: database_id={database_id}")
        pages = []
        next_cursor = None
        batch_num = 0
        restored = 0
        # 1. Сбор всех страниц
        while True:
            kwargs = dict(database_id=database_id, page_size=100)
            if next_cursor:
                kwargs["start_cursor"] = next_cursor
            response = await self.client.databases.query(**kwargs)
            batch = response.get("results", [])
            pages.extend(batch)
            batch_num += 1
            progress_logger.info(f"[MCP] RESTORE: загружено {len(pages)} страниц (батч {batch_num})...")
            if not response.get("has_more"):
                break
            next_cursor = response.get("next_cursor")
        # 2. Восстановление
        for idx, page in enumerate(pages, 1):
            if not isinstance(page, dict):
                continue
            props = page.get("properties")
            if not isinstance(props, dict):
                continue
            page_id = page.get("id")
            tags = []
            status = None
            # Tags
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "multi_select":
                    tags = [tag.get("name") for tag in v.get("multi_select", []) if isinstance(tag, dict)]
                    break
            # Status
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "select":
                    sel = v.get("select")
                    if isinstance(sel, dict):
                        status = sel.get("name")
                    break
            if status == "Архив" and "#dup" in tags:
                new_tags = [t for t in tags if t != "#dup"]
                await self.update_page({"page_id": page_id, "status": "Идея", "tags": new_tags})
                restored += 1
        summary = f"# MCP RESTORE DUPLICATES\nВосстановлено: {restored}"
        progress_logger.info(summary)
        return [{"success": True, "restore_summary": summary}]

    async def add_yadisk_image_as_notion_cover(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ставит картинку с Яндекс.Диска как cover и как файл в идею Notion"""
        from services.media_cover_manager import MediaCoverManager
        yadisk_url = arguments.get("yadisk_url")
        page_id = arguments.get("page_id")
        if not yadisk_url or not page_id:
            return [{"success": False, "error": "yadisk_url и page_id обязательны"}]
        mgr = MediaCoverManager()
        # Получаем preview/public_url
        try:
            meta = mgr.yadisk.get_meta(yadisk_url)
            if meta['type'] != 'file':
                return [{"success": False, "error": "Ссылка не на файл Яндекс.Диска"}]
            preview_url = meta.get('preview') or meta.get('public_url')
            if not preview_url:
                return [{"success": False, "error": "Нет preview/public_url у файла"}]
        except Exception as e:
            return [{"success": False, "error": f"Ошибка получения метаданных Яндекс.Диска: {e}"}]
        # Обновляем страницу в Notion: cover и поле 'Файл'
        try:
            await mgr.notion.pages.update(
                page_id=page_id,
                cover={
                    "type": "external",
                    "external": {"url": preview_url}
                },
                properties={
                    'Файл': {
                        'type': 'files',
                        'files': [
                            {'type': 'external', 'name': meta.get('name', 'image.jpg'), 'external': {'url': preview_url}}
                        ]
                    }
                }
            )
            return [{"success": True, "message": f"Картинка {preview_url} установлена как cover и файл для {page_id}"}]
        except Exception as e:
            return [{"success": False, "error": f"Ошибка обновления Notion: {e}"}]

    # ------------------------------------------------------------------
    # SCHEMA CACHING
    # ------------------------------------------------------------------

    async def _get_database_schema(self, database_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Возвращает схему базы данных Notion с кэшированием.

        1. Вначале пытается взять из памяти (если не истёк TTL).
        2. Затем из файлового кэша (если актуально).
        3. И только потом делает запрос к Notion.
        """

        now_ts = time.time()

        # In-memory cache
        if (
            not force_refresh
            and database_id in self.database_cache
            and (now_ts - self.cache_timestamp.get(database_id, 0)) < self.cache_ttl
        ):
            logger.debug(f"[MCP] Schema cache hit (memory) for {database_id}")
            return self.database_cache[database_id]

        # File cache
        cache_file = self.schema_cache_dir / f"{database_id}.json"
        if (
            not force_refresh
            and cache_file.exists()
            and (now_ts - cache_file.stat().st_mtime) < self.cache_ttl
        ):
            logger.debug(f"[MCP] Schema cache hit (file) for {database_id}")
            with cache_file.open("r", encoding="utf-8") as f:
                schema = json.load(f)
            # Обновляем память и timestamp
            self.database_cache[database_id] = schema
            self.cache_timestamp[database_id] = now_ts
            return schema

        # Fallback → запрос в Notion
        logger.info(f"[MCP] Fetching schema from Notion for {database_id}")
        schema = await self.client.databases.retrieve(database_id=database_id)

        # Записываем в кэш
        try:
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(schema, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"[MCP] Cannot write schema cache file {cache_file}: {e}")

        self.database_cache[database_id] = schema
        self.cache_timestamp[database_id] = now_ts

        return schema

    async def get_notion_schema(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Возвращает полную схему базы данных Notion (из кэша или с обновлением)."""
        logger.info(f"[MCP] GET_NOTION_SCHEMA: {arguments}")
        try:
            database_id = arguments["database_id"]
            force_refresh = arguments.get("force_refresh", False)
            schema = await self._get_database_schema(database_id, force_refresh=force_refresh)
            return [{"success": True, "schema": schema}]
        except Exception as e:
            logger.error(f"[MCP] ERROR GET_NOTION_SCHEMA: {e}")
            return [{"success": False, "error": str(e)}]

    async def get_users(self) -> List[dict]:
        """Получить список пользователей Notion"""
        try:
            response = await self.client.users.list()
            return response.get("results", [])
        except Exception as e:
            logger.error(f"[MCP] ERROR GET_USERS: {e}")
            return []

    # Новые методы с интеграцией схем
    async def get_schema_database_info(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить информацию о базе данных из централизованных схем"""
        database_name = arguments.get("database_name")
        
        if not database_name:
            return [{"success": False, "error": "Не указано имя базы данных"}]
        
        schema = get_database_schema(database_name)
        if not schema:
            return [{"success": False, "error": f"База данных '{database_name}' не найдена в схемах"}]
        
        result = {
            "success": True,
            "database_name": database_name,
            "name": schema.name,
            "database_id": schema.database_id,
            "description": schema.description,
            "properties": list(schema.properties.keys()),
            "status_options": schema.status_options,
            "multi_select_options": schema.multi_select_options,
            "relations": schema.relations
        }
        
        return [result]

    async def get_schema_options(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить доступные опции для поля из схемы"""
        database_name = arguments.get("database_name")
        property_name = arguments.get("property_name")
        
        if not database_name or not property_name:
            return [{"success": False, "error": "Не указаны database_name или property_name"}]
        
        schema = get_database_schema(database_name)
        if not schema:
            return [{"success": False, "error": f"База данных '{database_name}' не найдена в схемах"}]
        
        if property_name not in schema.properties:
            return [{"success": False, "error": f"Поле '{property_name}' не найдено в схеме"}]
        
        prop_type = schema.properties[property_name].get("type")
        result = {
            "success": True,
            "database_name": database_name,
            "property_name": property_name,
            "property_type": prop_type,
            "options": {}
        }
        
        if prop_type == "status" and property_name in schema.status_options:
            result["options"]["status"] = schema.status_options[property_name]
        elif prop_type == "select" and property_name in schema.select_options:
            result["options"]["select"] = schema.select_options[property_name]
        elif prop_type == "multi_select" and property_name in schema.multi_select_options:
            result["options"]["multi_select"] = schema.multi_select_options[property_name]
        
        return [result]

    async def validate_schema_property(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Проверить валидность значения для поля по схеме"""
        database_name = arguments.get("database_name")
        property_name = arguments.get("property_name")
        value = arguments.get("value")
        
        if not all([database_name, property_name, value]):
            return [{"success": False, "error": "Не указаны database_name, property_name или value"}]
        
        is_valid = validate_property_value(database_name, property_name, value)
        
        result = {
            "success": True,
            "database_name": database_name,
            "property_name": property_name,
            "value": value,
            "is_valid": is_valid
        }
        
        return [result]

    async def list_schema_databases(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Список всех доступных баз данных из централизованных схем"""
        databases = []
        
        for db_name, schema in DATABASE_SCHEMAS.items():
            databases.append({
                "name": db_name,
                "display_name": schema.name,
                "database_id": schema.database_id,
                "description": schema.description,
                "properties_count": len(schema.properties)
            })
        
        return [{"success": True, "databases": databases}]

    async def get_kpi_metrics(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить KPI метрики по сотруднику/периоду/типу"""
        employee_name = arguments.get("employee_name")
        kpi_type = arguments.get("kpi_type")
        period_start = arguments.get("period_start")
        period_end = arguments.get("period_end")
        include_formulas = arguments.get("include_formulas", True)
        
        logger.info(f"[MCP] GET_KPI_METRICS: employee_name={employee_name}, kpi_type={kpi_type}, period_start={period_start}, period_end={period_end}")
        
        try:
            # Получаем KPI базу из схем
            kpi_db_id = get_database_id("kpi")
            if not kpi_db_id:
                return [{"success": False, "error": "KPI база не найдена в схемах"}]
            
            # Строим фильтр для запроса
            filter_conditions = []
            
            if employee_name:
                # Для фильтрации по людям нужно использовать UUID или правильный синтаксис
                # Пока убираем фильтр по сотруднику, будем фильтровать на уровне приложения
                logger.info(f"[MCP] Фильтр по сотруднику '{employee_name}' будет применен на уровне приложения")
            
            if kpi_type:
                filter_conditions.append({
                    "property": "Тип KPI",
                    "select": {"equals": kpi_type}
                })
            
            if period_start or period_end:
                date_filter = {"property": "Период", "date": {}}
                if period_start:
                    date_filter["date"]["on_or_after"] = period_start
                if period_end:
                    date_filter["date"]["on_or_before"] = period_end
                filter_conditions.append(date_filter)
            
            # Выполняем запрос
            query_kwargs = {"database_id": kpi_db_id}
            if filter_conditions:
                if len(filter_conditions) == 1:
                    query_kwargs["filter"] = filter_conditions[0]
                else:
                    query_kwargs["filter"] = {"and": filter_conditions}
            
            response = await self.client.databases.query(**query_kwargs)
            pages = response.get("results", [])
            
            # Обрабатываем результаты
            metrics = []
            for page in pages:
                properties = page.get("properties", {})
                
                # Фильтрация по сотруднику на уровне приложения
                if employee_name:
                    page_employees = self._get_property_people(properties, "Сотрудник")
                    if not any(employee_name.lower() in emp.lower() for emp in page_employees):
                        continue
                
                metric = {
                    "id": page["id"],
                    "name": self._get_property_text(properties, "Name"),
                    "kpi_type": self._get_property_select(properties, "Тип KPI"),
                    "target_value": self._get_property_number(properties, "Целевое значение"),
                    "current_value": self._get_property_number(properties, "Текущее значение"),
                    "achievement_percent": self._get_property_number(properties, "Достижение (%)"),
                    "content_type": self._get_property_multi_select(properties, "Тип контента"),
                    "metric_type": self._get_property_select(properties, "Метрика"),
                    "status": self._get_property_select(properties, "Статус"),
                    "period": self._get_property_date(properties, "Период"),
                    "employee": self._get_property_people(properties, "Сотрудник"),
                    "formula": self._get_property_text(properties, "Формула расчёта") if include_formulas else None,
                    "comment": self._get_property_text(properties, "Комментарий")
                }
                
                # Добавляем специфичные метрики по типу контента
                if "Карточки товаров" in metric["content_type"]:
                    metric.update({
                        "views": self._get_property_number(properties, "Просмотры"),
                        "clicks": self._get_property_number(properties, "Клики"),
                        "conversion": self._get_property_number(properties, "Конверсия"),
                        "sales": self._get_property_number(properties, "Продажи"),
                        "cart_additions": self._get_property_number(properties, "Добавления в корзину")
                    })
                elif "YouTube" in metric["content_type"]:
                    metric.update({
                        "views": self._get_property_number(properties, "Просмотры"),
                        "engagement": self._get_property_number(properties, "Вовлечённость"),
                        "ctr": self._get_property_number(properties, "CTR")
                    })
                elif "Соцсети" in metric["content_type"]:
                    metric.update({
                        "reach": self._get_property_number(properties, "Охват"),
                        "engagement": self._get_property_number(properties, "Вовлечённость"),
                        "clicks": self._get_property_number(properties, "Клики")
                    })
                elif "Полиграфия" in metric["content_type"]:
                    metric.update({
                        "execution_time": self._get_property_number(properties, "Время выполнения"),
                        "quality": self._get_property_number(properties, "Качество выполнения"),
                        "revisions": self._get_property_number(properties, "Количество правок")
                    })
                
                metrics.append(metric)
            
            result = {
                "success": True,
                "metrics": metrics,
                "total_count": len(metrics),
                "filters_applied": {
                    "employee_name": employee_name,
                    "kpi_type": kpi_type,
                    "period_start": period_start,
                    "period_end": period_end
                }
            }
            
            return [result]
            
        except Exception as e:
            logger.error(f"[MCP] ERROR GET_KPI_METRICS: {e}")
            return [{"success": False, "error": str(e)}]

    async def calculate_bonus(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Рассчитать бонус по формуле эффективности"""
        employee_name = arguments.get("employee_name")
        base_salary = arguments.get("base_salary", 100000)
        period = arguments.get("period", "месяц")
        
        logger.info(f"[MCP] CALCULATE_BONUS: employee_name={employee_name}, base_salary={base_salary}, period={period}")
        
        try:
            if not employee_name:
                return [{"success": False, "error": "Не указано имя сотрудника"}]
            
            # Получаем KPI метрики для сотрудника
            kpi_result = await self.get_kpi_metrics({
                "employee_name": employee_name,
                "period_start": "2025-01-01",  # Можно сделать динамическим
                "period_end": "2025-12-31"
            })
            
            if not kpi_result[0]["success"]:
                return kpi_result
            
            metrics = kpi_result[0]["metrics"]
            
            # Рассчитываем эффективность по формуле из документации
            efficiency = 0.0
            quality = 0.0
            overdue_tasks = 0.0
            
            for metric in metrics:
                if metric["kpi_type"] == "Эффективность":
                    efficiency = metric["current_value"] or 0.0
                elif metric["kpi_type"] == "Качество":
                    quality = metric["current_value"] or 0.0
                elif metric["kpi_type"] == "% выполнено":
                    # Просрочки = 100% - % выполнено
                    overdue_tasks = 1.0 - ((metric["current_value"] or 0.0) / 100.0)
            
            # Формула бонуса из документации
            bonus_multiplier = (1 + efficiency * 0.2 + quality * 0.3 - overdue_tasks * 0.3)
            bonus = base_salary * bonus_multiplier
            
            result = {
                "success": True,
                "employee_name": employee_name,
                "base_salary": base_salary,
                "efficiency": efficiency,
                "quality": quality,
                "overdue_tasks": overdue_tasks,
                "bonus_multiplier": bonus_multiplier,
                "bonus": bonus,
                "period": period,
                "formula": "бонус = base_salary * (1 + эффективность*0.2 + качество*0.3 − просрочки*0.3)"
            }
            
            return [result]
            
        except Exception as e:
            logger.error(f"[MCP] ERROR CALCULATE_BONUS: {e}")
            return [{"success": False, "error": str(e)}]

    async def get_performance_data(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить данные эффективности по проектам/материалам"""
        content_type = arguments.get("content_type")
        metric_type = arguments.get("metric_type")
        date_from = arguments.get("date_from")
        date_to = arguments.get("date_to")
        
        logger.info(f"[MCP] GET_PERFORMANCE_DATA: content_type={content_type}, metric_type={metric_type}, date_from={date_from}, date_to={date_to}")
        
        try:
            # Получаем KPI базу
            kpi_db_id = get_database_id("kpi")
            if not kpi_db_id:
                return [{"success": False, "error": "KPI база не найдена в схемах"}]
            
            # Строим фильтр
            filter_conditions = []
            
            if content_type:
                filter_conditions.append({
                    "property": "Тип контента",
                    "multi_select": {"contains": content_type}
                })
            
            if metric_type:
                filter_conditions.append({
                    "property": "Метрика",
                    "select": {"equals": metric_type}
                })
            
            if date_from or date_to:
                date_filter = {"property": "Период", "date": {}}
                if date_from:
                    date_filter["date"]["on_or_after"] = date_from
                if date_to:
                    date_filter["date"]["on_or_before"] = date_to
                filter_conditions.append(date_filter)
            
            # Выполняем запрос
            query_kwargs = {"database_id": kpi_db_id}
            if filter_conditions:
                if len(filter_conditions) == 1:
                    query_kwargs["filter"] = filter_conditions[0]
                else:
                    query_kwargs["filter"] = {"and": filter_conditions}
            
            response = await self.client.databases.query(**query_kwargs)
            pages = response.get("results", [])
            
            # Группируем данные по типам контента
            performance_data = {
                "Карточки товаров": {"metrics": [], "total": 0},
                "YouTube": {"metrics": [], "total": 0},
                "Соцсети": {"metrics": [], "total": 0},
                "Полиграфия": {"metrics": [], "total": 0},
                "Концепты": {"metrics": [], "total": 0},
                "Гайды": {"metrics": [], "total": 0}
            }
            
            for page in pages:
                properties = page.get("properties", {})
                content_types = self._get_property_multi_select(properties, "Тип контента")
                
                for content_type_name in content_types:
                    if content_type_name in performance_data:
                        metric = {
                            "name": self._get_property_text(properties, "Name"),
                            "current_value": self._get_property_number(properties, "Текущее значение"),
                            "target_value": self._get_property_number(properties, "Целевое значение"),
                            "achievement_percent": self._get_property_number(properties, "Достижение (%)"),
                            "metric_type": self._get_property_select(properties, "Метрика"),
                            "period": self._get_property_date(properties, "Период")
                        }
                        
                        performance_data[content_type_name]["metrics"].append(metric)
                        performance_data[content_type_name]["total"] += 1
            
            # Убираем пустые категории
            performance_data = {k: v for k, v in performance_data.items() if v["total"] > 0}
            
            result = {
                "success": True,
                "performance_data": performance_data,
                "filters_applied": {
                    "content_type": content_type,
                    "metric_type": metric_type,
                    "date_from": date_from,
                    "date_to": date_to
                }
            }
            
            return [result]
            
        except Exception as e:
            logger.error(f"[MCP] ERROR GET_PERFORMANCE_DATA: {e}")
            return [{"success": False, "error": str(e)}]

    async def update_kpi_record(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Обновить или создать KPI запись"""
        kpi_name = arguments.get("kpi_name")
        kpi_type = arguments.get("kpi_type")
        target_value = arguments.get("target_value")
        current_value = arguments.get("current_value")
        content_type = arguments.get("content_type")
        period = arguments.get("period")
        comment = arguments.get("comment")
        
        logger.info(f"[MCP] UPDATE_KPI_RECORD: kpi_name={kpi_name}, kpi_type={kpi_type}, target_value={target_value}, current_value={current_value}")
        
        try:
            if not kpi_name or not kpi_type:
                return [{"success": False, "error": "Не указаны обязательные поля kpi_name и kpi_type"}]
            
            # Получаем KPI базу
            kpi_db_id = get_database_id("kpi")
            if not kpi_db_id:
                return [{"success": False, "error": "KPI база не найдена в схемах"}]
            
            # Подготавливаем свойства для создания/обновления
            properties = {
                "Name": {
                    "title": [{"text": {"content": kpi_name}}]
                },
                "Тип KPI": {
                    "select": {"name": kpi_type}
                }
            }
            
            if target_value is not None:
                properties["Целевое значение"] = {"number": target_value}
            
            if current_value is not None:
                properties["Текущее значение"] = {"number": current_value}
            
            if content_type:
                # Обрабатываем content_type как строку или список
                if isinstance(content_type, str):
                    content_types = [ct.strip() for ct in content_type.split(",")]
                else:
                    content_types = content_type
                
                properties["Тип контента"] = {
                    "multi_select": [{"name": ct} for ct in content_types]
                }
            
            if period:
                properties["Период"] = {"date": {"start": period}}
            
            if comment:
                properties["Комментарий"] = {
                    "rich_text": [{"text": {"content": comment}}]
                }
            
            # Создаем новую запись
            response = await self.client.pages.create(
                parent={"database_id": kpi_db_id},
                properties=properties
            )
            
            result = {
                "success": True,
                "message": f"KPI запись '{kpi_name}' создана",
                "page_id": response["id"],
                "url": response["url"],
                "properties": properties
            }
            
            return [result]
            
        except Exception as e:
            logger.error(f"[MCP] ERROR UPDATE_KPI_RECORD: {e}")
            return [{"success": False, "error": str(e)}]

    async def safe_create_page(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Безопасное создание страницы с валидацией и post-check"""
        try:
            safe_ops = SafeDatabaseOperations()
            database_name = arguments.get("database_name")
            properties = arguments.get("properties", {})
            
            if not database_name or not properties:
                return [{"success": False, "error": "Не указаны database_name или properties"}]
            
            result = await safe_ops.safe_create_page(database_name, properties)
            return [result]
            
        except Exception as e:
            logger.error(f"Ошибка safe_create_page: {e}")
            return [{"success": False, "error": str(e)}]
    
    async def safe_update_page(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Безопасное обновление страницы с валидацией и post-check"""
        try:
            safe_ops = SafeDatabaseOperations()
            page_id = arguments.get("page_id")
            properties = arguments.get("properties", {})
            
            if not page_id or not properties:
                return [{"success": False, "error": "Не указаны page_id или properties"}]
            
            result = await safe_ops.safe_update_page(page_id, properties)
            return [result]
            
        except Exception as e:
            logger.error(f"Ошибка safe_update_page: {e}")
            return [{"success": False, "error": str(e)}]
    
    async def safe_bulk_create(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Безопасное массовое создание с валидацией"""
        try:
            safe_ops = SafeDatabaseOperations()
            database_name = arguments.get("database_name")
            properties_list = arguments.get("properties_list", [])
            
            if not database_name or not properties_list:
                return [{"success": False, "error": "Не указаны database_name или properties_list"}]
            
            result = await safe_ops.safe_bulk_create(database_name, properties_list)
            return [result]
            
        except Exception as e:
            logger.error(f"Ошибка safe_bulk_create: {e}")
            return [{"success": False, "error": str(e)}]

    async def add_select_option(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Добавить новое значение в select поле"""
        try:
            safe_ops = SafeDatabaseOperations()
            database_id = arguments.get("database_id")
            property_name = arguments.get("property_name")
            new_option = arguments.get("new_option")
            
            if not all([database_id, property_name, new_option]):
                return [{"success": False, "error": "Не указаны database_id, property_name или new_option"}]
            
            result = await safe_ops.add_select_option(database_id, property_name, new_option)
            return [result]
            
        except Exception as e:
            logger.error(f"Ошибка add_select_option: {e}")
            return [{"success": False, "error": str(e)}]

    async def add_multi_select_option(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Добавить новое значение в multi_select поле"""
        try:
            safe_ops = SafeDatabaseOperations()
            database_id = arguments.get("database_id")
            property_name = arguments.get("property_name")
            new_option = arguments.get("new_option")
            
            if not all([database_id, property_name, new_option]):
                return [{"success": False, "error": "Не указаны database_id, property_name или new_option"}]
            
            result = await safe_ops.add_multi_select_option(database_id, property_name, new_option)
            return [result]
            
        except Exception as e:
            logger.error(f"Ошибка add_multi_select_option: {e}")
            return [{"success": False, "error": str(e)}]

    async def safe_create_with_auto_options(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Создать запись с автоматическим добавлением новых значений в select/multi_select поля"""
        try:
            safe_ops = SafeDatabaseOperations()
            database_id = arguments.get("database_id")
            properties = arguments.get("properties", {})
            
            if not database_id or not properties:
                return [{"success": False, "error": "Не указаны database_id или properties"}]
            
            result = await safe_ops.safe_create_page_with_auto_options(database_id, properties)
            return [result]
            
        except Exception as e:
            logger.error(f"Ошибка safe_create_with_auto_options: {e}")
            return [{"success": False, "error": str(e)}]

    async def add_multiple_options(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Добавить несколько новых значений в select или multi_select поле"""
        try:
            safe_ops = SafeDatabaseOperations()
            database_id = arguments.get("database_id")
            property_name = arguments.get("property_name")
            new_options = arguments.get("new_options", [])
            field_type = arguments.get("field_type", "select")
            
            if not all([database_id, property_name, new_options]):
                return [{"success": False, "error": "Не указаны database_id, property_name или new_options"}]
            
            result = await safe_ops.add_multiple_options(database_id, property_name, new_options, field_type)
            return [result]
            
        except Exception as e:
            logger.error(f"Ошибка add_multiple_options: {e}")
            return [{"success": False, "error": str(e)}]

    def _get_property_text(self, properties: Dict[str, Any], property_name: str) -> str:
        """Получить текстовое значение свойства"""
        prop = properties.get(property_name, {})
        if prop.get("type") == "title":
            return "".join([text.get("text", {}).get("content", "") for text in prop.get("title", [])])
        elif prop.get("type") == "rich_text":
            return "".join([text.get("text", {}).get("content", "") for text in prop.get("rich_text", [])])
        return ""

    def _get_property_number(self, properties: Dict[str, Any], property_name: str) -> Optional[float]:
        """Получить числовое значение свойства"""
        prop = properties.get(property_name, {})
        if prop.get("type") == "number":
            return prop.get("number")
        return None

    def _get_property_select(self, properties: Dict[str, Any], property_name: str) -> Optional[str]:
        """Получить значение select свойства"""
        prop = properties.get(property_name, {})
        if prop.get("type") == "select":
            select_value = prop.get("select", {})
            return select_value.get("name") if select_value else None
        return None

    def _get_property_multi_select(self, properties: Dict[str, Any], property_name: str) -> List[str]:
        """Получить значения multi_select свойства"""
        prop = properties.get(property_name, {})
        if prop.get("type") == "multi_select":
            return [item.get("name", "") for item in prop.get("multi_select", [])]
        return []

    def _get_property_date(self, properties: Dict[str, Any], property_name: str) -> Optional[str]:
        """Получить значение date свойства"""
        prop = properties.get(property_name, {})
        if prop.get("type") == "date":
            date_value = prop.get("date", {})
            return date_value.get("start") if date_value else None
        return None

    def _get_property_people(self, properties: Dict[str, Any], property_name: str) -> List[str]:
        """Получить значения people свойства"""
        prop = properties.get(property_name, {})
        if prop.get("type") == "people":
            return [person.get("name", "") for person in prop.get("people", [])]
        return []

async def main():
    """Основная функция запуска MCP сервера"""
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

async def cli_main():
    """CLI режим для прямых команд"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Notion MCP Server CLI")
    parser.add_argument("command", help="Команда для выполнения")
    parser.add_argument("--database_id", help="ID базы данных")
    parser.add_argument("--limit", type=int, default=10, help="Лимит записей")
    parser.add_argument("--properties", help="JSON свойства")
    parser.add_argument("--properties_file", help="Файл с JSON свойствами")
    parser.add_argument("--filter_dict", help="JSON фильтр")
    
    args = parser.parse_args()
    
    server = NotionMCPServer()
    
    try:
        if args.command == "list_pages":
            if not args.database_id:
                print("❌ Ошибка: требуется --database_id")
                return
            
            pages = await server.get_pages(args.database_id, limit=args.limit)
            print(f"✅ Найдено {len(pages)} записей:")
            for i, page in enumerate(pages[:5], 1):
                title = server._get_property_text(page.get("properties", {}), "Name") or server._get_property_text(page.get("properties", {}), "Название") or server._get_property_text(page.get("properties", {}), "Задача") or "Без названия"
                print(f"  {i}. {title} (ID: {page.get('id', 'N/A')})")
        
        elif args.command == "safe_create_with_auto_options":
            if not args.database_id:
                print("❌ Ошибка: требуется --database_id")
                return
            
            properties = {}
            if args.properties:
                properties = json.loads(args.properties)
            elif args.properties_file:
                with open(args.properties_file, 'r', encoding='utf-8') as f:
                    properties = json.load(f)
            else:
                print("❌ Ошибка: требуется --properties или --properties_file")
                return
            
            result = await server.safe_create_with_auto_options({"database_id": args.database_id, "properties": properties})
            print(f"✅ Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        elif args.command == "get_database_info":
            if not args.database_id:
                print("❌ Ошибка: требуется --database_id")
                return
            
            result = await server.get_database_info({"database_id": args.database_id})
            print(f"✅ Информация о базе: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        else:
            print(f"❌ Неизвестная команда: {args.command}")
            print("Доступные команды: list_pages, safe_create_with_auto_options, get_database_info")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in ["--help", "-h"]:
        # CLI режим
        asyncio.run(cli_main())
    else:
        # MCP сервер режим
        asyncio.run(main()) 