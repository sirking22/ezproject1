"""Unified Notion service for interacting with Notion API."""
from typing import Dict, List, Optional, Any, Union
import asyncio
from datetime import datetime
import logging
from urllib.parse import urljoin

import aiohttp
from pydantic import ValidationError
from notion_client import AsyncClient

from .base_service import BaseService
from ..models.notion_models import (
    NotionPage,
    NotionDatabase,
    NotionBlock,
    TextBlock,
    TodoBlock,
    HeadingBlock
)
from ..config import get_settings
from ..repositories.notion_repository import NotionTaskRepository

logger = logging.getLogger(__name__)

class NotionError(Exception):
    """Base exception for Notion service."""
    pass

# Constants
PROPERTY_NAMES: Dict[str, str] = {
    "name": "Name",
    "status": "Status",
    "priority": "Priority",
    "assignee": "Assignee",
    "due_date": "Due Date",
    "url": "URL",
    "responsible": "Responsible",
    "department": "Department",
    "metric": "Metric",
    "target": "Target",
    "actual": "Actual",
    "period": "Period"
}

class NotionService(BaseService):
    """Unified service for interacting with Notion API."""
    
    def __init__(self):
        """Initialize service with configuration."""
        super().__init__()
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        self.databases = self.settings.NOTION_DATABASES
        self.client = AsyncClient(auth=self.settings.NOTION_TOKEN)
        self.task_repository = NotionTaskRepository(self.client, self.settings.NOTION_DATABASES["tasks"])
        
    async def initialize(self) -> None:
        """Initialize Notion client session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers=self.settings.get_notion_headers()
            )
        self.log_operation("initialization", {"status": "success"})
            
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
            await self.handle_error(e, {"database_id": database_id, "step": "validation"})
            raise NotionError(f"Invalid database data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {"database_id": database_id})
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
            await self.handle_error(e, {
                "database_id": database_id,
                "step": "validation"
            })
            raise NotionError(f"Invalid page data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {
                "database_id": database_id,
                "filters": filter_conditions,
                "sorts": sorts
            })
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
            await self.handle_error(e, {
                "database_id": database_id,
                "step": "validation"
            })
            raise NotionError(f"Invalid page data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {
                "database_id": database_id,
                "properties": properties
            })
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
            await self.handle_error(e, {
                "page_id": page_id,
                "step": "validation"
            })
            raise NotionError(f"Invalid page data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {
                "page_id": page_id,
                "properties": properties
            })
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
        except ValidationError as e:
            await self.handle_error(e, {
                "page_id": page_id,
                "step": "validation"
            })
            raise NotionError(f"Invalid block data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {"page_id": page_id})
            raise
            
    async def append_blocks(
        self,
        page_id: str,
        blocks: List[Dict[str, Any]]
    ) -> List[NotionBlock]:
        """Append blocks to a page."""
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
            await self.handle_error(e, {
                "page_id": page_id,
                "blocks": blocks
            })
            raise

    async def create_task(self, task_data: Dict[str, Any]) -> NotionPage:
        """Create a new task."""
        try:
            return await self.task_repository.create_task(task_data)
        except Exception as e:
            await self.handle_error(e, {"task_data": task_data})
            raise

    async def update_task(self, page_id: str, task_data: Dict[str, Any]) -> NotionPage:
        """Update an existing task."""
        try:
            return await self.task_repository.update_task(page_id, task_data)
        except Exception as e:
            await self.handle_error(e, {
                "page_id": page_id,
                "task_data": task_data
            })
            raise

    async def get_page(self, page_id: str) -> NotionPage:
        """Get a specific page."""
        try:
            data = await self._request("GET", f"pages/{page_id}")
            return NotionPage.model_validate(data)
        except ValidationError as e:
            await self.handle_error(e, {
                "page_id": page_id,
                "step": "validation"
            })
            raise NotionError(f"Invalid page data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {"page_id": page_id})
            raise

    async def delete_page(self, page_id: str) -> bool:
        """Delete a page (archive it)."""
        try:
            await self._request("PATCH", f"pages/{page_id}", {"archived": True})
            return True
        except Exception as e:
            await self.handle_error(e, {"page_id": page_id})
            return False

    async def restore_page(self, page_id: str) -> bool:
        """Restore an archived page."""
        try:
            await self._request("PATCH", f"pages/{page_id}", {"archived": False})
            return True
        except Exception as e:
            await self.handle_error(e, {"page_id": page_id})
            return False

    async def search(self, query: str, filter_params: Optional[Dict] = None) -> List[NotionPage]:
        """Search pages and databases."""
        try:
            data = {
                "query": query,
                "page_size": 100
            }
            if filter_params:
                data["filter"] = filter_params
                
            response = await self._request("POST", "search", data)
            return [NotionPage.model_validate(page) for page in response["results"]]
        except ValidationError as e:
            await self.handle_error(e, {
                "query": query,
                "step": "validation"
            })
            raise NotionError(f"Invalid search results: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {"query": query})
            raise

    async def create_database(self, parent_id: str, title: str, properties: Dict[str, Any]) -> NotionPage:
        """Create a new database."""
        try:
            data = {
                "parent": {"page_id": parent_id},
                "title": [{"text": {"content": title}}],
                "properties": properties
            }
            response = await self._request("POST", "databases", data)
            return NotionPage.model_validate(response)
        except ValidationError as e:
            await self.handle_error(e, {
                "parent_id": parent_id,
                "title": title,
                "step": "validation"
            })
            raise NotionError(f"Invalid database data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {
                "parent_id": parent_id,
                "title": title,
                "properties": properties
            })
            raise

    async def update_database(self, database_id: str, properties: Dict[str, Any]) -> NotionPage:
        """Update database properties."""
        try:
            response = await self._request("PATCH", f"databases/{database_id}", {"properties": properties})
            return NotionPage.model_validate(response)
        except ValidationError as e:
            await self.handle_error(e, {
                "database_id": database_id,
                "step": "validation"
            })
            raise NotionError(f"Invalid database data: {str(e)}")
        except Exception as e:
            await self.handle_error(e, {
                "database_id": database_id,
                "properties": properties
            })
            raise 