"""Notion service for interacting with Notion API."""
from typing import Dict, List, Optional, Any, Union
import asyncio
from datetime import datetime
import logging
from urllib.parse import urljoin

import aiohttp
from pydantic import ValidationError
from notion_client import AsyncClient

from ..base_service import BaseService
# Временно закомментируем проблемные импорты
# from ...models.notion_models import (
#     NotionPage,
#     NotionDatabase,
#     NotionBlock,
#     TextBlock,
#     TodoBlock,
#     HeadingBlock
# )
# from ...config import get_settings
# from .constants import PROPERTY_NAMES, SOCIAL_MEDIA_DB_ID, TEAM_DB_ID, KPI_DB_ID, TYPICAL_TASKS_DB_ID
# from src.models.task import Task
# from src.repositories.notion_repository import NotionTaskRepository

logger = logging.getLogger(__name__)

class NotionError(Exception):
    """Base exception for Notion service."""
    pass

# Временные заглушки для моделей
class NotionPage:
    def __init__(self, **kwargs):
        pass
    
    @classmethod
    def model_validate(cls, data):
        return cls(**data)

class NotionDatabase:
    def __init__(self, **kwargs):
        pass
    
    @classmethod
    def model_validate(cls, data):
        return cls(**data)

class NotionBlock:
    def __init__(self, **kwargs):
        pass

class TextBlock:
    def __init__(self, **kwargs):
        pass
    
    @classmethod
    def model_validate(cls, data):
        return cls(**data)

class TodoBlock:
    def __init__(self, **kwargs):
        pass
    
    @classmethod
    def model_validate(cls, data):
        return cls(**data)

class HeadingBlock:
    def __init__(self, **kwargs):
        pass
    
    @classmethod
    def model_validate(cls, data):
        return cls(**data)

class NotionTaskRepository:
    def __init__(self, client, database_id):
        self.client = client
        self.database_id = database_id

def get_settings():
    """Временная заглушка для настроек"""
    class Settings:
        def __init__(self):
            self.NOTION_TOKEN = None
            self.NOTION_DATABASES = {}
        
        def get_notion_headers(self):
            return {"Authorization": f"Bearer {self.NOTION_TOKEN}"}
    
    return Settings()

class NotionService(BaseService):
    """Service for interacting with Notion API."""
    
    def __init__(self):
        """Initialize service with configuration."""
        super().__init__()
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        self.databases = self.settings.NOTION_DATABASES
        self.client = AsyncClient(auth=self.settings.NOTION_TOKEN)
        self.task_repository = NotionTaskRepository(self.client, self.settings.NOTION_DATABASES.get("tasks", ""))
        
    async def initialize(self) -> None:
        """Initialize Notion client session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers=self.settings.get_notion_headers()
            )
        logger.info("Notion service initialized")
            
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        if self.session:
            await self.session.close()
            self.session = None
            
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make request to Notion API."""
        if not self.session:
            await self.initialize()
            
        url = urljoin("https://api.notion.com/v1/", endpoint)
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            raise NotionError(f"API request failed: {str(e)}")
            
    async def get_database(self, database_id: str) -> NotionDatabase:
        """Get database metadata."""
        try:
            data = await self._request("GET", f"databases/{database_id}")
            return NotionDatabase.model_validate(data)
        except ValidationError as e:
            logger.error(f"Invalid database data: {str(e)}")
            raise NotionError(f"Invalid database data: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting database: {str(e)}")
            raise
            
    async def query_database(
        self,
        database_id: str,
        filter_conditions: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> List[NotionPage]:
        """Query database with optional filters and sorting."""
        try:
            data = {
                "page_size": 100
            }
            if filter_conditions:
                data["filter"] = filter_conditions
            if sorts:
                data["sorts"] = sorts
                
            response = await self._request(
                "POST",
                f"databases/{database_id}/query",
                data
            )
            
            return [NotionPage.model_validate(page) for page in response["results"]]
        except ValidationError as e:
            logger.error(f"Invalid page data: {str(e)}")
            raise NotionError(f"Invalid page data: {str(e)}")
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            raise
            
    async def create_page(
        self,
        database_id: str,
        properties: Dict[str, Any],
        content: Optional[List[Dict]] = None
    ) -> NotionPage:
        """Create a new page in specified database."""
        try:
            data = {
                "parent": {"database_id": database_id},
                "properties": properties
            }
            if content:
                data["children"] = content
                
            response = await self._request("POST", "pages", data)
            return NotionPage.model_validate(response)
        except ValidationError as e:
            logger.error(f"Invalid page data: {str(e)}")
            raise NotionError(f"Invalid page data: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating page: {str(e)}")
            raise
            
    async def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any],
        archived: bool = False
    ) -> NotionPage:
        """Update an existing page."""
        try:
            data = {
                "properties": properties,
                "archived": archived
            }
            response = await self._request("PATCH", f"pages/{page_id}", data)
            return NotionPage.model_validate(response)
        except ValidationError as e:
            logger.error(f"Invalid page data: {str(e)}")
            raise NotionError(f"Invalid page data: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating page: {str(e)}")
            raise
            
    async def get_page_content(
        self,
        page_id: str
    ) -> List[Union[TextBlock, TodoBlock, HeadingBlock]]:
        """Get page content blocks."""
        try:
            response = await self._request("GET", f"blocks/{page_id}/children")
            blocks = []
            
            for block_data in response["results"]:
                block_type = block_data["type"]
                if block_type == "paragraph":
                    blocks.append(TextBlock.model_validate(block_data))
                elif block_type == "to_do":
                    blocks.append(TodoBlock.model_validate(block_data))
                elif block_type in ["heading_1", "heading_2", "heading_3"]:
                    blocks.append(HeadingBlock.model_validate(block_data))
                    
            return blocks
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            raise
            
    async def append_blocks(
        self,
        page_id: str,
        blocks: List[Dict[str, Any]]
    ) -> List[NotionBlock]:
        """Append blocks to page."""
        try:
            response = await self._request(
                "PATCH",
                f"blocks/{page_id}/children",
                {"children": blocks}
            )
            return [NotionBlock.model_validate(block) for block in response["results"]]
        except ValidationError as e:
            await self.handle_error(e, {
                "page_id": page_id,
                "step": "validation"
            })
            raise NotionError(f"Invalid block data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {"page_id": page_id})
            raise
            
    async def get_social_media_data(self) -> List[Dict[str, Any]]:
        """Get social media data from database."""
        try:
            results = await self.query_database(SOCIAL_MEDIA_DB_ID)
            social_data = []
            
            for page in results:
                properties = page.properties
                social_data.append({
                    "name": properties.get(PROPERTY_NAMES["name"], {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                    "status": properties.get(PROPERTY_NAMES["status"], {}).get("select", {}).get("name", "Unknown"),
                    "url": properties.get(PROPERTY_NAMES["url"], {}).get("url", ""),
                    "responsible": properties.get(PROPERTY_NAMES["responsible"], {}).get("people", [{}])[0].get("name", "Unassigned")
                })
                
            return social_data
        except Exception as e:
            logger.error(f"Error getting social media data: {e}")
            raise
            
    async def get_team_data(self) -> List[Dict[str, Any]]:
        """Get team data from database."""
        try:
            results = await self.query_database(TEAM_DB_ID)
            team_data = []
            
            for page in results:
                properties = page.properties
                team_data.append({
                    "name": properties.get(PROPERTY_NAMES["name"], {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                    "members": properties.get("Members", {}).get("people", []),
                    "lead": properties.get("Lead", {}).get("people", [{}])[0].get("name", "Unassigned"),
                    "department": properties.get(PROPERTY_NAMES["department"], {}).get("select", {}).get("name", "General")
                })
                
            return team_data
        except Exception as e:
            logger.error(f"Error getting team data: {e}")
            raise
            
    async def get_kpi_data(self) -> List[Dict[str, Any]]:
        """Get KPI data from database."""
        try:
            results = await self.query_database(KPI_DB_ID)
            kpi_data = []
            
            for page in results:
                properties = page.properties
                kpi_data.append({
                    "metric": properties.get(PROPERTY_NAMES["metric"], {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                    "target": properties.get(PROPERTY_NAMES["target"], {}).get("number", 0),
                    "actual": properties.get(PROPERTY_NAMES["actual"], {}).get("number", 0),
                    "period": properties.get(PROPERTY_NAMES["period"], {}).get("select", {}).get("name", "Current"),
                    "status": properties.get(PROPERTY_NAMES["status"], {}).get("select", {}).get("name", "In Progress")
                })
                
            return kpi_data
        except Exception as e:
            logger.error(f"Error getting KPI data: {e}")
            raise
            
    async def get_typical_tasks(self) -> List[Dict[str, Any]]:
        """Get typical tasks from database."""
        try:
            results = await self.query_database(TYPICAL_TASKS_DB_ID)
            tasks_data = []
            
            for page in results:
                properties = page.properties
                tasks_data.append({
                    "name": properties.get(PROPERTY_NAMES["name"], {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                    "status": properties.get(PROPERTY_NAMES["status"], {}).get("select", {}).get("name", "New"),
                    "priority": properties.get(PROPERTY_NAMES["priority"], {}).get("select", {}).get("name", "Medium"),
                    "assignee": properties.get(PROPERTY_NAMES["assignee"], {}).get("people", [{}])[0].get("name", "Unassigned"),
                    "due_date": properties.get(PROPERTY_NAMES["due_date"], {}).get("date", {}).get("start", None)
                })
                
            return tasks_data
        except Exception as e:
            logger.error(f"Error getting typical tasks: {e}")
            raise
            
    async def create_task(self, task_data: Dict[str, Any]) -> NotionPage:
        """Create a new task."""
        try:
            properties = {
                PROPERTY_NAMES["name"]: {"title": [{"text": {"content": task_data["name"]}}]},
                PROPERTY_NAMES["status"]: {"select": {"name": task_data.get("status", "New")}},
                PROPERTY_NAMES["priority"]: {"select": {"name": task_data.get("priority", "Medium")}},
            }
            
            if "assignee_id" in task_data:
                properties[PROPERTY_NAMES["assignee"]] = {"people": [{"id": task_data["assignee_id"]}]}
            if "due_date" in task_data:
                properties[PROPERTY_NAMES["due_date"]] = {"date": {"start": task_data["due_date"]}}
                
            return await self.create_page(TYPICAL_TASKS_DB_ID, properties)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
            
    async def update_task(self, page_id: str, task_data: Dict[str, Any]) -> NotionPage:
        """Update an existing task."""
        try:
            properties = {}
            
            if "name" in task_data:
                properties[PROPERTY_NAMES["name"]] = {"title": [{"text": {"content": task_data["name"]}}]}
            if "status" in task_data:
                properties[PROPERTY_NAMES["status"]] = {"select": {"name": task_data["status"]}}
            if "priority" in task_data:
                properties[PROPERTY_NAMES["priority"]] = {"select": {"name": task_data["priority"]}}
            if "assignee_id" in task_data:
                properties[PROPERTY_NAMES["assignee"]] = {"people": [{"id": task_data["assignee_id"]}]}
            if "due_date" in task_data:
                properties[PROPERTY_NAMES["due_date"]] = {"date": {"start": task_data["due_date"]}}
                
            return await self.update_page(page_id, properties)
        except Exception as e:
            logger.error(f"Error updating task {page_id}: {e}")
            raise
            
    async def get_page(self, page_id: str) -> NotionPage:
        """Get a Notion page by ID."""
        try:
            page = await self.client.pages.retrieve(page_id=page_id)
            return NotionPage(**page)
        except Exception as e:
            logger.error(f"Error getting Notion page {page_id}: {e}", exc_info=True)
            raise NotionError(f"Failed to get page: {e}")
            
    async def get_page_content(self, page_id: str) -> List[NotionPage]:
        """Get content blocks of a Notion page."""
        try:
            blocks = await self.client.blocks.children.list(block_id=page_id)
            return [NotionPage(**block) for block in blocks["results"]]
        except Exception as e:
            logger.error(f"Error getting page content {page_id}: {e}", exc_info=True)
            raise NotionError(f"Failed to get page content: {e}")
            
    async def create_task(self, database_id: str, task_data: Dict[str, Any]) -> NotionPage:
        """Create a new task in Notion database."""
        try:
            page = await self.client.pages.create(
                parent={"database_id": database_id},
                properties=task_data
            )
            return NotionPage(**page)
        except Exception as e:
            logger.error(f"Error creating task: {e}", exc_info=True)
            raise NotionError(f"Failed to create task: {e}")
            
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> NotionPage:
        """Update an existing task in Notion."""
        try:
            page = await self.client.pages.update(
                page_id=task_id,
                properties=task_data
            )
            return NotionPage(**page)
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}", exc_info=True)
            raise NotionError(f"Failed to update task: {e}")
            
    async def query_database(self, database_id: str, filter_params: Optional[Dict] = None) -> List[NotionPage]:
        """Query a Notion database with optional filters."""
        try:
            query = {"database_id": database_id}
            if filter_params:
                query.update(filter_params)
                
            response = await self.client.databases.query(**query)
            return [NotionPage(**page) for page in response["results"]]
        except Exception as e:
            logger.error(f"Error querying database {database_id}: {e}", exc_info=True)
            raise NotionError(f"Failed to query database: {e}")
            
    async def get_database(self, database_id: str) -> NotionPage:
        """Get a Notion database by ID."""
        try:
            database = await self.client.databases.retrieve(database_id=database_id)
            return NotionPage(**database)
        except Exception as e:
            logger.error(f"Error getting database {database_id}: {e}", exc_info=True)
            raise NotionError(f"Failed to get database: {e}")
            
    async def create_database(self, parent_id: str, title: str, properties: Dict[str, Any]) -> NotionPage:
        """Create a new Notion database."""
        try:
            database = await self.client.databases.create(
                parent={"page_id": parent_id},
                title=[{"text": {"content": title}}],
                properties=properties
            )
            return NotionPage(**database)
        except Exception as e:
            logger.error(f"Error creating database: {e}", exc_info=True)
            raise NotionError(f"Failed to create database: {e}")
            
    async def update_database(self, database_id: str, properties: Dict[str, Any]) -> NotionPage:
        """Update an existing Notion database."""
        try:
            database = await self.client.databases.update(
                database_id=database_id,
                properties=properties
            )
            return NotionPage(**database)
        except Exception as e:
            logger.error(f"Error updating database {database_id}: {e}", exc_info=True)
            raise NotionError(f"Failed to update database: {e}")
            
    async def delete_page(self, page_id: str) -> bool:
        """Delete (archive) a Notion page."""
        try:
            await self.client.pages.update(
                page_id=page_id,
                archived=True
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting page {page_id}: {e}", exc_info=True)
            raise NotionError(f"Failed to delete page: {e}")
            
    async def restore_page(self, page_id: str) -> bool:
        """Restore an archived Notion page."""
        try:
            await self.client.pages.update(
                page_id=page_id,
                archived=False
            )
            return True
        except Exception as e:
            logger.error(f"Error restoring page {page_id}: {e}", exc_info=True)
            raise NotionError(f"Failed to restore page: {e}")
            
    async def search(self, query: str, filter_params: Optional[Dict] = None) -> List[NotionPage]:
        """Search Notion workspace."""
        try:
            search_params = {"query": query}
            if filter_params:
                search_params.update(filter_params)
                
            response = await self.client.search(**search_params)
            return [NotionPage(**page) for page in response["results"]]
        except Exception as e:
            logger.error(f"Error searching Notion: {e}", exc_info=True)
            raise NotionError(f"Failed to search: {e}") 