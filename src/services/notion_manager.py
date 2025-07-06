"""
🔧 Главный менеджер для работы с Notion
Централизованная система для управления всеми базами данных Notion
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, TypeVar, Generic
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    from notion_client import AsyncClient
    from notion_client.errors import NotionClientError, APIResponseError
except ImportError:
    # Fallback если notion_client не установлен
    AsyncClient = None
    NotionClientError = Exception
    APIResponseError = Exception

from ..models.notion_models import NotionPage, NotionDatabase
try:
    from ..config import get_settings
except ImportError:
    # Fallback для конфигурации
    def get_settings():
        return type('Settings', (), {'NOTION_TOKEN': ''})()

try:
    from notion_database_schemas import (
        get_database_schema, 
        get_database_id, 
        validate_property_value,
        get_status_options,
        get_select_options,
        get_multi_select_options,
        DatabaseSchema
    )
except ImportError:
    # Fallback функции
    def get_database_schema(db_name): return None
    def get_database_id(db_name): return ""
    def validate_property_value(db_name, field_name, value): return True
    def get_status_options(db_name, field_name): return []
    def get_select_options(db_name, field_name): return []
    def get_multi_select_options(db_name, field_name): return []
    DatabaseSchema = None

logger = logging.getLogger(__name__)

# Типы данных
T = TypeVar('T')

class NotionError(Exception):
    """Базовая ошибка работы с Notion"""
    pass

class ValidationError(NotionError):
    """Ошибка валидации данных"""
    pass

class DatabaseNotFoundError(NotionError):
    """База данных не найдена"""
    pass

class OperationResult(Generic[T]):
    """Результат операции с детальной информацией"""
    
    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.now()
    
    def __bool__(self) -> bool:
        return self.success

@dataclass
class FilterCondition:
    """Условие фильтрации"""
    property: str
    condition: str  # equals, contains, not_equals, etc.
    value: Any

@dataclass
class SortCondition:
    """Условие сортировки"""
    property: str
    direction: str = "ascending"  # ascending, descending

class NotionManager:
    """
    🎯 Главный менеджер для работы с Notion
    
    Предоставляет высокоуровневый API для работы со всеми базами данных
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncClient(auth=self.settings.NOTION_TOKEN)
        self._schema_cache: Dict[str, DatabaseSchema] = {}
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'databases_accessed': set()
        }
        
    async def initialize(self) -> None:
        """Инициализация менеджера"""
        logger.info("🔧 Инициализация NotionManager...")
        
        # Проверяем доступность API
        try:
            await self.client.users.me()
            logger.info("✅ Соединение с Notion API установлено")
        except Exception as e:
            logger.error(f"❌ Ошибка соединения с Notion API: {e}")
            raise NotionError(f"Не удалось подключиться к Notion API: {e}")
    
    async def cleanup(self) -> None:
        """Очистка ресурсов"""
        if hasattr(self.client, 'close'):
            await self.client.close()
        logger.info("🧹 NotionManager очищен")
    
    # ===== РАБОТА С БАЗАМИ ДАННЫХ =====
    
    async def get_database_info(self, db_name: str) -> OperationResult[Dict[str, Any]]:
        """
        📊 Получить информацию о базе данных
        
        Args:
            db_name: Имя базы данных из схемы
            
        Returns:
            Результат с информацией о базе данных
        """
        try:
            schema = get_database_schema(db_name)
            if not schema:
                return OperationResult(False, error=f"Схема базы данных '{db_name}' не найдена")
            
            self._stats['total_requests'] += 1
            self._stats['databases_accessed'].add(db_name)
            
            # Получаем метаданные из Notion
            database = await self.client.databases.retrieve(database_id=schema.database_id)
            
            self._stats['successful_requests'] += 1
            
            info = {
                'id': database['id'],
                'title': database['title'],
                'description': schema.description,
                'properties_count': len(database['properties']),
                'schema': schema,
                'notion_metadata': database
            }
            
            return OperationResult(True, data=info)
            
        except Exception as e:
            self._stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка получения информации о базе данных '{db_name}': {e}")
            return OperationResult(False, error=str(e))
    
    # ===== СОЗДАНИЕ ЗАПИСЕЙ =====
    
    async def create_record(
        self, 
        db_name: str, 
        data: Dict[str, Any], 
        validate: bool = True
    ) -> OperationResult[Dict[str, Any]]:
        """
        ➕ Создать запись в базе данных
        
        Args:
            db_name: Имя базы данных
            data: Данные для создания записи
            validate: Валидировать данные перед созданием
            
        Returns:
            Результат создания записи
        """
        try:
            schema = get_database_schema(db_name)
            if not schema:
                return OperationResult(False, error=f"Схема базы данных '{db_name}' не найдена")
            
            # Валидация данных
            if validate:
                validation_result = self._validate_data(db_name, data)
                if not validation_result.success:
                    return validation_result
            
            # Преобразуем данные в формат Notion
            properties = self._convert_to_notion_properties(db_name, data)
            
            self._stats['total_requests'] += 1
            self._stats['databases_accessed'].add(db_name)
            
            # Создаем запись
            response = await self.client.pages.create(
                parent={"database_id": schema.database_id},
                properties=properties
            )
            
            self._stats['successful_requests'] += 1
            
            # Преобразуем ответ обратно в наш формат
            result_data = self._convert_from_notion_page(response)
            
            logger.info(f"✅ Создана запись в базе '{db_name}': {result_data.get('id', 'unknown')}")
            
            return OperationResult(True, data=result_data)
            
        except Exception as e:
            self._stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка создания записи в базе '{db_name}': {e}")
            return OperationResult(False, error=str(e))
    
    # ===== ПОЛУЧЕНИЕ ЗАПИСЕЙ =====
    
    async def get_record(self, db_name: str, record_id: str) -> OperationResult[Dict[str, Any]]:
        """
        🔍 Получить запись по ID
        
        Args:
            db_name: Имя базы данных
            record_id: ID записи
            
        Returns:
            Результат получения записи
        """
        try:
            self._stats['total_requests'] += 1
            self._stats['databases_accessed'].add(db_name)
            
            # Получаем запись
            response = await self.client.pages.retrieve(page_id=record_id)
            
            self._stats['successful_requests'] += 1
            
            # Преобразуем в наш формат
            result_data = self._convert_from_notion_page(response)
            
            return OperationResult(True, data=result_data)
            
        except Exception as e:
            self._stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка получения записи '{record_id}' из базы '{db_name}': {e}")
            return OperationResult(False, error=str(e))
    
    async def query_records(
        self,
        db_name: str,
        filters: Optional[List[FilterCondition]] = None,
        sorts: Optional[List[SortCondition]] = None,
        limit: Optional[int] = None
    ) -> OperationResult[List[Dict[str, Any]]]:
        """
        🔍 Запросить записи с фильтрацией и сортировкой
        
        Args:
            db_name: Имя базы данных
            filters: Условия фильтрации
            sorts: Условия сортировки
            limit: Лимит записей
            
        Returns:
            Результат запроса записей
        """
        try:
            schema = get_database_schema(db_name)
            if not schema:
                return OperationResult(False, error=f"Схема базы данных '{db_name}' не найдена")
            
            # Строим запрос
            query = {
                "database_id": schema.database_id,
                "page_size": limit or 100
            }
            
            # Добавляем фильтры
            if filters:
                filter_conditions = []
                for f in filters:
                    filter_conditions.append(self._build_filter_condition(f))
                
                if len(filter_conditions) == 1:
                    query["filter"] = filter_conditions[0]
                else:
                    query["filter"] = {"and": filter_conditions}
            
            # Добавляем сортировку
            if sorts:
                query["sorts"] = [
                    {
                        "property": s.property,
                        "direction": s.direction
                    }
                    for s in sorts
                ]
            
            self._stats['total_requests'] += 1
            self._stats['databases_accessed'].add(db_name)
            
            # Выполняем запрос
            response = await self.client.databases.query(**query)
            
            self._stats['successful_requests'] += 1
            
            # Преобразуем результаты
            results = []
            for page in response.get("results", []):
                try:
                    result_data = self._convert_from_notion_page(page)
                    results.append(result_data)
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка преобразования записи: {e}")
                    continue
            
            logger.info(f"✅ Получено {len(results)} записей из базы '{db_name}'")
            
            return OperationResult(True, data=results)
            
        except Exception as e:
            self._stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка запроса записей из базы '{db_name}': {e}")
            return OperationResult(False, error=str(e))
    
    # ===== ОБНОВЛЕНИЕ ЗАПИСЕЙ =====
    
    async def update_record(
        self, 
        db_name: str, 
        record_id: str, 
        data: Dict[str, Any],
        validate: bool = True
    ) -> OperationResult[Dict[str, Any]]:
        """
        ✏️ Обновить запись
        
        Args:
            db_name: Имя базы данных
            record_id: ID записи
            data: Данные для обновления
            validate: Валидировать данные перед обновлением
            
        Returns:
            Результат обновления записи
        """
        try:
            schema = get_database_schema(db_name)
            if not schema:
                return OperationResult(False, error=f"Схема базы данных '{db_name}' не найдена")
            
            # Валидация данных
            if validate:
                validation_result = self._validate_data(db_name, data)
                if not validation_result.success:
                    return validation_result
            
            # Преобразуем данные в формат Notion
            properties = self._convert_to_notion_properties(db_name, data)
            
            self._stats['total_requests'] += 1
            self._stats['databases_accessed'].add(db_name)
            
            # Обновляем запись
            response = await self.client.pages.update(
                page_id=record_id,
                properties=properties
            )
            
            self._stats['successful_requests'] += 1
            
            # Преобразуем ответ обратно в наш формат
            result_data = self._convert_from_notion_page(response)
            
            logger.info(f"✅ Обновлена запись '{record_id}' в базе '{db_name}'")
            
            return OperationResult(True, data=result_data)
            
        except Exception as e:
            self._stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка обновления записи '{record_id}' в базе '{db_name}': {e}")
            return OperationResult(False, error=str(e))
    
    # ===== УДАЛЕНИЕ ЗАПИСЕЙ =====
    
    async def delete_record(self, db_name: str, record_id: str) -> OperationResult[bool]:
        """
        🗑️ Удалить запись (архивировать)
        
        Args:
            db_name: Имя базы данных
            record_id: ID записи
            
        Returns:
            Результат удаления записи
        """
        try:
            self._stats['total_requests'] += 1
            self._stats['databases_accessed'].add(db_name)
            
            # Архивируем запись
            await self.client.pages.update(
                page_id=record_id,
                archived=True
            )
            
            self._stats['successful_requests'] += 1
            
            logger.info(f"✅ Удалена запись '{record_id}' из базы '{db_name}'")
            
            return OperationResult(True, data=True)
            
        except Exception as e:
            self._stats['failed_requests'] += 1
            logger.error(f"❌ Ошибка удаления записи '{record_id}' из базы '{db_name}': {e}")
            return OperationResult(False, error=str(e))
    
    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====
    
    def _validate_data(self, db_name: str, data: Dict[str, Any]) -> OperationResult[bool]:
        """Валидация данных перед отправкой в Notion"""
        try:
            schema = get_database_schema(db_name)
            if not schema:
                return OperationResult(False, error=f"Схема базы данных '{db_name}' не найдена")
            
            errors = []
            
            # Проверяем каждое поле
            for field_name, field_value in data.items():
                # Проверяем, что поле существует в схеме
                if field_name not in schema.properties:
                    errors.append(f"Поле '{field_name}' не существует в схеме базы данных")
                    continue
                
                # Валидируем значение
                if not validate_property_value(db_name, field_name, field_value):
                    valid_options = (
                        get_status_options(db_name, field_name) or
                        get_select_options(db_name, field_name) or
                        get_multi_select_options(db_name, field_name)
                    )
                    if valid_options:
                        errors.append(f"Недопустимое значение '{field_value}' для поля '{field_name}'. Допустимые значения: {valid_options}")
                    else:
                        errors.append(f"Недопустимое значение '{field_value}' для поля '{field_name}'")
            
            if errors:
                return OperationResult(False, error=f"Ошибки валидации: {'; '.join(errors)}")
            
            return OperationResult(True, data=True)
            
        except Exception as e:
            return OperationResult(False, error=f"Ошибка валидации: {e}")
    
    def _convert_to_notion_properties(self, db_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразование данных в формат Notion"""
        schema = get_database_schema(db_name)
        if not schema:
            raise ValueError(f"Схема базы данных '{db_name}' не найдена")
        
        properties = {}
        
        for field_name, field_value in data.items():
            if field_name not in schema.properties:
                continue
            
            property_config = schema.properties[field_name]
            property_type = property_config.get('type')
            
            # Преобразуем в зависимости от типа
            if property_type == 'title':
                properties[field_name] = {
                    "title": [{"text": {"content": str(field_value)}}]
                }
            elif property_type == 'rich_text':
                properties[field_name] = {
                    "rich_text": [{"text": {"content": str(field_value)}}]
                }
            elif property_type == 'select':
                properties[field_name] = {
                    "select": {"name": str(field_value)}
                }
            elif property_type == 'multi_select':
                if isinstance(field_value, list):
                    properties[field_name] = {
                        "multi_select": [{"name": str(v)} for v in field_value]
                    }
                else:
                    properties[field_name] = {
                        "multi_select": [{"name": str(field_value)}]
                    }
            elif property_type == 'number':
                properties[field_name] = {
                    "number": float(field_value) if field_value is not None else None
                }
            elif property_type == 'date':
                if isinstance(field_value, str):
                    properties[field_name] = {
                        "date": {"start": field_value}
                    }
                elif isinstance(field_value, datetime):
                    properties[field_name] = {
                        "date": {"start": field_value.isoformat()}
                    }
            elif property_type == 'url':
                properties[field_name] = {
                    "url": str(field_value) if field_value else None
                }
            elif property_type == 'status':
                properties[field_name] = {
                    "status": {"name": str(field_value)}
                }
            elif property_type == 'people':
                if isinstance(field_value, list):
                    properties[field_name] = {
                        "people": [{"id": str(v)} for v in field_value]
                    }
                else:
                    properties[field_name] = {
                        "people": [{"id": str(field_value)}]
                    }
            elif property_type == 'relation':
                if isinstance(field_value, list):
                    properties[field_name] = {
                        "relation": [{"id": str(v)} for v in field_value]
                    }
                else:
                    properties[field_name] = {
                        "relation": [{"id": str(field_value)}]
                    }
        
        return properties
    
    def _convert_from_notion_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразование страницы Notion в наш формат"""
        result = {
            'id': page['id'],
            'created_time': page['created_time'],
            'last_edited_time': page['last_edited_time'],
            'archived': page.get('archived', False),
            'url': page.get('url', ''),
            'properties': {}
        }
        
        # Преобразуем свойства
        for prop_name, prop_data in page.get('properties', {}).items():
            prop_type = prop_data.get('type')
            
            if prop_type == 'title' and prop_data.get('title'):
                result['properties'][prop_name] = prop_data['title'][0]['text']['content']
            elif prop_type == 'rich_text' and prop_data.get('rich_text'):
                result['properties'][prop_name] = prop_data['rich_text'][0]['text']['content']
            elif prop_type == 'select' and prop_data.get('select'):
                result['properties'][prop_name] = prop_data['select']['name']
            elif prop_type == 'multi_select':
                result['properties'][prop_name] = [item['name'] for item in prop_data.get('multi_select', [])]
            elif prop_type == 'number':
                result['properties'][prop_name] = prop_data.get('number')
            elif prop_type == 'date' and prop_data.get('date'):
                result['properties'][prop_name] = prop_data['date']['start']
            elif prop_type == 'url':
                result['properties'][prop_name] = prop_data.get('url')
            elif prop_type == 'status' and prop_data.get('status'):
                result['properties'][prop_name] = prop_data['status']['name']
            elif prop_type == 'people':
                result['properties'][prop_name] = [person['id'] for person in prop_data.get('people', [])]
            elif prop_type == 'relation':
                result['properties'][prop_name] = [rel['id'] for rel in prop_data.get('relation', [])]
        
        return result
    
    def _build_filter_condition(self, filter_condition: FilterCondition) -> Dict[str, Any]:
        """Построение условия фильтрации для Notion API"""
        prop_name = filter_condition.property
        condition = filter_condition.condition
        value = filter_condition.value
        
        # Определяем тип свойства (можно улучшить через схему)
        if condition in ['equals', 'does_not_equal']:
            return {
                "property": prop_name,
                "select": {condition: value}
            }
        elif condition == 'contains':
            return {
                "property": prop_name,
                "multi_select": {"contains": value}
            }
        elif condition in ['is_empty', 'is_not_empty']:
            return {
                "property": prop_name,
                "rich_text": {condition: True}
            }
        else:
            # Fallback для других условий
            return {
                "property": prop_name,
                "rich_text": {"contains": str(value)}
            }
    
    # ===== СТАТИСТИКА =====
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику использования"""
        return {
            'total_requests': self._stats['total_requests'],
            'successful_requests': self._stats['successful_requests'],
            'failed_requests': self._stats['failed_requests'],
            'success_rate': (
                self._stats['successful_requests'] / max(self._stats['total_requests'], 1) * 100
            ),
            'databases_accessed': list(self._stats['databases_accessed']),
            'databases_count': len(self._stats['databases_accessed'])
        }
    
    def reset_stats(self) -> None:
        """Сбросить статистику"""
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'databases_accessed': set()
        }