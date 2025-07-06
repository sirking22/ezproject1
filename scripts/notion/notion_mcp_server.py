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
    validate_property_value
)

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

    async def get_pages(self, database_id: str, filter_dict: Optional[dict] = None) -> List[dict]:
        """Получить страницы из базы данных с опциональным фильтром"""
        try:
            kwargs = {"database_id": database_id}
            if filter_dict:
                kwargs["filter"] = filter_dict
            
            response = await self.client.databases.query(**kwargs)
            pages = response.get("results", [])
            
            # Пагинация для получения всех страниц
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
        return [{"success": False, "error": "Delete page not implemented yet"}]

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

if __name__ == "__main__":
    asyncio.run(main()) 