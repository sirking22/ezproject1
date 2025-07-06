"""
Интеграция с Notion для Quick Voice Assistant
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NotionItem:
    """Модель элемента Notion"""
    title: str
    content: str
    database: str
    properties: Dict[str, Any] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.tags is None:
            self.tags = []

class NotionIntegration:
    """Класс для интеграции с Notion"""
    
    def __init__(self, token: str, databases: Dict[str, str]):
        self.token = token
        self.databases = databases
        self.client = None
        self.enabled = bool(token and databases)
        
    async def initialize(self):
        """Инициализация клиента Notion"""
        if not self.enabled:
            logger.warning("Интеграция с Notion отключена")
            return
        
        try:
            # Здесь будет инициализация Notion клиента
            # from notion_client import AsyncClient
            # self.client = AsyncClient(auth=self.token)
            logger.info("Notion клиент инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Notion: {e}")
            self.enabled = False
    
    async def create_task(self, task_text: str, priority: str = "medium") -> bool:
        """Создание задачи в Notion"""
        if not self.enabled or "tasks" not in self.databases:
            return False
        
        try:
            item = NotionItem(
                title=f"Задача: {task_text}",
                content=task_text,
                database="tasks",
                properties={
                    "Status": {"select": {"name": "To Do"}},
                    "Priority": {"select": {"name": priority}},
                    "Created": {"date": {"start": datetime.now().isoformat()}}
                },
                tags=["voice-created", "task"]
            )
            
            success = await self._create_item(item)
            if success:
                logger.info(f"Задача создана в Notion: {task_text}")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            return False
    
    async def save_reflection(self, reflection_text: str, mood: str = "neutral") -> bool:
        """Сохранение рефлексии в Notion"""
        if not self.enabled or "reflections" not in self.databases:
            return False
        
        try:
            item = NotionItem(
                title=f"Рефлексия: {reflection_text[:50]}...",
                content=reflection_text,
                database="reflections",
                properties={
                    "Mood": {"select": {"name": mood}},
                    "Date": {"date": {"start": datetime.now().isoformat()}},
                    "Type": {"select": {"name": "voice"}}
                },
                tags=["voice-created", "reflection"]
            )
            
            success = await self._create_item(item)
            if success:
                logger.info(f"Рефлексия сохранена в Notion: {reflection_text[:50]}...")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка сохранения рефлексии: {e}")
            return False
    
    async def create_habit(self, habit_text: str, frequency: str = "daily") -> bool:
        """Создание привычки в Notion"""
        if not self.enabled or "habits" not in self.databases:
            return False
        
        try:
            item = NotionItem(
                title=f"Привычка: {habit_text}",
                content=habit_text,
                database="habits",
                properties={
                    "Status": {"select": {"name": "Active"}},
                    "Frequency": {"select": {"name": frequency}},
                    "Created": {"date": {"start": datetime.now().isoformat()}},
                    "Streak": {"number": 0}
                },
                tags=["voice-created", "habit"]
            )
            
            success = await self._create_item(item)
            if success:
                logger.info(f"Привычка создана в Notion: {habit_text}")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка создания привычки: {e}")
            return False
    
    async def save_idea(self, idea_text: str, category: str = "general") -> bool:
        """Сохранение идеи в Notion"""
        if not self.enabled or "ideas" not in self.databases:
            return False
        
        try:
            item = NotionItem(
                title=f"Идея: {idea_text[:50]}...",
                content=idea_text,
                database="ideas",
                properties={
                    "Category": {"select": {"name": category}},
                    "Status": {"select": {"name": "New"}},
                    "Created": {"date": {"start": datetime.now().isoformat()}}
                },
                tags=["voice-created", "idea"]
            )
            
            success = await self._create_item(item)
            if success:
                logger.info(f"Идея сохранена в Notion: {idea_text[:50]}...")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка сохранения идеи: {e}")
            return False
    
    async def _create_item(self, item: NotionItem) -> bool:
        """Создание элемента в Notion"""
        if not self.client:
            return False
        
        try:
            # Здесь будет код создания элемента через Notion API
            # response = await self.client.pages.create(
            #     parent={"database_id": self.databases[item.database]},
            #     properties=item.properties,
            #     children=[{
            #         "object": "block",
            #         "type": "paragraph",
            #         "paragraph": {
            #             "rich_text": [{"text": {"content": item.content}}]
            #         }
            #     }]
            # )
            
            # Имитация создания для тестирования
            await asyncio.sleep(0.1)
            logger.debug(f"Элемент создан: {item.title}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания элемента: {e}")
            return False
    
    async def get_recent_items(self, database: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Получение последних элементов из базы данных"""
        if not self.enabled or database not in self.databases:
            return []
        
        try:
            # Здесь будет код получения элементов через Notion API
            # response = await self.client.databases.query(
            #     database_id=self.databases[database],
            #     page_size=limit,
            #     sorts=[{"property": "Created", "direction": "descending"}]
            # )
            
            # Имитация данных для тестирования
            return [
                {
                    "id": f"test_{i}",
                    "title": f"Тестовый элемент {i}",
                    "created": datetime.now().isoformat(),
                    "status": "active"
                }
                for i in range(limit)
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения элементов: {e}")
            return []
    
    async def search_items(self, query: str, database: str = None) -> List[Dict[str, Any]]:
        """Поиск элементов в Notion"""
        if not self.enabled:
            return []
        
        try:
            # Здесь будет код поиска через Notion API
            # response = await self.client.search(
            #     query=query,
            #     filter={"property": "object", "value": "page"}
            # )
            
            # Имитация поиска для тестирования
            return [
                {
                    "id": "search_result_1",
                    "title": f"Результат поиска: {query}",
                    "url": "https://notion.so/test",
                    "database": database or "general"
                }
            ]
            
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []

# Глобальный экземпляр для использования в других модулях
notion_integration = None

async def initialize_notion_integration(token: str, databases: Dict[str, str]):
    """Инициализация глобального экземпляра интеграции с Notion"""
    global notion_integration
    notion_integration = NotionIntegration(token, databases)
    await notion_integration.initialize()
    return notion_integration

async def create_task(task_text: str) -> bool:
    """Создание задачи через глобальный экземпляр"""
    if notion_integration:
        return await notion_integration.create_task(task_text)
    return False

async def save_reflection(reflection_text: str) -> bool:
    """Сохранение рефлексии через глобальный экземпляр"""
    if notion_integration:
        return await notion_integration.save_reflection(reflection_text)
    return False

async def create_habit(habit_text: str) -> bool:
    """Создание привычки через глобальный экземпляр"""
    if notion_integration:
        return await notion_integration.create_habit(habit_text)
    return False 