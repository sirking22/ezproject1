#!/usr/bin/env python3
"""
Сервис для поиска похожих задач и исполнителей в Notion
"""

import os
import logging
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from notion_client import AsyncClient
import asyncio
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

class TaskSimilarityFinder:
    """Поиск похожих задач и исполнителей в Notion"""
    
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.tasks_db_id = os.getenv("TASKS_DB")
        self.subtasks_db_id = os.getenv("SUBTASKS_DB")
        self.guides_db_id = os.getenv("GUIDES_DB")
        
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN не найден в .env")
            
        self.client = AsyncClient(auth=self.notion_token)
        logger.info("✅ TaskSimilarityFinder инициализирован")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов из текста"""
        # Удаляем стоп-слова и извлекаем ключевые слова
        stop_words = {'делаем', 'делал', 'удалил', 'добавить', 'под', 'задачу', 'время', 'часов', 'час'}
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:5]  # Топ-5 ключевых слов
    
    async def find_similar_tasks(self, task_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Умный поиск похожих задач по названию и ключевым словам"""
        try:
            keywords = self._extract_keywords(task_name)
            similar_tasks = []
            
            # Поиск по точному совпадению
            response = await self.client.databases.query(
                database_id=self.tasks_db_id,
                filter={
                    "property": "Задача",
                    "rich_text": {
                        "contains": task_name.split()[0]
                    }
                },
                page_size=limit
            )
            
            for page in response.get("results", []):
                properties = page.get("properties", {})
                task_title = properties.get("Задача", {}).get("title", [])
                if task_title:
                    similar_tasks.append({
                        "id": page["id"],
                        "title": task_title[0]["text"]["content"],
                        "status": properties.get("Статус", {}).get("status", {}).get("name", ""),
                        "assignees": properties.get("Участники", {}).get("people", []),
                        "match_type": "exact"
                    })
            
            # Поиск по ключевым словам
            for keyword in keywords:
                if len(similar_tasks) >= limit:
                    break
                    
                response = await self.client.databases.query(
                    database_id=self.tasks_db_id,
                    filter={
                        "property": "Задача",
                        "rich_text": {
                            "contains": keyword
                        }
                    },
                    page_size=limit
                )
                
                for page in response.get("results", []):
                    properties = page.get("properties", {})
                    task_title = properties.get("Задача", {}).get("title", [])
                    if task_title and not any(t["id"] == page["id"] for t in similar_tasks):
                        similar_tasks.append({
                            "id": page["id"],
                            "title": task_title[0]["text"]["content"],
                            "status": properties.get("Статус", {}).get("status", {}).get("name", ""),
                            "assignees": properties.get("Участники", {}).get("people", []),
                            "match_type": "keyword",
                            "keyword": keyword
                        })
            
            logger.info(f"Найдено {len(similar_tasks)} похожих задач для '{task_name}' (ключевые слова: {keywords})")
            return similar_tasks
            
        except Exception as e:
            logger.error(f"Ошибка при поиске похожих задач: {e}")
            return []
    
    async def find_existing_task_by_keywords(self, keywords: List[str]) -> Optional[Dict[str, Any]]:
        """Поиск существующей задачи по ключевым словам для добавления подзадач"""
        try:
            for keyword in keywords:
                response = await self.client.databases.query(
                    database_id=self.tasks_db_id,
                    filter={
                        "property": "Задача",
                        "rich_text": {
                            "contains": keyword
                        }
                    },
                    page_size=1
                )
                
                if response.get("results"):
                    page = response["results"][0]
                    properties = page.get("properties", {})
                    task_title = properties.get("Задача", {}).get("title", [])
                    if task_title:
                        return {
                            "id": page["id"],
                            "title": task_title[0]["text"]["content"],
                            "status": properties.get("Статус", {}).get("status", {}).get("name", "")
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при поиске существующей задачи: {e}")
            return None
    
    async def find_assignee_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Поиск исполнителя по Telegram ID"""
        try:
            # Здесь нужно будет добавить поиск в базе сотрудников
            # Пока возвращаем заглушку
            return {
                "id": "user_id_placeholder",
                "name": "Пользователь",
                "telegram_id": telegram_id
            }
        except Exception as e:
            logger.error(f"Ошибка при поиске исполнителя: {e}")
            return None
    
    async def get_guide_steps(self, task_type: str) -> List[Dict[str, Any]]:
        """Получение шагов из гайдов для типа задачи"""
        try:
            if not self.guides_db_id:
                logger.warning("GUIDES_DB_ID не настроен")
                return []
            
            # Поиск гайда по типу задачи
            response = await self.client.databases.query(
                database_id=self.guides_db_id,
                filter={
                    "property": "Название",
                    "rich_text": {
                        "contains": task_type
                    }
                }
            )
            
            guide_steps = []
            for page in response.get("results", []):
                properties = page.get("properties", {})
                steps = properties.get("Шаги", {}).get("rich_text", [])
                for step in steps:
                    guide_steps.append({
                        "name": step["text"]["content"],
                        "time_hours": 0.5,  # По умолчанию 30 минут
                        "description": step["text"]["content"]
                    })
            
            logger.info(f"Найдено {len(guide_steps)} шагов из гайдов для '{task_type}'")
            return guide_steps
            
        except Exception as e:
            logger.error(f"Ошибка при получении шагов из гайдов: {e}")
            return []
    
    async def create_subtask(self, parent_task_id: str, subtask_data: Dict[str, Any]) -> Optional[str]:
        """Создание подзадачи в базе подзадач"""
        try:
            properties = {
                "Подзадачи": {
                    "title": [{"text": {"content": subtask_data["name"]}}]
                },
                "Статус": {
                    "status": {"name": "To Do"}
                },
                "Время": {
                    "number": subtask_data["time_hours"]
                }
            }
            
            if subtask_data.get("description"):
                properties["Описание"] = {
                    "rich_text": [{"text": {"content": subtask_data["description"]}}]
                }
            
            # Связь с родительской задачей
            properties["Задачи"] = {
                "relation": [{"id": parent_task_id}]
            }
            
            new_page = await self.client.pages.create(
                parent={"database_id": self.subtasks_db_id},
                properties=properties
            )
            
            logger.info(f"Создана подзадача: {subtask_data['name']}")
            return new_page["id"]
            
        except Exception as e:
            logger.error(f"Ошибка при создании подзадачи: {e}")
            return None

# Тест сервиса
async def test_similarity_finder():
    """Тест функций поиска"""
    finder = TaskSimilarityFinder()
    
    # Тест поиска похожих задач
    similar_tasks = await finder.find_similar_tasks("логотип с гонками")
    print(f"Похожие задачи: {similar_tasks}")
    
    # Тест поиска существующей задачи
    existing_task = await finder.find_existing_task_by_keywords(["логотип", "гонки"])
    print(f"Существующая задача: {existing_task}")

if __name__ == "__main__":
    asyncio.run(test_similarity_finder()) 