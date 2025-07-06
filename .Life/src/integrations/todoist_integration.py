#!/usr/bin/env python3
"""
Todoist интеграция для синхронизации задач
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
from enum import Enum

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    LOW = 4
    NORMAL = 3
    HIGH = 2
    URGENT = 1

@dataclass
class TodoistTask:
    id: str
    content: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    due_date: Optional[datetime] = None
    project_id: Optional[str] = None
    labels: List[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []

class TodoistIntegration:
    """Интеграция с Todoist API"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.todoist.com/rest/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        self.projects_cache: Dict[str, Dict] = {}
        self.labels_cache: Dict[str, Dict] = {}
        
    async def initialize(self):
        """Инициализация клиента"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                }
            )
        
        # Кэшируем проекты и метки
        await self._cache_projects()
        await self._cache_labels()
        
        logger.info("Todoist клиент инициализирован")
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _cache_projects(self):
        """Кэширование проектов"""
        try:
            async with self.session.get(f"{self.base_url}/projects") as response:
                if response.status == 200:
                    projects = await response.json()
                    self.projects_cache = {p["name"]: p for p in projects}
                    logger.info(f"Кэшировано {len(projects)} проектов")
        except Exception as e:
            logger.error(f"Ошибка кэширования проектов: {e}")
    
    async def _cache_labels(self):
        """Кэширование меток"""
        try:
            async with self.session.get(f"{self.base_url}/labels") as response:
                if response.status == 200:
                    labels = await response.json()
                    self.labels_cache = {l["name"]: l for l in labels}
                    logger.info(f"Кэшировано {len(labels)} меток")
        except Exception as e:
            logger.error(f"Ошибка кэширования меток: {e}")
    
    async def create_task(self, content: str, description: str = None, 
                         priority: TaskPriority = TaskPriority.NORMAL,
                         due_date: Optional[datetime] = None,
                         project_name: str = None,
                         labels: List[str] = None) -> Optional[TodoistTask]:
        """Создание задачи в Todoist"""
        try:
            task_data = {
                "content": content,
                "priority": priority.value
            }
            
            if description:
                task_data["description"] = description
            
            if due_date:
                task_data["due_date"] = due_date.strftime("%Y-%m-%d")
            
            if project_name and project_name in self.projects_cache:
                task_data["project_id"] = self.projects_cache[project_name]["id"]
            
            if labels:
                task_data["labels"] = labels
            
            async with self.session.post(f"{self.base_url}/tasks", json=task_data) as response:
                if response.status == 200:
                    task_json = await response.json()
                    task = self._json_to_task(task_json)
                    logger.info(f"Задача создана в Todoist: {content}")
                    return task
                else:
                    logger.error(f"Ошибка создания задачи: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка создания задачи в Todoist: {e}")
            return None
    
    async def get_tasks(self, project_name: str = None, 
                       completed: bool = False,
                       limit: int = 50) -> List[TodoistTask]:
        """Получение задач"""
        try:
            params = {}
            if project_name and project_name in self.projects_cache:
                params["project_id"] = self.projects_cache[project_name]["id"]
            
            if completed:
                params["completed"] = "true"
            
            async with self.session.get(f"{self.base_url}/tasks", params=params) as response:
                if response.status == 200:
                    tasks_json = await response.json()
                    tasks = [self._json_to_task(t) for t in tasks_json[:limit]]
                    logger.info(f"Получено {len(tasks)} задач из Todoist")
                    return tasks
                else:
                    logger.error(f"Ошибка получения задач: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Ошибка получения задач из Todoist: {e}")
            return []
    
    async def update_task(self, task_id: str, **kwargs) -> Optional[TodoistTask]:
        """Обновление задачи"""
        try:
            async with self.session.post(f"{self.base_url}/tasks/{task_id}", json=kwargs) as response:
                if response.status == 200:
                    task_json = await response.json()
                    task = self._json_to_task(task_json)
                    logger.info(f"Задача обновлена в Todoist: {task_id}")
                    return task
                else:
                    logger.error(f"Ошибка обновления задачи: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка обновления задачи в Todoist: {e}")
            return None
    
    async def complete_task(self, task_id: str) -> bool:
        """Завершение задачи"""
        try:
            async with self.session.post(f"{self.base_url}/tasks/{task_id}/close") as response:
                if response.status == 204:
                    logger.info(f"Задача завершена в Todoist: {task_id}")
                    return True
                else:
                    logger.error(f"Ошибка завершения задачи: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Ошибка завершения задачи в Todoist: {e}")
            return False
    
    async def delete_task(self, task_id: str) -> bool:
        """Удаление задачи"""
        try:
            async with self.session.delete(f"{self.base_url}/tasks/{task_id}") as response:
                if response.status == 204:
                    logger.info(f"Задача удалена из Todoist: {task_id}")
                    return True
                else:
                    logger.error(f"Ошибка удаления задачи: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Ошибка удаления задачи из Todoist: {e}")
            return False
    
    async def get_projects(self) -> List[Dict]:
        """Получение проектов"""
        try:
            async with self.session.get(f"{self.base_url}/projects") as response:
                if response.status == 200:
                    projects = await response.json()
                    return projects
                else:
                    logger.error(f"Ошибка получения проектов: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Ошибка получения проектов из Todoist: {e}")
            return []
    
    async def create_project(self, name: str, color: str = None) -> Optional[Dict]:
        """Создание проекта"""
        try:
            project_data = {"name": name}
            if color:
                project_data["color"] = color
            
            async with self.session.post(f"{self.base_url}/projects", json=project_data) as response:
                if response.status == 200:
                    project = await response.json()
                    self.projects_cache[name] = project
                    logger.info(f"Проект создан в Todoist: {name}")
                    return project
                else:
                    logger.error(f"Ошибка создания проекта: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Ошибка создания проекта в Todoist: {e}")
            return None
    
    def _json_to_task(self, task_json: Dict) -> TodoistTask:
        """Конвертация JSON в TodoistTask"""
        return TodoistTask(
            id=task_json["id"],
            content=task_json["content"],
            description=task_json.get("description"),
            priority=TaskPriority(task_json.get("priority", 3)),
            due_date=datetime.fromisoformat(task_json["due"]["date"]) if task_json.get("due") else None,
            project_id=task_json.get("project_id"),
            labels=task_json.get("labels", []),
            created_at=datetime.fromisoformat(task_json["created_at"]) if task_json.get("created_at") else None,
            completed_at=datetime.fromisoformat(task_json["completed_at"]) if task_json.get("completed_at") else None
        )
    
    async def sync_with_notion(self, notion_service, sync_direction: str = "both"):
        """Синхронизация с Notion"""
        # TODO: Реализовать двустороннюю синхронизацию
        pass
    
    async def get_daily_tasks(self) -> List[TodoistTask]:
        """Получение задач на сегодня"""
        today = datetime.now().date()
        all_tasks = await self.get_tasks()
        
        today_tasks = []
        for task in all_tasks:
            if task.due_date and task.due_date.date() == today:
                today_tasks.append(task)
        
        return today_tasks
    
    async def get_overdue_tasks(self) -> List[TodoistTask]:
        """Получение просроченных задач"""
        today = datetime.now().date()
        all_tasks = await self.get_tasks()
        
        overdue_tasks = []
        for task in all_tasks:
            if task.due_date and task.due_date.date() < today:
                overdue_tasks.append(task)
        
        return overdue_tasks 