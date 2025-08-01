#!/usr/bin/env python3
"""
Умный процессор задач - проверяет дубли, находит эпики, молниеносно обрабатывает
"""

import os
import logging
from typing import List, Dict, Optional, Any, Tuple
from dotenv import load_dotenv
from notion_client import AsyncClient
import asyncio
import re
from difflib import SequenceMatcher

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

class SmartTaskProcessor:
    """Умный процессор для работы с задачами без дублей"""
    
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.tasks_db_id = os.getenv("TASKS_DB")
        self.subtasks_db_id = os.getenv("SUBTASKS_DB")
        
        if not self.notion_token or not self.tasks_db_id:
            raise ValueError("NOTION_TOKEN и TASKS_DB должны быть в .env")
            
        self.client = AsyncClient(auth=self.notion_token)
        logger.info("✅ SmartTaskProcessor инициализирован")
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Вычисление сходства между текстами"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов из текста"""
        # Удаляем стоп-слова
        stop_words = {
            'делаем', 'делал', 'удалил', 'добавить', 'под', 'задачу', 'время', 'часов', 'час',
            'два', 'три', 'четыре', 'пять', 'один', 'еще', 'также', 'потом', 'сейчас',
            'где', 'что', 'как', 'когда', 'почему', 'какой', 'которой', 'нужно', 'надо'
        }
        words = re.findall(r'\b[а-яё]+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return list(set(keywords))  # Уникальные ключевые слова
    
    async def get_all_existing_tasks(self) -> List[Dict[str, Any]]:
        """Получение всех существующих задач для проверки дублей"""
        try:
            logger.info("🔍 Загружаем ВСЕ существующие задачи для проверки дублей...")
            
            all_tasks = []
            has_more = True
            start_cursor = None
            
            while has_more:
                query_params = {
                    "database_id": self.tasks_db_id,
                    "page_size": 100
                }
                
                if start_cursor:
                    query_params["start_cursor"] = start_cursor
                
                response = await self.client.databases.query(**query_params)
                
                for page in response.get("results", []):
                    properties = page.get("properties", {})
                    task_title = properties.get("Задача", {}).get("title", [])
                    if task_title:
                        all_tasks.append({
                            "id": page["id"],
                            "title": task_title[0]["text"]["content"],
                            "status": properties.get("Статус", {}).get("status", {}).get("name", ""),
                            "assignees": properties.get("Участники", {}).get("people", []),
                            "hours": properties.get("Часы", {}).get("number", 0),
                            "keywords": self._extract_keywords(task_title[0]["text"]["content"])
                        })
                
                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")
            
            logger.info(f"📊 Загружено {len(all_tasks)} существующих задач")
            return all_tasks
            
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке существующих задач: {e}")
            return []
    
    async def find_duplicate_or_similar(self, new_task: str, existing_tasks: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
        """Поиск дублей или очень похожих задач"""
        new_keywords = self._extract_keywords(new_task)
        logger.info(f"🔍 Ищем дубли для '{new_task}' (ключевые слова: {new_keywords})")
        
        best_match = None
        best_score = 0.0
        
        for existing in existing_tasks:
            # Прямое сходство названий
            title_similarity = self._calculate_similarity(new_task, existing["title"])
            
            # Сходство по ключевым словам
            common_keywords = set(new_keywords) & set(existing["keywords"])
            keyword_score = len(common_keywords) / max(len(new_keywords), 1) if new_keywords else 0
            
            # Общий балл (60% название + 40% ключевые слова)
            total_score = title_similarity * 0.6 + keyword_score * 0.4
            
            logger.debug(f"  📋 '{existing['title']}' - сходство: {total_score:.2f} (название: {title_similarity:.2f}, слова: {keyword_score:.2f})")
            
            if total_score > best_score:
                best_score = total_score
                best_match = existing
        
        if best_score > 0.7:  # Порог для дубля
            logger.info(f"🎯 НАЙДЕН ДУБЛЬ: '{best_match['title']}' (сходство: {best_score:.2f})")
            return best_match, best_score
        elif best_score > 0.4:  # Порог для похожей задачи
            logger.info(f"🔗 НАЙДЕНА ПОХОЖАЯ: '{best_match['title']}' (сходство: {best_score:.2f})")
            return best_match, best_score
        
        logger.info(f"✨ Новая уникальная задача: '{new_task}'")
        return None, 0.0
    
    async def process_task_intelligently(self, task_data: Dict[str, Any], existing_tasks: List[Dict[str, Any]], user_id: int) -> Dict[str, Any]:
        """Умная обработка задачи: проверка дублей, добавление подзадач"""
        task_name = task_data.get("task", "")
        subtasks = task_data.get("subtasks", [])
        
        logger.info(f"\n🧠 УМНАЯ ОБРАБОТКА: '{task_name}'")
        logger.info(f"   📋 Подзадач: {len(subtasks)}")
        
        # Ищем дубли или похожие задачи
        duplicate, similarity = await self.find_duplicate_or_similar(task_name, existing_tasks)
        
        if duplicate and similarity > 0.7:
            # Это дубль - добавляем подзадачи к существующей задаче
            logger.info(f"⚡ МОЛНИЕНОСНО: Добавляем подзадачи к существующей задаче '{duplicate['title']}'")
            
            added_subtasks = []
            for subtask in subtasks:
                subtask_id = await self._add_subtask_to_existing(duplicate["id"], subtask)
                if subtask_id:
                    added_subtasks.append(subtask["name"])
            
            return {
                "action": "updated_existing",
                "task_id": duplicate["id"],
                "task_title": duplicate["title"],
                "added_subtasks": added_subtasks,
                "similarity": similarity
            }
        
        elif duplicate and similarity > 0.4:
            # Похожая задача - спрашиваем пользователя
            logger.info(f"❓ ТРЕБУЕТ УТОЧНЕНИЯ: Найдена похожая задача '{duplicate['title']}'")
            return {
                "action": "needs_clarification",
                "existing_task": duplicate,
                "similarity": similarity,
                "new_task_data": task_data
            }
        
        else:
            # Новая уникальная задача
            logger.info(f"✨ СОЗДАЕМ НОВУЮ: '{task_name}'")
            new_task_id = await self._create_new_task(task_data, user_id)
            return {
                "action": "created_new",
                "task_id": new_task_id,
                "task_title": task_name,
                "subtasks_count": len(subtasks)
            }
    
    async def _add_subtask_to_existing(self, parent_task_id: str, subtask_data: Dict[str, Any]) -> Optional[str]:
        """Добавление подзадачи к существующей задаче"""
        try:
            properties = {
                "Подзадачи": {
                    "title": [{"text": {"content": subtask_data["name"]}}]
                },
                "Статус": {
                    "status": {"name": "To Do"}
                },
                "Время": {
                    "number": subtask_data.get("time_hours", 0)
                },
                "Задачи": {
                    "relation": [{"id": parent_task_id}]
                }
            }
            
            if subtask_data.get("description"):
                properties["Описание"] = {
                    "rich_text": [{"text": {"content": subtask_data["description"]}}]
                }
            
            new_page = await self.client.pages.create(
                parent={"database_id": self.subtasks_db_id},
                properties=properties
            )
            
            logger.info(f"✅ Добавлена подзадача: {subtask_data['name']} ({subtask_data.get('time_hours', 0)} ч)")
            return new_page["id"]
            
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении подзадачи: {e}")
            return None
    
    async def _create_new_task(self, task_data: Dict[str, Any], user_id: int) -> Optional[str]:
        """Создание новой задачи с подзадачами"""
        try:
            properties = {
                "Задача": {"title": [{"text": {"content": task_data["task"]}}]},
                "Статус": {"status": {"name": "To Do"}},
            }
            
            if task_data.get('time_hours'):
                properties["Часы"] = {"number": task_data['time_hours']}
            
            # Создаем основную задачу
            new_task = await self.client.pages.create(
                parent={"database_id": self.tasks_db_id},
                properties=properties
            )
            
            task_id = new_task["id"]
            logger.info(f"✅ Создана новая задача: {task_data['task']}")
            
            # Добавляем подзадачи
            for subtask in task_data.get("subtasks", []):
                await self._add_subtask_to_existing(task_id, subtask)
            
            return task_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка при создании новой задачи: {e}")
            return None

# Тест системы
async def test_smart_processor():
    """Тест умной обработки"""
    processor = SmartTaskProcessor()
    
    # Загружаем существующие задачи
    existing_tasks = await processor.get_all_existing_tasks()
    
    # Тестовая задача
    test_task = {
        "task": "Создание логотипа для бренда",
        "time_hours": 2,
        "subtasks": [
            {"name": "Разработка концепции", "time_hours": 1},
            {"name": "Создание вариантов", "time_hours": 1}
        ]
    }
    
    result = await processor.process_task_intelligently(test_task, existing_tasks, 307055142)
    print(f"Результат обработки: {result}")

if __name__ == "__main__":
    asyncio.run(test_smart_processor()) 