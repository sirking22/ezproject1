"""
Система мониторинга изменений в базах данных Notion
Автоматическое обнаружение новых параметров, тегов, статусов
"""

import os
import json
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from notion_client import Client
from notion_database_schemas import get_database_schema, get_all_schemas

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SchemaChange:
    """Изменение в схеме базы данных"""
    database_name: str
    change_type: str  # 'new_property', 'new_status', 'new_select_option', 'new_multi_select_option'
    property_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class SchemaDiff:
    """Различия между схемами"""
    database_name: str
    added_properties: List[str] = None
    removed_properties: List[str] = None
    added_status_options: Dict[str, List[str]] = None
    removed_status_options: Dict[str, List[str]] = None
    added_select_options: Dict[str, List[str]] = None
    removed_select_options: Dict[str, List[str]] = None
    added_multi_select_options: Dict[str, List[str]] = None
    removed_multi_select_options: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.added_properties is None:
            self.added_properties = []
        if self.removed_properties is None:
            self.removed_properties = []
        if self.added_status_options is None:
            self.added_status_options = {}
        if self.removed_status_options is None:
            self.removed_status_options = {}
        if self.added_select_options is None:
            self.added_select_options = {}
        if self.removed_select_options is None:
            self.removed_select_options = {}
        if self.added_multi_select_options is None:
            self.added_multi_select_options = {}
        if self.removed_multi_select_options is None:
            self.removed_multi_select_options = {}

class NotionSchemaMonitor:
    """Монитор изменений в схемах баз данных Notion"""
    
    def __init__(self):
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.changes_file = "schema_changes.json"
        self.backup_file = "schema_backup.json"
        
    def get_current_schema_from_notion(self, database_id: str) -> Dict[str, Any]:
        """Получить текущую схему базы данных из Notion API"""
        try:
            database = self.notion.databases.retrieve(database_id=database_id)
            return database["properties"]
        except Exception as e:
            logger.error(f"Ошибка получения схемы для {database_id}: {e}")
            return {}
    
    def extract_schema_info(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечь информацию о схеме из свойств Notion"""
        schema_info = {
            "properties": {},
            "status_options": {},
            "select_options": {},
            "multi_select_options": {}
        }
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type", "unknown")
            schema_info["properties"][prop_name] = {"type": prop_type}
            
            # Извлечение статусов
            if prop_type == "status":
                status_options = prop_data.get("status", {}).get("options", [])
                schema_info["status_options"][prop_name] = [
                    option["name"] for option in status_options
                ]
            
            # Извлечение select опций
            elif prop_type == "select":
                select_options = prop_data.get("select", {}).get("options", [])
                schema_info["select_options"][prop_name] = [
                    option["name"] for option in select_options
                ]
            
            # Извлечение multi_select опций
            elif prop_type == "multi_select":
                multi_select_options = prop_data.get("multi_select", {}).get("options", [])
                schema_info["multi_select_options"][prop_name] = [
                    option["name"] for option in multi_select_options
                ]
        
        return schema_info
    
    def compare_schemas(self, current_schema: Dict[str, Any], stored_schema: Dict[str, Any]) -> SchemaDiff:
        """Сравнить текущую схему с сохранённой"""
        diff = SchemaDiff(database_name="unknown")
        
        # Сравнение свойств
        current_props = set(current_schema.get("properties", {}).keys())
        stored_props = set(stored_schema.get("properties", {}).keys())
        
        diff.added_properties = list(current_props - stored_props)
        diff.removed_properties = list(stored_props - current_props)
        
        # Сравнение статусов
        current_status = current_schema.get("status_options", {})
        stored_status = stored_schema.get("status_options", {})
        
        for prop_name in set(current_status.keys()) | set(stored_status.keys()):
            current_options = set(current_status.get(prop_name, []))
            stored_options = set(stored_status.get(prop_name, []))
            
            added = list(current_options - stored_options)
            removed = list(stored_options - current_options)
            
            if added:
                diff.added_status_options[prop_name] = added
            if removed:
                diff.removed_status_options[prop_name] = removed
        
        # Сравнение select опций
        current_select = current_schema.get("select_options", {})
        stored_select = stored_schema.get("select_options", {})
        
        for prop_name in set(current_select.keys()) | set(stored_select.keys()):
            current_options = set(current_select.get(prop_name, []))
            stored_options = set(stored_select.get(prop_name, []))
            
            added = list(current_options - stored_options)
            removed = list(stored_options - current_options)
            
            if added:
                diff.added_select_options[prop_name] = added
            if removed:
                diff.removed_select_options[prop_name] = removed
        
        # Сравнение multi_select опций
        current_multi = current_schema.get("multi_select_options", {})
        stored_multi = stored_schema.get("multi_select_options", {})
        
        for prop_name in set(current_multi.keys()) | set(stored_multi.keys()):
            current_options = set(current_multi.get(prop_name, []))
            stored_options = set(stored_multi.get(prop_name, []))
            
            added = list(current_options - stored_options)
            removed = list(stored_options - current_options)
            
            if added:
                diff.added_multi_select_options[prop_name] = added
            if removed:
                diff.removed_multi_select_options[prop_name] = removed
        
        return diff
    
    def detect_changes(self) -> List[SchemaChange]:
        """Обнаружить изменения во всех базах данных"""
        changes = []
        all_schemas = get_all_schemas()
        
        for db_name, schema in all_schemas.items():
            logger.info(f"Проверка изменений в {db_name}...")
            
            # Получить текущую схему из Notion
            current_properties = self.get_current_schema_from_notion(schema.database_id)
            current_schema = self.extract_schema_info(current_properties)
            
            # Сравнить с сохранённой схемой
            stored_schema = {
                "properties": schema.properties,
                "status_options": schema.status_options,
                "select_options": schema.select_options,
                "multi_select_options": schema.multi_select_options
            }
            
            diff = self.compare_schemas(current_schema, stored_schema)
            diff.database_name = db_name
            
            # Создать записи об изменениях
            for prop_name in diff.added_properties:
                changes.append(SchemaChange(
                    database_name=db_name,
                    change_type="new_property",
                    property_name=prop_name,
                    new_value=current_schema["properties"][prop_name]["type"]
                ))
            
            for prop_name, options in diff.added_status_options.items():
                for option in options:
                    changes.append(SchemaChange(
                        database_name=db_name,
                        change_type="new_status",
                        property_name=prop_name,
                        new_value=option
                    ))
            
            for prop_name, options in diff.added_select_options.items():
                for option in options:
                    changes.append(SchemaChange(
                        database_name=db_name,
                        change_type="new_select_option",
                        property_name=prop_name,
                        new_value=option
                    ))
            
            for prop_name, options in diff.added_multi_select_options.items():
                for option in options:
                    changes.append(SchemaChange(
                        database_name=db_name,
                        change_type="new_multi_select_option",
                        property_name=prop_name,
                        new_value=option
                    ))
        
        return changes
    
    def save_changes(self, changes: List[SchemaChange]):
        """Сохранить обнаруженные изменения"""
        changes_data = [asdict(change) for change in changes]
        
        # Загрузить существующие изменения
        existing_changes = []
        if os.path.exists(self.changes_file):
            with open(self.changes_file, "r", encoding="utf-8") as f:
                existing_changes = json.load(f)
        
        # Добавить новые изменения
        all_changes = existing_changes + changes_data
        
        # Сохранить
        with open(self.changes_file, "w", encoding="utf-8") as f:
            json.dump(all_changes, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Сохранено {len(changes)} изменений в {self.changes_file}")
    
    def generate_update_script(self, changes: List[SchemaChange]) -> str:
        """Сгенерировать скрипт для обновления схем"""
        script_lines = [
            "# Автоматически сгенерированный скрипт обновления схем",
            "# Запуск: python update_schemas.py",
            "",
            "from notion_database_schemas import DATABASE_SCHEMAS",
            "import json",
            "",
            "def update_schemas():",
            "    \"\"\"Обновить схемы на основе обнаруженных изменений\"\"\"",
            ""
        ]
        
        # Группировать изменения по базе данных
        changes_by_db = {}
        for change in changes:
            if change.database_name not in changes_by_db:
                changes_by_db[change.database_name] = []
            changes_by_db[change.database_name].append(change)
        
        for db_name, db_changes in changes_by_db.items():
            script_lines.append(f"    # Обновления для {db_name}")
            
            for change in db_changes:
                if change.change_type == "new_status":
                    script_lines.append(
                        f"    # Добавить статус '{change.new_value}' в поле '{change.property_name}'"
                    )
                elif change.change_type == "new_select_option":
                    script_lines.append(
                        f"    # Добавить опцию '{change.new_value}' в поле '{change.property_name}'"
                    )
                elif change.change_type == "new_multi_select_option":
                    script_lines.append(
                        f"    # Добавить тег '{change.new_value}' в поле '{change.property_name}'"
                    )
                elif change.change_type == "new_property":
                    script_lines.append(
                        f"    # Добавить свойство '{change.property_name}' типа '{change.new_value}'"
                    )
            
            script_lines.append("")
        
        script_lines.extend([
            "    # После обновления запустить:",
            "    # python test_schemas_integration.py",
            "    # python setup_ci.py check",
            "",
            "if __name__ == '__main__':",
            "    update_schemas()"
        ])
        
        return "\n".join(script_lines)
    
    def create_backup(self):
        """Создать резервную копию текущих схем"""
        all_schemas = get_all_schemas()
        backup_data = {}
        
        for db_name, schema in all_schemas.items():
            backup_data[db_name] = {
                "name": schema.name,
                "database_id": schema.database_id,
                "description": schema.description,
                "properties": schema.properties,
                "status_options": schema.status_options,
                "select_options": schema.select_options,
                "multi_select_options": schema.multi_select_options,
                "relations": schema.relations
            }
        
        with open(self.backup_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Резервная копия создана: {self.backup_file}")
    
    def run_monitoring(self) -> List[SchemaChange]:
        """Запустить мониторинг изменений"""
        logger.info("🔍 Запуск мониторинга изменений в схемах...")
        
        # Создать резервную копию
        self.create_backup()
        
        # Обнаружить изменения
        changes = self.detect_changes()
        
        if changes:
            logger.info(f"📝 Обнаружено {len(changes)} изменений:")
            for change in changes:
                logger.info(f"  - {change.database_name}: {change.change_type} - {change.property_name} = {change.new_value}")
            
            # Сохранить изменения
            self.save_changes(changes)
            
            # Сгенерировать скрипт обновления
            update_script = self.generate_update_script(changes)
            with open("update_schemas.py", "w", encoding="utf-8") as f:
                f.write(update_script)
            
            logger.info("✅ Скрипт обновления создан: update_schemas.py")
        else:
            logger.info("✅ Изменений не обнаружено")
        
        return changes

def main():
    """Главная функция"""
    monitor = NotionSchemaMonitor()
    changes = monitor.run_monitoring()
    
    if changes:
        print(f"\n🎯 Обнаружено {len(changes)} изменений:")
        print("1. Проверьте файл schema_changes.json")
        print("2. Изучите update_schemas.py")
        print("3. Обновите notion_database_schemas.py")
        print("4. Запустите тесты: python test_schemas_integration.py")
    else:
        print("\n✅ Все схемы актуальны")

if __name__ == "__main__":
    main() 