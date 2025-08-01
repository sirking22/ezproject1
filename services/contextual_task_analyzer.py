#!/usr/bin/env python3
"""
🧠 РЕВОЛЮЦИОННЫЙ АНАЛИЗАТОР КОНТЕКСТА ЗАДАЧ
Извлекает из сообщения ссылку на конкретную задачу и работает с ней
"""

import os
import logging
from typing import List, Dict, Optional, Any, Tuple
from dotenv import load_dotenv
from notion_client import AsyncClient
import asyncio
import re
from difflib import SequenceMatcher
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

class TaskAction(BaseModel):
    """Действие с задачей"""
    action_type: str = Field(description="Тип: add_subtask, update_time, mark_done, add_time")
    task_reference: str = Field(description="Ссылка на задачу (название или ключевые слова)")
    subtask_name: Optional[str] = Field(default=None, description="Название подзадачи для добавления")
    time_hours: Optional[float] = Field(default=None, description="Время в часах")
    description: Optional[str] = Field(default=None, description="Описание действия")
    confidence: float = Field(default=0.5, description="Уверенность в распознавании (0-1)")

class ContextualAnalysis(BaseModel):
    """Результат контекстного анализа"""
    actions: List[TaskAction]
    has_task_reference: bool = Field(description="Есть ли ссылка на существующую задачу")
    extracted_context: str = Field(description="Извлеченный контекст")

class ContextualTaskAnalyzer:
    """🧠 Гениальный анализатор контекста задач"""
    
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.tasks_db_id = os.getenv("TASKS_DB")
        self.subtasks_db_id = os.getenv("SUBTASKS_DB")
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL")
        
        if not all([self.notion_token, self.tasks_db_id, self.api_key, self.base_url]):
            raise ValueError("Не хватает переменных окружения")
            
        self.client = AsyncClient(auth=self.notion_token)
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model_name="deepseek-chat",
            temperature=0,
        )
        self.parser = JsonOutputParser(pydantic_object=ContextualAnalysis)
        
        # 🧠 ГЕНИАЛЬНЫЙ ПРОМПТ для извлечения контекста
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты гениальный анализатор контекста задач. Твоя цель - понять, к какой СУЩЕСТВУЮЩЕЙ задаче относится сообщение пользователя."),
            ("system", "🎯 КРИТИЧЕСКИЕ ПРАВИЛА АНАЛИЗА:"),
            ("system", "1. Ищи ссылки на существующие задачи: 'к лого', 'в обложках', 'для YouTube', 'по заставке'"),
            ("system", "2. Определи тип действия: add_subtask (добавить подзадачу), update_time (обновить время), mark_done (завершить)"),
            ("system", "3. Извлеки время: 'час', 'два часа', 'полтора часа', '30 минут' = 0.5"),
            ("system", "4. Если есть ссылка на задачу - has_task_reference = true"),
            ("system", "5. Оцени уверенность в распознавании (0-1)"),
            ("system", "6. Используй русский язык для всех текстовых полей"),
            ("system", "Format instructions: {format_instructions}"),
            ("human", "Контекст существующих задач: {existing_tasks_context}"),
            ("human", "Сообщение пользователя: {user_message}"),
        ])
        
        self.chain = self.prompt.partial(format_instructions=self.parser.get_format_instructions()) | self.llm | self.parser
        
        logger.info("🧠 ContextualTaskAnalyzer инициализирован")
    
    async def get_tasks_context(self) -> str:
        """Получение контекста существующих задач для LLM"""
        try:
            logger.info("📋 Загружаем контекст существующих задач...")
            
            response = await self.client.databases.query(
                database_id=self.tasks_db_id,
                page_size=50,  # Последние 50 задач для контекста
                sorts=[{"timestamp": "last_edited_time", "direction": "descending"}]
            )
            
            tasks_context = []
            for page in response.get("results", []):
                properties = page.get("properties", {})
                task_title = properties.get("Задача", {}).get("title", [])
                if task_title:
                    title = task_title[0]["text"]["content"]
                    status = properties.get("Статус", {}).get("status", {}).get("name", "")
                    tasks_context.append(f"- {title} ({status})")
            
            context_text = "Существующие задачи:\n" + "\n".join(tasks_context[:20])  # Топ-20 для LLM
            logger.info(f"📊 Подготовлен контекст из {len(tasks_context)} задач")
            
            return context_text
            
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке контекста: {e}")
            return "Контекст задач недоступен"
    
    def parse_llm_response(self, llm_response: Any) -> ContextualAnalysis:
        """🔧 Универсальный парсер ответа LLM - всегда возвращает ContextualAnalysis"""
        try:
            # Если уже объект ContextualAnalysis
            if isinstance(llm_response, ContextualAnalysis):
                return llm_response
            
            # Если dict - конвертируем
            if isinstance(llm_response, dict):
                actions = []
                for action_data in llm_response.get("actions", []):
                    if isinstance(action_data, dict):
                        actions.append(TaskAction(**action_data))
                    else:
                        actions.append(action_data)
                
                return ContextualAnalysis(
                    actions=actions,
                    has_task_reference=llm_response.get("has_task_reference", False),
                    extracted_context=llm_response.get("extracted_context", "")
                )
            
            # Если строка - возможно JSON
            if isinstance(llm_response, str):
                try:
                    import json
                    data = json.loads(llm_response)
                    return self.parse_llm_response(data)  # Рекурсия для dict
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Не удалось распарсить JSON из строки: {llm_response[:100]}")
                    return ContextualAnalysis(
                        actions=[],
                        has_task_reference=False,
                        extracted_context=f"Ошибка парсинга: {llm_response[:50]}..."
                    )
            
            # Неизвестный тип
            logger.warning(f"⚠️ Неизвестный тип ответа LLM: {type(llm_response)}")
            return ContextualAnalysis(
                actions=[],
                has_task_reference=False,
                extracted_context="Неизвестный формат ответа"
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге ответа LLM: {e}")
            return ContextualAnalysis(
                actions=[],
                has_task_reference=False,
                extracted_context=f"Ошибка парсинга: {str(e)}"
            )

    async def analyze_context(self, user_message: str) -> ContextualAnalysis:
        """🧠 Гениальный анализ контекста сообщения"""
        try:
            logger.info(f"🔍 Анализируем контекст: '{user_message}'")
            
            # Получаем контекст существующих задач
            tasks_context = await self.get_tasks_context()
            
            # Анализируем через LLM
            llm_response = self.chain.invoke({
                "existing_tasks_context": tasks_context,
                "user_message": user_message
            })
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: используем универсальный парсер
            analysis = self.parse_llm_response(llm_response)
            
            logger.info(f"🧠 Результат анализа: actions={len(analysis.actions)} has_task_reference={analysis.has_task_reference}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка при анализе контекста: {e}")
            # ВСЕГДА возвращаем валидный объект
            return ContextualAnalysis(
                actions=[],
                has_task_reference=False,
                extracted_context=f"Ошибка анализа: {str(e)}"
            )
    
    async def find_target_task(self, task_reference: str) -> Optional[Dict[str, Any]]:
        """🎯 Поиск целевой задачи по ссылке"""
        try:
            logger.info(f"🎯 Ищем целевую задачу: '{task_reference}'")
            
            # Сначала пробуем точное совпадение (нечувствительно к регистру)
            response = await self.client.databases.query(
                database_id=self.tasks_db_id,
                page_size=100  # Получаем больше задач для поиска
            )
            
            best_match = None
            best_score = 0.0
            
            for page in response.get("results", []):
                properties = page.get("properties", {})
                task_title = properties.get("Задача", {}).get("title", [])
                if task_title:
                    title = task_title[0]["text"]["content"]
                    
                    # 1. Точное совпадение (нечувствительно к регистру)
                    if task_reference.lower() == title.lower():
                        logger.info(f"🎯 ТОЧНОЕ СОВПАДЕНИЕ: '{title}'")
                        return {
                            "id": page["id"],
                            "title": title,
                            "status": properties.get("Статус", {}).get("status", {}).get("name", ""),
                            "similarity": 1.0
                        }
                    
                    # 2. Содержит ли название задачи ключевые слова из ссылки
                    reference_words = set(re.findall(r'\b[а-яё]{3,}\b', task_reference.lower()))
                    title_words = set(re.findall(r'\b[а-яё]{3,}\b', title.lower()))
                    
                    # Проверяем пересечение слов
                    common_words = reference_words & title_words
                    if common_words:
                        # Вычисляем сходство на основе общих слов
                        word_similarity = len(common_words) / max(len(reference_words), 1)
                        
                        # Дополнительно проверяем общее сходство строк
                        string_similarity = SequenceMatcher(None, task_reference.lower(), title.lower()).ratio()
                        
                        # Комбинированный скор
                        combined_score = (word_similarity * 0.7) + (string_similarity * 0.3)
                        
                        if combined_score > best_score:
                            best_score = combined_score
                            best_match = {
                                "id": page["id"],
                                "title": title,
                                "status": properties.get("Статус", {}).get("status", {}).get("name", ""),
                                "similarity": combined_score
                            }
            
            if best_match and best_score > 0.4:  # Повышаем порог для лучшего качества
                logger.info(f"🎯 НАЙДЕНА ЦЕЛЕВАЯ ЗАДАЧА: '{best_match['title']}' (сходство: {best_score:.2f})")
                return best_match
            
            logger.warning(f"❌ Целевая задача не найдена для: '{task_reference}' (лучший скор: {best_score:.2f})")
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске целевой задачи: {e}")
            return None
    
    async def execute_action(self, action: TaskAction, target_task: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """⚡ Выполнение действия с задачей"""
        try:
            logger.info(f"⚡ Выполняем действие: {action.action_type} для '{target_task['title']}'")
            
            if action.action_type == "add_subtask":
                # Добавляем подзадачу
                subtask_id = await self._add_subtask(target_task["id"], action)
                return {
                    "success": True,
                    "action": "subtask_added",
                    "subtask_name": action.subtask_name,
                    "subtask_id": subtask_id,
                    "time_hours": action.time_hours
                }
                
            elif action.action_type == "update_time":
                # Обновляем время задачи
                await self._update_task_time(target_task["id"], action.time_hours)
                return {
                    "success": True,
                    "action": "time_updated",
                    "new_time": action.time_hours
                }
                
            elif action.action_type == "mark_done":
                # Отмечаем как выполненную
                await self._mark_task_done(target_task["id"])
                return {
                    "success": True,
                    "action": "marked_done"
                }
            
            return {"success": False, "error": "Неизвестное действие"}
            
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении действия: {e}")
            return {"success": False, "error": str(e)}
    
    async def _add_subtask(self, parent_task_id: str, action: TaskAction) -> Optional[str]:
        """Добавление подзадачи"""
        try:
            properties = {
                "Подзадачи": {
                    "title": [{"text": {"content": action.subtask_name or "Новая подзадача"}}]
                },
                "Статус": {"status": {"name": "To Do"}},
                "Задачи": {"relation": [{"id": parent_task_id}]}
            }
            
            if action.time_hours:
                properties["Время"] = {"number": action.time_hours}
            
            if action.description:
                properties["Описание"] = {
                    "rich_text": [{"text": {"content": action.description}}]
                }
            
            new_page = await self.client.pages.create(
                parent={"database_id": self.subtasks_db_id},
                properties=properties
            )
            
            logger.info(f"✅ Добавлена подзадача: {action.subtask_name} ({action.time_hours} ч)")
            return new_page["id"]
            
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении подзадачи: {e}")
            return None
    
    async def _update_task_time(self, task_id: str, time_hours: float):
        """Обновление времени задачи"""
        try:
            await self.client.pages.update(
                page_id=task_id,
                properties={"Часы": {"number": time_hours}}
            )
            logger.info(f"✅ Обновлено время задачи: {time_hours} ч")
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении времени: {e}")
    
    async def _mark_task_done(self, task_id: str):
        """Отметка задачи как выполненной"""
        try:
            await self.client.pages.update(
                page_id=task_id,
                properties={"Статус": {"status": {"name": "Done"}}}
            )
            logger.info(f"✅ Задача отмечена как выполненная")
        except Exception as e:
            logger.error(f"❌ Ошибка при отметке выполнения: {e}")

# Тест гениальной системы
async def test_contextual_analyzer():
    """Тест революционного анализатора"""
    analyzer = ContextualTaskAnalyzer()
    
    # Тестовые сообщения
    test_messages = [
        "К лого добавить час на правки силуэта",
        "В обложках YouTube потратил два часа на тексты",
        "Заставка готова, отметить как выполненную",
        "Добавить к логотипу подзадачу - цветовые варианты, полтора часа"
    ]
    
    for message in test_messages:
        print(f"\n🧠 Тест: '{message}'")
        analysis = await analyzer.analyze_context(message)
        print(f"Результат: {analysis}")

if __name__ == "__main__":
    asyncio.run(test_contextual_analyzer()) 