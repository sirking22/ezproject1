"""
🔧 Упрощенный менеджер для работы с Notion
Четкая работа с базами данных Notion без излишней сложности
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass 
class NotionResult:
    """Результат операции с Notion"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    
    def __bool__(self) -> bool:
        return self.success

class SimpleNotionManager:
    """
    🎯 Упрощенный менеджер для работы с Notion
    
    Фокус на простоте и надежности
    """
    
    def __init__(self, notion_client, database_schemas):
        """
        Инициализация с готовым клиентом и схемами
        
        Args:
            notion_client: Готовый AsyncClient для Notion
            database_schemas: Словарь схем баз данных
        """
        self.client = notion_client
        self.schemas = database_schemas
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }
        
    # ===== СОЗДАНИЕ ЗАПИСЕЙ =====
    
    async def create_task(self, task_data: Dict[str, Any]) -> NotionResult:
        """
        ➕ Создать задачу
        
        Args:
            task_data: Данные задачи
                - title: str - название
                - status: str - статус
                - description: str - описание
                - participants: List[str] - участники
                - priority: str - приоритет
                
        Returns:
            NotionResult с созданной записью
        """
        try:
            schema = self.schemas.get("tasks")
            if not schema:
                return NotionResult(False, error="Схема задач не найдена")
            
            # Преобразуем данные в формат Notion
            properties = {}
            
            # Название (обязательное поле)
            if "title" in task_data:
                properties["Задача"] = {
                    "title": [{"text": {"content": str(task_data["title"])}}]
                }
            
            # Статус
            if "status" in task_data:
                properties["Статус"] = {
                    "status": {"name": str(task_data["status"])}
                }
            
            # Описание
            if "description" in task_data:
                properties["Описание"] = {
                    "rich_text": [{"text": {"content": str(task_data["description"])}}]
                }
            
            # Участники
            if "participants" in task_data:
                participants = task_data["participants"]
                if isinstance(participants, list):
                    properties["Участники"] = {
                        "people": [{"id": str(p)} for p in participants]
                    }
            
            # Приоритет
            if "priority" in task_data:
                properties["! Задачи"] = {
                    "multi_select": [{"name": str(task_data["priority"])}]
                }
            
            # Дата
            if "date" in task_data:
                properties["Дата"] = {
                    "date": {"start": str(task_data["date"])}
                }
                
            self.stats['total_requests'] += 1
            
            # Создаем запись
            response = await self.client.pages.create(
                parent={"database_id": schema.database_id},
                properties=properties
            )
            
            self.stats['successful_requests'] += 1
            
            # Преобразуем ответ
            result = self._convert_page_to_dict(response)
            
            logger.info(f"✅ Создана задача: {result.get('id')}")
            return NotionResult(True, data=result)
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка создания задачи: {e}")
            return NotionResult(False, error=str(e))
    
    async def create_idea(self, idea_data: Dict[str, Any]) -> NotionResult:
        """
        💡 Создать идею
        
        Args:
            idea_data: Данные идеи
                - name: str - название
                - description: str - описание
                - tags: List[str] - теги
                - importance: int - важность (1-10)
                - url: str - ссылка
                
        Returns:
            NotionResult с созданной записью
        """
        try:
            schema = self.schemas.get("ideas")
            if not schema:
                return NotionResult(False, error="Схема идей не найдена")
            
            properties = {}
            
            # Название
            if "name" in idea_data:
                properties["Name"] = {
                    "title": [{"text": {"content": str(idea_data["name"])}}]
                }
            
            # Описание
            if "description" in idea_data:
                properties["Описание"] = {
                    "rich_text": [{"text": {"content": str(idea_data["description"])}}]
                }
            
            # Теги
            if "tags" in idea_data:
                tags = idea_data["tags"]
                if isinstance(tags, list):
                    properties["Теги"] = {
                        "multi_select": [{"name": str(tag)} for tag in tags]
                    }
                elif isinstance(tags, str):
                    # Разделяем по запятым
                    tag_list = [tag.strip() for tag in tags.split(",")]
                    properties["Теги"] = {
                        "multi_select": [{"name": tag} for tag in tag_list if tag]
                    }
            
            # Важность
            if "importance" in idea_data:
                properties["Вес"] = {
                    "number": float(idea_data["importance"])
                }
            
            # URL
            if "url" in idea_data:
                properties["URL"] = {
                    "url": str(idea_data["url"])
                }
            
            # Статус по умолчанию
            properties["Статус"] = {
                "status": {"name": "To do"}
            }
            
            self.stats['total_requests'] += 1
            
            response = await self.client.pages.create(
                parent={"database_id": schema.database_id},
                properties=properties
            )
            
            self.stats['successful_requests'] += 1
            
            result = self._convert_page_to_dict(response)
            
            logger.info(f"✅ Создана идея: {result.get('id')}")
            return NotionResult(True, data=result)
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка создания идеи: {e}")
            return NotionResult(False, error=str(e))
    
    async def create_material(self, material_data: Dict[str, Any]) -> NotionResult:
        """
        📁 Создать материал
        
        Args:
            material_data: Данные материала
                - name: str - название
                - description: str - описание
                - url: str - ссылка на файл
                - tags: List[str] - теги
                
        Returns:
            NotionResult с созданной записью
        """
        try:
            schema = self.schemas.get("materials")
            if not schema:
                return NotionResult(False, error="Схема материалов не найдена")
            
            properties = {}
            
            # Название
            if "name" in material_data:
                properties["Name"] = {
                    "title": [{"text": {"content": str(material_data["name"])}}]
                }
            
            # URL
            if "url" in material_data:
                properties["URL"] = {
                    "url": str(material_data["url"])
                }
            
            # Описание
            if "description" in material_data:
                properties["Описание"] = {
                    "rich_text": [{"text": {"content": str(material_data["description"])}}]
                }
            
            # Теги
            if "tags" in material_data:
                tags = material_data["tags"]
                if isinstance(tags, list):
                    properties["Теги"] = {
                        "multi_select": [{"name": str(tag)} for tag in tags]
                    }
            
            # Статус по умолчанию
            properties["Статус"] = {
                "status": {"name": "Ок"}
            }
            
            self.stats['total_requests'] += 1
            
            response = await self.client.pages.create(
                parent={"database_id": schema.database_id},
                properties=properties
            )
            
            self.stats['successful_requests'] += 1
            
            result = self._convert_page_to_dict(response)
            
            logger.info(f"✅ Создан материал: {result.get('id')}")
            return NotionResult(True, data=result)
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка создания материала: {e}")
            return NotionResult(False, error=str(e))
    
    # ===== ПОЛУЧЕНИЕ ЗАПИСЕЙ =====
    
    async def get_tasks(self, filters: Optional[Dict[str, Any]] = None, limit: int = 50) -> NotionResult:
        """
        📋 Получить задачи
        
        Args:
            filters: Фильтры (status, participant, etc.)
            limit: Лимит записей
            
        Returns:
            NotionResult со списком задач
        """
        try:
            schema = self.schemas.get("tasks")
            if not schema:
                return NotionResult(False, error="Схема задач не найдена")
            
            query = {
                "database_id": schema.database_id,
                "page_size": limit
            }
            
            # Добавляем фильтры
            if filters:
                filter_conditions = []
                
                # Фильтр по статусу
                if "status" in filters:
                    filter_conditions.append({
                        "property": "Статус",
                        "status": {"equals": filters["status"]}
                    })
                
                # Фильтр по участнику
                if "participant" in filters:
                    filter_conditions.append({
                        "property": "Участники",
                        "people": {"contains": filters["participant"]}
                    })
                
                if filter_conditions:
                    if len(filter_conditions) == 1:
                        query["filter"] = filter_conditions[0]
                    else:
                        query["filter"] = {"and": filter_conditions}
            
            self.stats['total_requests'] += 1
            
            response = await self.client.databases.query(**query)
            
            self.stats['successful_requests'] += 1
            
            # Преобразуем результаты
            tasks = []
            for page in response.get("results", []):
                task_dict = self._convert_page_to_dict(page)
                tasks.append(task_dict)
            
            logger.info(f"✅ Получено {len(tasks)} задач")
            return NotionResult(True, data=tasks)
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка получения задач: {e}")
            return NotionResult(False, error=str(e))
    
    async def get_ideas(self, limit: int = 50) -> NotionResult:
        """📝 Получить идеи"""
        try:
            schema = self.schemas.get("ideas")
            if not schema:
                return NotionResult(False, error="Схема идей не найдена")
            
            query = {
                "database_id": schema.database_id,
                "page_size": limit,
                "sorts": [{"property": "Вес", "direction": "descending"}]
            }
            
            self.stats['total_requests'] += 1
            
            response = await self.client.databases.query(**query)
            
            self.stats['successful_requests'] += 1
            
            ideas = []
            for page in response.get("results", []):
                idea_dict = self._convert_page_to_dict(page)
                ideas.append(idea_dict)
            
            logger.info(f"✅ Получено {len(ideas)} идей")
            return NotionResult(True, data=ideas)
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка получения идей: {e}")
            return NotionResult(False, error=str(e))
    
    # ===== ОБНОВЛЕНИЕ ЗАПИСЕЙ =====
    
    async def update_task_status(self, task_id: str, status: str) -> NotionResult:
        """
        ✏️ Обновить статус задачи
        
        Args:
            task_id: ID задачи
            status: Новый статус
            
        Returns:
            NotionResult с обновленной записью
        """
        try:
            properties = {
                "Статус": {
                    "status": {"name": status}
                }
            }
            
            self.stats['total_requests'] += 1
            
            response = await self.client.pages.update(
                page_id=task_id,
                properties=properties
            )
            
            self.stats['successful_requests'] += 1
            
            result = self._convert_page_to_dict(response)
            
            logger.info(f"✅ Обновлен статус задачи {task_id} на {status}")
            return NotionResult(True, data=result)
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка обновления статуса задачи: {e}")
            return NotionResult(False, error=str(e))
    
    async def set_cover_image(self, page_id: str, image_url: str) -> NotionResult:
        """
        🖼️ Установить обложку для страницы
        
        Args:
            page_id: ID страницы
            image_url: URL изображения
            
        Returns:
            NotionResult с результатом
        """
        try:
            # Устанавливаем обложку
            cover_data = {
                "cover": {
                    "type": "external",
                    "external": {"url": image_url}
                }
            }
            
            self.stats['total_requests'] += 1
            
            response = await self.client.pages.update(
                page_id=page_id,
                **cover_data
            )
            
            self.stats['successful_requests'] += 1
            
            logger.info(f"✅ Установлена обложка для страницы {page_id}")
            return NotionResult(True, data={"cover_url": image_url})
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка установки обложки: {e}")
            return NotionResult(False, error=str(e))
    
    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====
    
    def _convert_page_to_dict(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразование страницы Notion в упрощенный словарь"""
        result = {
            'id': page['id'],
            'created_time': page['created_time'],
            'last_edited_time': page['last_edited_time'],
            'archived': page.get('archived', False),
            'url': page.get('url', ''),
            'cover': page.get('cover', {}),
            'properties': {}
        }
        
        # Преобразуем свойства
        for prop_name, prop_data in page.get('properties', {}).items():
            prop_type = prop_data.get('type')
            
            try:
                if prop_type == 'title' and prop_data.get('title'):
                    result['properties'][prop_name] = prop_data['title'][0]['text']['content']
                elif prop_type == 'rich_text' and prop_data.get('rich_text'):
                    if prop_data['rich_text']:
                        result['properties'][prop_name] = prop_data['rich_text'][0]['text']['content']
                    else:
                        result['properties'][prop_name] = ""
                elif prop_type == 'select' and prop_data.get('select'):
                    result['properties'][prop_name] = prop_data['select']['name']
                elif prop_type == 'status' and prop_data.get('status'):
                    result['properties'][prop_name] = prop_data['status']['name']
                elif prop_type == 'multi_select':
                    result['properties'][prop_name] = [item['name'] for item in prop_data.get('multi_select', [])]
                elif prop_type == 'number':
                    result['properties'][prop_name] = prop_data.get('number')
                elif prop_type == 'date' and prop_data.get('date'):
                    result['properties'][prop_name] = prop_data['date']['start']
                elif prop_type == 'url':
                    result['properties'][prop_name] = prop_data.get('url')
                elif prop_type == 'people':
                    result['properties'][prop_name] = [
                        {"id": person['id'], "name": person.get('name', '')}
                        for person in prop_data.get('people', [])
                    ]
                elif prop_type == 'relation':
                    result['properties'][prop_name] = [rel['id'] for rel in prop_data.get('relation', [])]
                else:
                    # Для неизвестных типов сохраняем как есть
                    result['properties'][prop_name] = prop_data
            except (IndexError, KeyError, TypeError) as e:
                # Если не удалось преобразовать свойство, логируем и пропускаем
                logger.warning(f"⚠️ Не удалось преобразовать свойство {prop_name}: {e}")
                result['properties'][prop_name] = None
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Получить статистику"""
        total = self.stats['total_requests']
        successful = self.stats['successful_requests']
        
        return {
            'total_requests': total,
            'successful_requests': successful,
            'failed_requests': self.stats['failed_requests'],
            'success_rate': (successful / max(total, 1)) * 100
        }
    
    def reset_stats(self) -> None:
        """🔄 Сбросить статистику"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }