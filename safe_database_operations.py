import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from notion_client import AsyncClient
from notion_database_schemas import get_database_schema, get_database_schema_by_id, get_select_options, get_select_options_by_id, get_multi_select_options, get_multi_select_options_by_id, get_database_id

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeDatabaseOperations:
    """Безопасные операции с базами данных Notion с автоматическим добавлением новых значений"""
    
    def __init__(self):
        self.client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.logger = logger
    
    # ==================== АВТОМАТИЧЕСКОЕ ДОБАВЛЕНИЕ ОПЦИЙ ====================
    
    async def add_select_option(self, database_id: str, property_name: str, new_option: str) -> Dict[str, Any]:
        """Добавить новое значение в select поле через Notion API"""
        try:
            self.logger.info(f"🔄 Добавление нового значения '{new_option}' в поле '{property_name}' базы {database_id}")
            
            # Получаем текущую схему базы
            response = await self.client.databases.retrieve(database_id=database_id)
            properties = response.get("properties", {})
            
            if property_name not in properties:
                return {"success": False, "error": f"Поле '{property_name}' не найдено в базе"}
            
            property_config = properties[property_name]
            if property_config.get("type") != "select":
                return {"success": False, "error": f"Поле '{property_name}' не является select полем"}
            
            # Получаем существующие опции
            current_options = property_config.get("select", {}).get("options", [])
            existing_names = [opt.get("name", "") for opt in current_options]
            
            if new_option in existing_names:
                return {"success": True, "message": f"Значение '{new_option}' уже существует в поле '{property_name}'"}
            
            # Добавляем новую опцию
            new_option_config = {
                "name": new_option,
                "color": "default"
            }
            
            updated_options = current_options + [new_option_config]
            
            # Обновляем схему базы
            update_response = await self.client.databases.update(
                database_id=database_id,
                properties={
                    property_name: {
                        "select": {
                            "options": updated_options
                        }
                    }
                }
            )
            
            self.logger.info(f"✅ Успешно добавлено значение '{new_option}' в поле '{property_name}'")
            return {
                "success": True, 
                "message": f"Добавлено значение '{new_option}' в поле '{property_name}'",
                "database_id": database_id,
                "property_name": property_name,
                "new_option": new_option
            }
            
        except Exception as e:
            error_msg = f"Ошибка добавления значения '{new_option}' в поле '{property_name}': {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def add_multi_select_option(self, database_id: str, property_name: str, new_option: str) -> Dict[str, Any]:
        """Добавить новое значение в multi_select поле через Notion API"""
        try:
            self.logger.info(f"🔄 Добавление нового значения '{new_option}' в multi_select поле '{property_name}' базы {database_id}")
            
            # Получаем текущую схему базы
            response = await self.client.databases.retrieve(database_id=database_id)
            properties = response.get("properties", {})
            
            if property_name not in properties:
                return {"success": False, "error": f"Поле '{property_name}' не найдено в базе"}
            
            property_config = properties[property_name]
            if property_config.get("type") != "multi_select":
                return {"success": False, "error": f"Поле '{property_name}' не является multi_select полем"}
            
            # Получаем существующие опции
            current_options = property_config.get("multi_select", {}).get("options", [])
            existing_names = [opt.get("name", "") for opt in current_options]
            
            if new_option in existing_names:
                return {"success": True, "message": f"Значение '{new_option}' уже существует в поле '{property_name}'"}
            
            # Добавляем новую опцию
            new_option_config = {
                "name": new_option,
                "color": "default"
            }
            
            updated_options = current_options + [new_option_config]
            
            # Обновляем схему базы
            update_response = await self.client.databases.update(
                database_id=database_id,
                properties={
                    property_name: {
                        "multi_select": {
                            "options": updated_options
                        }
                    }
                }
            )
            
            self.logger.info(f"✅ Успешно добавлено значение '{new_option}' в multi_select поле '{property_name}'")
            return {
                "success": True, 
                "message": f"Добавлено значение '{new_option}' в multi_select поле '{property_name}'",
                "database_id": database_id,
                "property_name": property_name,
                "new_option": new_option
            }
            
        except Exception as e:
            error_msg = f"Ошибка добавления значения '{new_option}' в multi_select поле '{property_name}': {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def ensure_select_option_exists(self, database_id: str, property_name: str, option: str) -> Dict[str, Any]:
        """Проверить и добавить значение в select поле, если его нет"""
        try:
            # Получаем текущие опции из схемы
            current_options = get_select_options_by_id(database_id, property_name)
            
            if option in current_options:
                return {"success": True, "message": f"Значение '{option}' уже существует в поле '{property_name}'"}
            
            # Добавляем новое значение
            return await self.add_select_option(database_id, property_name, option)
            
        except Exception as e:
            error_msg = f"Ошибка проверки/добавления значения '{option}' в select поле '{property_name}': {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def ensure_multi_select_option_exists(self, database_id: str, property_name: str, option: str) -> Dict[str, Any]:
        """Проверить и добавить значение в multi_select поле, если его нет"""
        try:
            # Получаем текущие опции из схемы
            current_options = get_multi_select_options_by_id(database_id, property_name)
            
            if option in current_options:
                return {"success": True, "message": f"Значение '{option}' уже существует в поле '{property_name}'"}
            
            # Добавляем новое значение
            return await self.add_multi_select_option(database_id, property_name, option)
            
        except Exception as e:
            error_msg = f"Ошибка проверки/добавления значения '{option}' в multi_select поле '{property_name}': {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def add_multiple_options(self, database_id: str, property_name: str, new_options: List[str], field_type: str = "select") -> Dict[str, Any]:
        """Добавить несколько новых значений в select или multi_select поле"""
        try:
            self.logger.info(f"🔄 Добавление {len(new_options)} новых значений в {field_type} поле '{property_name}' базы {database_id}")
            
            results = []
            for option in new_options:
                if field_type == "select":
                    result = await self.add_select_option(database_id, property_name, option)
                else:
                    result = await self.add_multi_select_option(database_id, property_name, option)
                results.append(result)
            
            successful = [r for r in results if r["success"]]
            failed = [r for r in results if not r["success"]]
            
            return {
                "success": len(failed) == 0,
                "message": f"Добавлено {len(successful)} из {len(new_options)} значений",
                "successful": successful,
                "failed": failed,
                "total": len(new_options)
            }
            
        except Exception as e:
            error_msg = f"Ошибка добавления множественных опций в {field_type} поле '{property_name}': {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    # ==================== БЕЗОПАСНЫЕ ОПЕРАЦИИ С ВАЛИДАЦИЕЙ ====================
    
    async def validate_payload(self, database_name: str, properties: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Валидация payload по схеме базы"""
        errors = []
        
        try:
            # Получаем схему базы
            schema = get_database_schema(database_name)
            if not schema:
                errors.append(f"Схема базы '{database_name}' не найдена")
                return False, errors
            
            schema_properties = schema.properties
            
            # Проверяем каждое поле
            for field_name, field_value in properties.items():
                if field_name not in schema_properties:
                    errors.append(f"Поле '{field_name}' не существует в схеме базы '{database_name}'")
                    continue
                
                field_schema = schema_properties[field_name]
                field_type = field_schema.get("type")
                
                # Валидация по типу поля
                if not self._validate_field_type(field_name, field_value, field_type, schema):
                    errors.append(f"Поле '{field_name}' имеет неверный тип данных")
                    continue
                
                # Валидация select/multi_select значений
                if field_type in ["select", "multi_select"]:
                    if not self._validate_select_values(field_name, field_value, schema):
                        errors.append(f"Поле '{field_name}' содержит недопустимые значения")
                        continue
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Ошибка валидации схемы: {e}")
            return False, errors
    
    def _validate_field_type(self, field_name: str, field_value: Any, field_type: Optional[str], schema: Any) -> bool:
        """Валидация типа поля"""
        try:
            if field_type == "title":
                return isinstance(field_value, dict) and "title" in field_value
            elif field_type == "rich_text":
                return isinstance(field_value, dict) and "rich_text" in field_value
            elif field_type == "number":
                return isinstance(field_value, dict) and "number" in field_value
            elif field_type == "select":
                return isinstance(field_value, dict) and "select" in field_value
            elif field_type == "multi_select":
                return isinstance(field_value, dict) and "multi_select" in field_value
            elif field_type == "date":
                return isinstance(field_value, dict) and "date" in field_value
            elif field_type == "checkbox":
                return isinstance(field_value, dict) and "checkbox" in field_value
            elif field_type == "url":
                return isinstance(field_value, dict) and "url" in field_value
            elif field_type == "email":
                return isinstance(field_value, dict) and "email" in field_value
            elif field_type == "phone_number":
                return isinstance(field_value, dict) and "phone_number" in field_value
            elif field_type == "relation":
                return isinstance(field_value, dict) and "relation" in field_value
            else:
                return True  # Неизвестный тип - пропускаем
                
        except Exception:
            return False
    
    def _validate_select_values(self, field_name: str, field_value: Any, schema: Any) -> bool:
        """Валидация значений select/multi_select"""
        try:
            schema_properties = schema.properties
            field_schema = schema_properties.get(field_name, {})
            
            if field_schema.get("type") == "select":
                select_options = schema.select_options.get(field_name, [])
                if field_value.get("select", {}).get("name") not in select_options:
                    return False
                    
            elif field_schema.get("type") == "multi_select":
                multi_select_options = schema.multi_select_options.get(field_name, [])
                field_values = field_value.get("multi_select", [])
                for value in field_values:
                    if value.get("name") not in multi_select_options:
                        return False
            
            return True
            
        except Exception:
            return False
    
    async def safe_create_page(self, database_name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Безопасное создание страницы с валидацией и post-check"""
        result = {
            "success": False,
            "page_id": None,
            "errors": [],
            "warnings": [],
            "validation_passed": False,
            "post_check_passed": False
        }
        
        try:
            # 1. Валидация payload
            self.logger.info(f"🔍 Валидация payload для базы '{database_name}'")
            validation_passed, validation_errors = await self.validate_payload(database_name, properties)
            result["validation_passed"] = validation_passed
            result["errors"].extend(validation_errors)
            
            if not validation_passed:
                self.logger.error(f"❌ Валидация не пройдена: {validation_errors}")
                return result
            
            # 2. Получение ID базы
            database_id = get_database_id(database_name)
            if not database_id:
                result["errors"].append(f"База '{database_name}' не найдена")
                return result
            
            # 3. Создание страницы
            self.logger.info(f"📝 Создание страницы в базе '{database_name}'")
            response = await self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            # 4. Извлечение ID созданной страницы
            page_id = response.get("id")
            result["page_id"] = page_id
            
            if not page_id:
                result["errors"].append("Не удалось получить ID созданной страницы")
                return result
            
            # 5. Post-check - проверяем что запись реально создана с нужными полями
            self.logger.info(f"🔍 Post-check для страницы {page_id}")
            post_check_passed, post_check_errors = await self._post_check_page(database_name, page_id, properties)
            result["post_check_passed"] = post_check_passed
            result["warnings"].extend(post_check_errors)
            
            if post_check_passed:
                self.logger.info(f"✅ Страница {page_id} успешно создана и проверена")
                result["success"] = True
            else:
                self.logger.warning(f"⚠️ Страница {page_id} создана, но post-check не пройден: {post_check_errors}")
                result["success"] = True  # Создана, но с предупреждениями
            
            return result
            
        except Exception as e:
            result["errors"].append(f"Исключение при создании страницы: {e}")
            self.logger.error(f"❌ Исключение при создании страницы: {e}")
            return result
    
    async def safe_create_page_with_auto_options(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Создать запись с автоматическим добавлением новых значений в select/multi_select поля"""
        try:
            self.logger.info(f"🔄 Создание записи в базе {database_id} с автоматическим добавлением опций")
            
            # Получаем схему базы
            schema = get_database_schema_by_id(database_id)
            if not schema:
                return {"success": False, "error": f"Схема для базы {database_id} не найдена"}
            
            # Проверяем и добавляем новые значения для select полей
            for property_name, property_value in properties.items():
                if property_name in schema.select_options:
                    if isinstance(property_value, dict) and "select" in property_value:
                        option_name = property_value["select"].get("name")
                        if option_name:
                            result = await self.ensure_select_option_exists(database_id, property_name, option_name)
                            if not result["success"]:
                                self.logger.warning(f"⚠️ Не удалось добавить опцию '{option_name}' в поле '{property_name}': {result['error']}")
                
                elif property_name in schema.multi_select_options:
                    if isinstance(property_value, dict) and "multi_select" in property_value:
                        options = property_value["multi_select"]
                        if isinstance(options, list):
                            for option in options:
                                if isinstance(option, dict) and "name" in option:
                                    option_name = option["name"]
                                    result = await self.ensure_multi_select_option_exists(database_id, property_name, option_name)
                                    if not result["success"]:
                                        self.logger.warning(f"⚠️ Не удалось добавить опцию '{option_name}' в multi_select поле '{property_name}': {result['error']}")
            
            # Создаем запись
            response = await self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            self.logger.info(f"✅ Успешно создана запись {response['id']} в базе {database_id}")
            return {
                "success": True,
                "message": "Запись создана с автоматическим добавлением опций",
                "page_id": response["id"],
                "database_id": database_id
            }
            
        except Exception as e:
            error_msg = f"Ошибка создания записи с автоматическим добавлением опций: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def _post_check_page(self, database_name: str, page_id: str, expected_properties: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Post-check: проверяем что запись реально создана с нужными полями"""
        errors = []
        
        try:
            # Получаем созданную страницу
            response = await self.client.pages.retrieve(page_id=page_id)
            actual_properties = response.get("properties", {})
            
            # Проверяем каждое ожидаемое поле
            for field_name, expected_value in expected_properties.items():
                if field_name not in actual_properties:
                    errors.append(f"Поле '{field_name}' отсутствует в созданной странице")
                    continue
                
                actual_value = actual_properties[field_name]
                
                # Проверяем что поле не пустое
                if self._is_field_empty(actual_value):
                    errors.append(f"Поле '{field_name}' пустое в созданной странице")
                    continue
                
                # Проверяем соответствие значений для критичных полей
                if field_name == "Name" and expected_value.get("title"):
                    expected_title = expected_value["title"][0]["text"]["content"]
                    actual_title = actual_value.get("title", [{}])[0].get("text", {}).get("content", "")
                    if expected_title != actual_title:
                        errors.append(f"Название не соответствует: ожидалось '{expected_title}', получено '{actual_title}'")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Ошибка post-check: {e}")
            return False, errors
    
    def _is_field_empty(self, field_value: Any) -> bool:
        """Проверка что поле пустое"""
        if not field_value:
            return True
        
        if isinstance(field_value, dict):
            if "title" in field_value:
                return not field_value["title"] or not field_value["title"][0].get("text", {}).get("content")
            elif "rich_text" in field_value:
                return not field_value["rich_text"] or not field_value["rich_text"][0].get("text", {}).get("content")
            elif "select" in field_value:
                return not field_value["select"]
            elif "multi_select" in field_value:
                return not field_value["multi_select"]
            elif "number" in field_value:
                return field_value["number"] is None
            elif "date" in field_value:
                return not field_value["date"]
        
        return False

# Глобальный экземпляр для использования в других модулях
safe_operations = SafeDatabaseOperations() 