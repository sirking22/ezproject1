import logging
from typing import Optional, List, Dict, Any, Union
from notion_client import AsyncClient
from datetime import datetime, UTC
from .core import NotionClient
from ..core.config import Settings
from ..utils.notion_formatter import (
    create_title_property,
    create_rich_text_property,
    create_select_property,
    create_multi_select_property,
    create_date_property,
    create_number_property,
    create_checkbox_property,
    create_url_property,
    extract_title,
    extract_rich_text,
    extract_select,
    extract_multi_select,
    extract_date,
    extract_number,
    extract_checkbox,
    extract_url
)

logger = logging.getLogger(__name__)

class UniversalNotionRepository:
    """
    Универсальный репозиторий для всех 7 таблиц Notion
    Поддерживает CRUD операции для: rituals, habits, reflections, guides, actions, terms, materials
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = NotionClient(settings)
        
        # Алиасы для всех таблиц
        self.databases = {
            'rituals': settings.NOTION_RITUALS_DATABASE_ID,
            'habits': settings.NOTION_HABITS_DATABASE_ID,
            'reflections': settings.NOTION_REFLECTIONS_DATABASE_ID,
            'guides': settings.NOTION_GUIDES_DATABASE_ID,
            'actions': settings.NOTION_ACTIONS_DATABASE_ID,
            'terms': settings.NOTION_TERMS_DATABASE_ID,
            'materials': settings.NOTION_MATERIALS_DATABASE_ID,
        }
        
        # Схемы свойств для каждой таблицы
        self.schemas = {
            'rituals': {
                'title': 'title',
                'status': 'select',
                'category': 'select',
                'frequency': 'select',
                'description': 'rich_text',
                'tags': 'multi_select',
                'created_date': 'date',
                'last_performed': 'date',
                'streak': 'number',
                'priority': 'select'
            },
            'habits': {
                'title': 'title',
                'status': 'select',
                'category': 'select',
                'frequency': 'select',
                'description': 'rich_text',
                'tags': 'multi_select',
                'created_date': 'date',
                'last_performed': 'date',
                'streak': 'number',
                'target_frequency': 'number',
                'current_frequency': 'number'
            },
            'reflections': {
                'title': 'title',
                'type': 'select',
                'mood': 'select',
                'content': 'rich_text',
                'tags': 'multi_select',
                'created_date': 'date',
                'related_activities': 'multi_select',
                'insights': 'rich_text',
                'action_items': 'rich_text'
            },
            'guides': {
                'title': 'title',
                'category': 'select',
                'difficulty': 'select',
                'content': 'rich_text',
                'tags': 'multi_select',
                'created_date': 'date',
                'last_updated': 'date',
                'author': 'rich_text',
                'status': 'select',
                'url': 'url'
            },
            'actions': {
                'title': 'title',
                'status': 'select',
                'priority': 'select',
                'category': 'select',
                'description': 'rich_text',
                'tags': 'multi_select',
                'due_date': 'date',
                'created_date': 'date',
                'assigned_to': 'rich_text',
                'estimated_time': 'number',
                'actual_time': 'number'
            },
            'terms': {
                'title': 'title',
                'category': 'select',
                'definition': 'rich_text',
                'examples': 'rich_text',
                'tags': 'multi_select',
                'created_date': 'date',
                'last_reviewed': 'date',
                'mastery_level': 'select',
                'related_terms': 'multi_select'
            },
            'materials': {
                'title': 'title',
                'type': 'select',
                'category': 'select',
                'description': 'rich_text',
                'tags': 'multi_select',
                'url': 'url',
                'created_date': 'date',
                'last_accessed': 'date',
                'status': 'select',
                'rating': 'number',
                'notes': 'rich_text'
            }
        }

    async def validate_database(self, table_name: str) -> tuple[bool, str]:
        """Проверка структуры базы данных"""
        try:
            database_id = self.databases.get(table_name)
            if not database_id:
                return False, f"Unknown table: {table_name}"
            
            database = await self.client.databases.retrieve(database_id=database_id)
            schema = self.schemas.get(table_name, {})
            
            missing_properties = []
            wrong_type_properties = []
            
            for prop_name, prop_type in schema.items():
                if prop_name not in database["properties"]:
                    missing_properties.append(prop_name)
                elif database["properties"][prop_name]["type"] != prop_type:
                    wrong_type_properties.append(f"{prop_name} (expected {prop_type}, got {database['properties'][prop_name]['type']})")
            
            if missing_properties or wrong_type_properties:
                error_msg = f"Database validation failed for {table_name}:\n"
                if missing_properties:
                    error_msg += f"Missing properties: {', '.join(missing_properties)}\n"
                if wrong_type_properties:
                    error_msg += f"Wrong property types: {', '.join(wrong_type_properties)}"
                return False, error_msg
            
            return True, "Database structure is valid"
            
        except Exception as e:
            return False, f"Failed to validate database {table_name}: {str(e)}"

    async def create_item(self, table_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создание элемента в указанной таблице"""
        try:
            database_id = self.databases.get(table_name)
            if not database_id:
                raise ValueError(f"Unknown table: {table_name}")
            
            properties = self._convert_to_notion_properties(table_name, data)
            
            response = await self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            return self._convert_from_notion(table_name, response)
            
        except Exception as e:
            logger.error(f"Error creating item in {table_name}: {str(e)}")
            return None

    async def get_item(self, table_name: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Получение элемента по ID"""
        try:
            page = await self.client.pages.retrieve(page_id=item_id)
            return self._convert_from_notion(table_name, page)
        except Exception as e:
            logger.error(f"Error getting item {item_id} from {table_name}: {str(e)}")
            return None

    async def update_item(self, table_name: str, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновление элемента"""
        try:
            properties = self._convert_to_notion_properties(table_name, data)
            
            response = await self.client.pages.update(
                page_id=item_id,
                properties=properties
            )
            
            return self._convert_from_notion(table_name, response)
            
        except Exception as e:
            logger.error(f"Error updating item {item_id} in {table_name}: {str(e)}")
            return None

    async def delete_item(self, table_name: str, item_id: str) -> bool:
        """Удаление элемента (архивирование в Notion)"""
        try:
            await self.client.pages.update(
                page_id=item_id,
                archived=True
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting item {item_id} from {table_name}: {str(e)}")
            return False

    async def list_items(
        self, 
        table_name: str, 
        filters: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Список элементов с фильтрацией и сортировкой"""
        try:
            database_id = self.databases.get(table_name)
            if not database_id:
                return []
            
            query = {
                "database_id": database_id,
                "page_size": limit,
                "sorts": sorts or [],
                "filter": self._build_filter(table_name, filters) if filters else {}
            }
            
            response = await self.client.databases.query(**query)
            return [self._convert_from_notion(table_name, page) for page in response["results"]]
            
        except Exception as e:
            logger.error(f"Error listing items from {table_name}: {str(e)}")
            return []

    async def search_items(
        self, 
        table_name: str, 
        query: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Поиск элементов по тексту"""
        try:
            database_id = self.databases.get(table_name)
            if not database_id:
                return []
            
            response = await self.client.search(
                query=query,
                filter={"property": "object", "value": "page"},
                sort={"direction": "descending", "timestamp": "last_edited_time"},
                page_size=limit
            )
            
            # Фильтруем только страницы из нужной базы данных
            filtered_results = []
            for page in response["results"]:
                if page.get("parent", {}).get("database_id") == database_id:
                    filtered_results.append(self._convert_from_notion(table_name, page))
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error searching items in {table_name}: {str(e)}")
            return []

    def _convert_to_notion_properties(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация данных в свойства Notion"""
        schema = self.schemas.get(table_name, {})
        properties = {}
        
        for field, value in data.items():
            if field not in schema:
                continue
                
            prop_type = schema[field]
            
            if prop_type == "title" and value:
                properties[field] = create_title_property(value)
            elif prop_type == "rich_text" and value:
                properties[field] = create_rich_text_property(value)
            elif prop_type == "select" and value:
                properties[field] = create_select_property(value)
            elif prop_type == "multi_select" and value:
                properties[field] = create_multi_select_property(value)
            elif prop_type == "date" and value:
                properties[field] = create_date_property(value)
            elif prop_type == "number" and value is not None:
                properties[field] = create_number_property(value)
            elif prop_type == "checkbox" and value is not None:
                properties[field] = create_checkbox_property(value)
            elif prop_type == "url" and value:
                properties[field] = create_url_property(value)
        
        return properties

    def _convert_from_notion(self, table_name: str, page: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация страницы Notion в словарь"""
        schema = self.schemas.get(table_name, {})
        result = {
            "id": page["id"],
            "created_time": page["created_time"],
            "last_edited_time": page["last_edited_time"],
            "archived": page.get("archived", False)
        }
        
        properties = page.get("properties", {})
        
        for field, prop_type in schema.items():
            if field in properties:
                prop = properties[field]
                
                if prop_type == "title":
                    result[field] = extract_title(prop)
                elif prop_type == "rich_text":
                    result[field] = extract_rich_text(prop)
                elif prop_type == "select":
                    result[field] = extract_select(prop)
                elif prop_type == "multi_select":
                    result[field] = extract_multi_select(prop)
                elif prop_type == "date":
                    result[field] = extract_date(prop)
                elif prop_type == "number":
                    result[field] = extract_number(prop)
                elif prop_type == "checkbox":
                    result[field] = extract_checkbox(prop)
                elif prop_type == "url":
                    result[field] = extract_url(prop)
        
        return result

    def _build_filter(self, table_name: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Построение фильтра для запроса"""
        schema = self.schemas.get(table_name, {})
        notion_filters = []
        
        for field, value in filters.items():
            if field not in schema:
                continue
                
            prop_type = schema[field]
            
            if prop_type == "select":
                if isinstance(value, dict):
                    if "equals" in value:
                        notion_filters.append({
                            "property": field,
                            "select": {"equals": value["equals"]}
                        })
                    elif "not_equals" in value:
                        notion_filters.append({
                            "property": field,
                            "select": {"does_not_equal": value["not_equals"]}
                        })
                else:
                    notion_filters.append({
                        "property": field,
                        "select": {"equals": value}
                    })
            
            elif prop_type == "multi_select":
                if isinstance(value, list):
                    for item in value:
                        notion_filters.append({
                            "property": field,
                            "multi_select": {"contains": item}
                        })
            
            elif prop_type == "date":
                if isinstance(value, dict):
                    notion_filters.append({
                        "property": field,
                        "date": value
                    })
            
            elif prop_type == "number":
                if isinstance(value, dict):
                    notion_filters.append({
                        "property": field,
                        "number": value
                    })
        
        if len(notion_filters) == 1:
            return notion_filters[0]
        elif len(notion_filters) > 1:
            return {"and": notion_filters}
        else:
            return {}

    # Алиасы для удобства использования
    async def create_ritual(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.create_item('rituals', data)
    
    async def create_habit(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.create_item('habits', data)
    
    async def create_reflection(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.create_item('reflections', data)
    
    async def create_guide(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.create_item('guides', data)
    
    async def create_action(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.create_item('actions', data)
    
    async def create_term(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.create_item('terms', data)
    
    async def create_material(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.create_item('materials', data)

    async def get_rituals(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return await self.list_items('rituals', filters)
    
    async def get_habits(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return await self.list_items('habits', filters)
    
    async def get_reflections(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return await self.list_items('reflections', filters)
    
    async def get_guides(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return await self.list_items('guides', filters)
    
    async def get_actions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return await self.list_items('actions', filters)
    
    async def get_terms(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return await self.list_items('terms', filters)
    
    async def get_materials(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return await self.list_items('materials', filters) 