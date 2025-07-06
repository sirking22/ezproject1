"""
Advanced Notion Service with mass editing, relationships, and bulk operations
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from notion_client import AsyncClient

logger = logging.getLogger(__name__)

@dataclass
class NotionFilter:
    """Класс для фильтрации данных в Notion"""
    property_name: str
    condition: str
    value: Any

@dataclass
class NotionUpdate:
    """Класс для обновления данных в Notion"""
    property_name: str
    new_value: Any
    property_type: str = "rich_text"

@dataclass
class NotionRelation:
    """Класс для работы с связями в Notion"""
    source_page_id: str
    target_page_id: str
    relation_property: str

class AdvancedNotionService:
    """Продвинутый сервис для работы с Notion"""
    
    def __init__(self):
        self.client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.databases = self._load_databases()
        self.batch_size = 100
        self.max_concurrent = 10
        
    def _load_databases(self) -> Dict[str, str]:
        """Загружает все ID баз данных из переменных окружения"""
        databases = {}
        for key, value in os.environ.items():
            if key.startswith("NOTION_") and key.endswith("_DB_ID"):
                db_name = key.replace("NOTION_", "").replace("_DB_ID", "").lower()
                databases[db_name] = value
        return databases
    
    async def get_database_schema(self, db_id: str) -> Dict[str, Any]:
        """Получает схему базы данных"""
        try:
            response = await self.client.databases.retrieve(database_id=db_id)
            return response.get("properties", {})
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return {}
    
    async def query_database_bulk(
        self, 
        db_id: str, 
        filters: Optional[List[NotionFilter]] = None,
        sorts: Optional[List[Dict]] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Массовый запрос данных из базы"""
        try:
            query_params = {}
            
            # Добавляем фильтры
            if filters:
                query_params["filter"] = self._build_filters(filters)
            
            # Добавляем сортировку
            if sorts:
                query_params["sorts"] = sorts
            
            # Получаем все страницы
            all_results = []
            has_more = True
            next_cursor = None
            
            while has_more and (limit is None or len(all_results) < limit):
                if next_cursor:
                    query_params["start_cursor"] = next_cursor
                
                response = await self.client.databases.query(
                    database_id=db_id,
                    **query_params
                )
                
                results = response.get("results", [])
                all_results.extend(results)
                
                has_more = response.get("has_more", False)
                next_cursor = response.get("next_cursor")
                
                if limit and len(all_results) >= limit:
                    all_results = all_results[:limit]
                    break
                    
            return all_results
            
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            return []
    
    def _build_filters(self, filters: List[NotionFilter]) -> Dict:
        """Строит фильтры для запроса"""
        if len(filters) == 1:
            return self._build_single_filter(filters[0])
        
        # Для множественных фильтров используем AND
        return {
            "and": [self._build_single_filter(f) for f in filters]
        }
    
    def _build_single_filter(self, filter_obj: NotionFilter) -> Dict:
        """Строит единичный фильтр"""
        return {
            "property": filter_obj.property_name,
            filter_obj.condition: filter_obj.value
        }
    
    async def update_pages_bulk(
        self, 
        page_updates: List[Tuple[str, List[NotionUpdate]]]
    ) -> List[Dict]:
        """Массовое обновление страниц"""
        
        async def update_single_page(page_id: str, updates: List[NotionUpdate]):
            try:
                properties = {}
                for update in updates:
                    properties[update.property_name] = self._format_property_value(
                        update.new_value, 
                        update.property_type
                    )
                
                response = await self.client.pages.update(
                    page_id=page_id,
                    properties=properties
                )
                return {"success": True, "page_id": page_id, "response": response}
                
            except Exception as e:
                logger.error(f"Error updating page {page_id}: {e}")
                return {"success": False, "page_id": page_id, "error": str(e)}
        
        # Выполняем обновления пачками
        results = []
        for i in range(0, len(page_updates), self.max_concurrent):
            batch = page_updates[i:i + self.max_concurrent]
            
            tasks = [
                update_single_page(page_id, updates) 
                for page_id, updates in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Небольшая пауза между пачками
            if i + self.max_concurrent < len(page_updates):
                await asyncio.sleep(0.1)
        
        return results
    
    def _format_property_value(self, value: Any, property_type: str) -> Dict:
        """Форматирует значение свойства для Notion API"""
        
        if property_type == "rich_text":
            return {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": str(value)}
                    }
                ]
            }
        
        elif property_type == "title":
            return {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": str(value)}
                    }
                ]
            }
        
        elif property_type == "number":
            return {"number": float(value) if value else None}
        
        elif property_type == "select":
            return {"select": {"name": str(value)} if value else None}
        
        elif property_type == "multi_select":
            if isinstance(value, list):
                return {"multi_select": [{"name": str(v)} for v in value]}
            else:
                return {"multi_select": [{"name": str(value)}]}
        
        elif property_type == "date":
            if isinstance(value, datetime):
                return {"date": {"start": value.isoformat()}}
            elif isinstance(value, str):
                return {"date": {"start": value}}
            else:
                return {"date": None}
        
        elif property_type == "checkbox":
            return {"checkbox": bool(value)}
        
        elif property_type == "url":
            return {"url": str(value) if value else None}
        
        elif property_type == "email":
            return {"email": str(value) if value else None}
        
        elif property_type == "phone_number":
            return {"phone_number": str(value) if value else None}
        
        elif property_type == "relation":
            if isinstance(value, list):
                return {"relation": [{"id": str(v)} for v in value]}
            else:
                return {"relation": [{"id": str(value)}]}
        
        else:
            # Fallback для неизвестных типов
            return {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": str(value)}
                    }
                ]
            }
    
    async def create_relations_bulk(self, relations: List[NotionRelation]) -> List[Dict]:
        """Массовое создание связей между страницами"""
        
        async def create_single_relation(relation: NotionRelation):
            try:
                # Получаем текущие связи
                page = await self.client.pages.retrieve(page_id=relation.source_page_id)
                current_relations = page["properties"].get(relation.relation_property, {}).get("relation", [])
                
                # Добавляем новую связь
                new_relations = current_relations + [{"id": relation.target_page_id}]
                
                # Обновляем страницу
                response = await self.client.pages.update(
                    page_id=relation.source_page_id,
                    properties={
                        relation.relation_property: {"relation": new_relations}
                    }
                )
                
                return {"success": True, "relation": relation, "response": response}
                
            except Exception as e:
                logger.error(f"Error creating relation: {e}")
                return {"success": False, "relation": relation, "error": str(e)}
        
        # Выполняем создание связей пачками
        results = []
        for i in range(0, len(relations), self.max_concurrent):
            batch = relations[i:i + self.max_concurrent]
            
            tasks = [create_single_relation(relation) for relation in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
            if i + self.max_concurrent < len(relations):
                await asyncio.sleep(0.1)
        
        return results
    
    async def analyze_database_content(self, db_id: str, analysis_type: str = "summary") -> Dict:
        """Анализирует содержимое базы данных"""
        try:
            # Получаем все данные
            all_pages = await self.query_database_bulk(db_id)
            
            if analysis_type == "summary":
                return {
                    "total_pages": len(all_pages),
                    "database_id": db_id,
                    "properties": await self.get_database_schema(db_id),
                    "sample_pages": all_pages[:5] if all_pages else []
                }
            
            elif analysis_type == "detailed":
                # Подробный анализ
                schema = await self.get_database_schema(db_id)
                analysis = {
                    "total_pages": len(all_pages),
                    "database_id": db_id,
                    "properties": schema,
                    "property_stats": {}
                }
                
                # Анализ каждого свойства
                for prop_name, prop_config in schema.items():
                    prop_type = prop_config.get("type")
                    stats = {"type": prop_type, "filled_count": 0, "unique_values": set()}
                    
                    for page in all_pages:
                        prop_value = page.get("properties", {}).get(prop_name)
                        if prop_value and self._is_property_filled(prop_value, prop_type):
                            stats["filled_count"] += 1
                            value = self._extract_property_value(prop_value, prop_type)
                            if value:
                                stats["unique_values"].add(str(value))
                    
                    stats["unique_values"] = list(stats["unique_values"])[:10]  # Лимит для примера
                    stats["fill_rate"] = stats["filled_count"] / len(all_pages) if all_pages else 0
                    analysis["property_stats"][prop_name] = stats
                
                return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing database: {e}")
            return {"error": str(e)}
    
    def _is_property_filled(self, prop_value: Dict, prop_type: str) -> bool:
        """Проверяет, заполнено ли свойство"""
        if prop_type == "rich_text":
            return bool(prop_value.get("rich_text", []))
        elif prop_type == "title":
            return bool(prop_value.get("title", []))
        elif prop_type == "number":
            return prop_value.get("number") is not None
        elif prop_type == "select":
            return prop_value.get("select") is not None
        elif prop_type == "multi_select":
            return bool(prop_value.get("multi_select", []))
        elif prop_type == "date":
            return prop_value.get("date") is not None
        elif prop_type == "checkbox":
            return True  # Checkbox всегда имеет значение
        elif prop_type == "relation":
            return bool(prop_value.get("relation", []))
        else:
            return bool(prop_value)
    
    def _extract_property_value(self, prop_value: Dict, prop_type: str) -> Any:
        """Извлекает значение свойства"""
        if prop_type == "rich_text":
            texts = prop_value.get("rich_text", [])
            return " ".join([t.get("text", {}).get("content", "") for t in texts])
        elif prop_type == "title":
            titles = prop_value.get("title", [])
            return " ".join([t.get("text", {}).get("content", "") for t in titles])
        elif prop_type == "number":
            return prop_value.get("number")
        elif prop_type == "select":
            select = prop_value.get("select")
            return select.get("name") if select else None
        elif prop_type == "multi_select":
            return [ms.get("name") for ms in prop_value.get("multi_select", [])]
        elif prop_type == "date":
            date = prop_value.get("date")
            return date.get("start") if date else None
        elif prop_type == "checkbox":
            return prop_value.get("checkbox")
        elif prop_type == "relation":
            return [r.get("id") for r in prop_value.get("relation", [])]
        else:
            return str(prop_value)
    
    async def smart_search(self, query: str, databases: Optional[List[str]] = None) -> Dict:
        """Умный поиск по базам данных"""
        if databases is None:
            databases = list(self.databases.keys())
        
        results = {}
        
        for db_name in databases:
            if db_name not in self.databases:
                continue
                
            db_id = self.databases[db_name]
            
            try:
                # Получаем схему базы данных
                schema = await self.get_database_schema(db_id)
                
                # Ищем в текстовых полях
                text_properties = [
                    name for name, config in schema.items() 
                    if config.get("type") in ["rich_text", "title"]
                ]
                
                if not text_properties:
                    continue
                
                # Создаем фильтры для поиска
                filters = []
                for prop_name in text_properties:
                    prop_type = schema[prop_name].get("type")
                    if prop_type == "rich_text":
                        filters.append(NotionFilter(
                            property_name=prop_name,
                            condition="rich_text",
                            value={"contains": query}
                        ))
                    elif prop_type == "title":
                        filters.append(NotionFilter(
                            property_name=prop_name,
                            condition="title",
                            value={"contains": query}
                        ))
                
                # Выполняем поиск с OR фильтром
                if len(filters) > 1:
                    filter_config = {"or": [self._build_single_filter(f) for f in filters]}
                elif len(filters) == 1:
                    filter_config = self._build_single_filter(filters[0])
                else:
                    continue
                
                search_results = await self.client.databases.query(
                    database_id=db_id,
                    filter=filter_config
                )
                
                results[db_name] = search_results.get("results", [])
                
            except Exception as e:
                logger.error(f"Error searching in {db_name}: {e}")
                results[db_name] = []
        
        return results
    
    async def get_database_by_name(self, name: str) -> Optional[str]:
        """Получает ID базы данных по имени"""
        return self.databases.get(name.lower())
    
    async def list_databases(self) -> Dict[str, str]:
        """Возвращает список всех доступных баз данных"""
        return self.databases.copy() 