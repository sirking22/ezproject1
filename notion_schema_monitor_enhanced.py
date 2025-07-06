"""
Улучшенная система мониторинга изменений в базах данных Notion
С дополнительными гарантиями запуска и уведомлениями
"""

import os
import json
import logging
import smtplib
import requests
from typing import Dict, List, Set, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

from notion_client import Client
from notion_database_schemas import get_database_schema, get_all_schemas

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('schema_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringResult:
    """Результат мониторинга"""
    success: bool
    changes_detected: int
    errors: List[str]
    execution_time: float
    timestamp: str
    last_run_file: str = "last_monitoring_run.json"

class EnhancedNotionSchemaMonitor:
    """Улучшенный монитор изменений в схемах баз данных Notion"""
    
    def __init__(self):
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.changes_file = "schema_changes.json"
        self.backup_file = "schema_backup.json"
        self.status_file = "monitoring_status.json"
        self.last_run_file = "last_monitoring_run.json"
        
        # Настройки уведомлений
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.email_enabled = os.getenv("EMAIL_NOTIFICATIONS", "false").lower() == "true"
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    def log_execution_start(self):
        """Записать начало выполнения"""
        execution_data = {
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "attempts": self.get_attempt_count() + 1
        }
        
        with open(self.last_run_file, "w", encoding="utf-8") as f:
            json.dump(execution_data, f, indent=2)
        
        logger.info(f"🚀 Начало мониторинга (попытка #{execution_data['attempts']})")
    
    def log_execution_end(self, success: bool, changes: int, errors: List[str]):
        """Записать завершение выполнения"""
        execution_data = {
            "end_time": datetime.now().isoformat(),
            "status": "completed" if success else "failed",
            "changes_detected": changes,
            "errors": errors,
            "success": success
        }
        
        # Обновить существующий файл
        if os.path.exists(self.last_run_file):
            with open(self.last_run_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            execution_data.update(existing_data)
        
        with open(self.last_run_file, "w", encoding="utf-8") as f:
            json.dump(execution_data, f, indent=2)
        
        logger.info(f"✅ Мониторинг завершён: {'успешно' if success else 'с ошибками'}")
    
    def get_attempt_count(self) -> int:
        """Получить количество попыток запуска"""
        if os.path.exists(self.last_run_file):
            try:
                with open(self.last_run_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("attempts", 0)
            except:
                return 0
        return 0
    
    def check_last_run(self) -> Optional[Dict[str, Any]]:
        """Проверить последний запуск"""
        if os.path.exists(self.last_run_file):
            try:
                with open(self.last_run_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def should_run_monitoring(self) -> bool:
        """Определить, нужно ли запускать мониторинг"""
        last_run = self.check_last_run()
        
        if not last_run:
            logger.info("📝 Первый запуск мониторинга")
            return True
        
        # Проверить, не запускался ли уже сегодня
        if "end_time" in last_run:
            last_run_time = datetime.fromisoformat(last_run["end_time"])
            today = datetime.now().date()
            
            if last_run_time.date() == today:
                logger.info("📝 Мониторинг уже запускался сегодня")
                return False
        
        # Проверить количество неудачных попыток
        attempts = last_run.get("attempts", 0)
        if attempts > 5:
            logger.warning(f"⚠️ Слишком много попыток ({attempts}), пропускаем запуск")
            return False
        
        return True
    
    def send_notification(self, message: str, is_error: bool = False):
        """Отправить уведомление"""
        emoji = "🚨" if is_error else "📢"
        full_message = f"{emoji} {message}"
        
        # Slack уведомление
        if self.slack_webhook:
            try:
                payload = {"text": full_message}
                response = requests.post(self.slack_webhook, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info("✅ Slack уведомление отправлено")
                else:
                    logger.warning(f"⚠️ Ошибка отправки в Slack: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Ошибка Slack уведомления: {e}")
        
        # Telegram уведомление
        if self.telegram_bot_token and self.telegram_chat_id:
            try:
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                payload = {
                    "chat_id": self.telegram_chat_id,
                    "text": full_message,
                    "parse_mode": "HTML"
                }
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info("✅ Telegram уведомление отправлено")
                else:
                    logger.warning(f"⚠️ Ошибка отправки в Telegram: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Ошибка Telegram уведомления: {e}")
    
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
    
    def compare_schemas(self, current_schema: Dict[str, Any], stored_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Сравнить текущую схему с сохранённой"""
        diff = {
            "added_properties": [],
            "removed_properties": [],
            "added_status_options": {},
            "removed_status_options": {},
            "added_select_options": {},
            "removed_select_options": {},
            "added_multi_select_options": {},
            "removed_multi_select_options": {}
        }
        
        # Сравнение свойств
        current_props = set(current_schema.get("properties", {}).keys())
        stored_props = set(stored_schema.get("properties", {}).keys())
        
        diff["added_properties"] = list(current_props - stored_props)
        diff["removed_properties"] = list(stored_props - current_props)
        
        # Сравнение статусов
        current_status = current_schema.get("status_options", {})
        stored_status = stored_schema.get("status_options", {})
        
        for prop_name in set(current_status.keys()) | set(stored_status.keys()):
            current_options = set(current_status.get(prop_name, []))
            stored_options = set(stored_status.get(prop_name, []))
            
            added = list(current_options - stored_options)
            removed = list(stored_options - current_options)
            
            if added:
                diff["added_status_options"][prop_name] = added
            if removed:
                diff["removed_status_options"][prop_name] = removed
        
        # Сравнение select опций
        current_select = current_schema.get("select_options", {})
        stored_select = stored_schema.get("select_options", {})
        
        for prop_name in set(current_select.keys()) | set(stored_select.keys()):
            current_options = set(current_select.get(prop_name, []))
            stored_options = set(stored_select.get(prop_name, []))
            
            added = list(current_options - stored_options)
            removed = list(stored_options - current_options)
            
            if added:
                diff["added_select_options"][prop_name] = added
            if removed:
                diff["removed_select_options"][prop_name] = removed
        
        # Сравнение multi_select опций
        current_multi = current_schema.get("multi_select_options", {})
        stored_multi = stored_schema.get("multi_select_options", {})
        
        for prop_name in set(current_multi.keys()) | set(stored_multi.keys()):
            current_options = set(current_multi.get(prop_name, []))
            stored_options = set(stored_multi.get(prop_name, []))
            
            added = list(current_options - stored_options)
            removed = list(stored_options - current_options)
            
            if added:
                diff["added_multi_select_options"][prop_name] = added
            if removed:
                diff["removed_multi_select_options"][prop_name] = removed
        
        return diff
    
    def detect_changes(self) -> List[Dict[str, Any]]:
        """Обнаружить изменения во всех базах данных"""
        changes = []
        all_schemas = get_all_schemas()
        errors = []
        
        for db_name, schema in all_schemas.items():
            logger.info(f"Проверка изменений в {db_name}...")
            
            try:
                # Получить текущую схему из Notion
                current_properties = self.get_current_schema_from_notion(schema.database_id)
                if not current_properties:
                    errors.append(f"Не удалось получить схему для {db_name}")
                    continue
                
                current_schema = self.extract_schema_info(current_properties)
                
                # Сравнить с сохранённой схемой
                stored_schema = {
                    "properties": schema.properties,
                    "status_options": schema.status_options,
                    "select_options": schema.select_options,
                    "multi_select_options": schema.multi_select_options
                }
                
                diff = self.compare_schemas(current_schema, stored_schema)
                
                # Создать записи об изменениях
                for prop_name in diff["added_properties"]:
                    changes.append({
                        "database_name": db_name,
                        "change_type": "new_property",
                        "property_name": prop_name,
                        "new_value": current_schema["properties"][prop_name]["type"],
                        "timestamp": datetime.now().isoformat()
                    })
                
                for prop_name, options in diff["added_status_options"].items():
                    for option in options:
                        changes.append({
                            "database_name": db_name,
                            "change_type": "new_status",
                            "property_name": prop_name,
                            "new_value": option,
                            "timestamp": datetime.now().isoformat()
                        })
                
                for prop_name, options in diff["added_select_options"].items():
                    for option in options:
                        changes.append({
                            "database_name": db_name,
                            "change_type": "new_select_option",
                            "property_name": prop_name,
                            "new_value": option,
                            "timestamp": datetime.now().isoformat()
                        })
                
                for prop_name, options in diff["added_multi_select_options"].items():
                    for option in options:
                        changes.append({
                            "database_name": db_name,
                            "change_type": "new_multi_select_option",
                            "property_name": prop_name,
                            "new_value": option,
                            "timestamp": datetime.now().isoformat()
                        })
                
            except Exception as e:
                error_msg = f"Ошибка при проверке {db_name}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return changes, errors
    
    def save_changes(self, changes: List[Dict[str, Any]]):
        """Сохранить обнаруженные изменения"""
        changes_data = changes
        
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
    
    def run_enhanced_monitoring(self) -> MonitoringResult:
        """Запустить улучшенный мониторинг изменений"""
        start_time = datetime.now()
        errors = []
        
        try:
            # Проверить, нужно ли запускать
            if not self.should_run_monitoring():
                return MonitoringResult(
                    success=True,
                    changes_detected=0,
                    errors=["Мониторинг уже запускался сегодня"],
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    timestamp=datetime.now().isoformat()
                )
            
            # Записать начало выполнения
            self.log_execution_start()
            
            # Отправить уведомление о начале
            self.send_notification("🔄 Запуск мониторинга схем Notion")
            
            # Создать резервную копию
            self.create_backup()
            
            # Обнаружить изменения
            changes, detection_errors = self.detect_changes()
            errors.extend(detection_errors)
            
            if changes:
                logger.info(f"📝 Обнаружено {len(changes)} изменений:")
                for change in changes:
                    logger.info(f"  - {change['database_name']}: {change['change_type']} - {change['property_name']} = {change['new_value']}")
                
                # Сохранить изменения
                self.save_changes(changes)
                
                # Отправить уведомление об изменениях
                change_summary = ", ".join([f"{c['change_type']} в {c['database_name']}" for c in changes[:3]])
                if len(changes) > 3:
                    change_summary += f" и ещё {len(changes) - 3}"
                
                self.send_notification(f"📝 Обнаружено {len(changes)} изменений: {change_summary}")
                
            else:
                logger.info("✅ Изменений не обнаружено")
                self.send_notification("✅ Изменений в схемах не обнаружено")
            
            # Записать завершение
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_execution_end(True, len(changes), errors)
            
            return MonitoringResult(
                success=True,
                changes_detected=len(changes),
                errors=errors,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            error_msg = f"Критическая ошибка мониторинга: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
            
            # Отправить уведомление об ошибке
            self.send_notification(f"🚨 Ошибка мониторинга: {e}", is_error=True)
            
            # Записать завершение с ошибкой
            execution_time = (datetime.now() - start_time).total_seconds()
            self.log_execution_end(False, 0, errors)
            
            return MonitoringResult(
                success=False,
                changes_detected=0,
                errors=errors,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat()
            )

def main():
    """Главная функция"""
    print("🚀 УЛУЧШЕННЫЙ МОНИТОРИНГ СХЕМ NOTION")
    print("=" * 50)
    
    monitor = EnhancedNotionSchemaMonitor()
    result = monitor.run_enhanced_monitoring()
    
    print(f"\n📊 Результат мониторинга:")
    print(f"✅ Успех: {result.success}")
    print(f"📝 Изменений: {result.changes_detected}")
    print(f"⏱️ Время выполнения: {result.execution_time:.2f} сек")
    
    if result.errors:
        print(f"❌ Ошибки: {len(result.errors)}")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.changes_detected > 0:
        print(f"\n🎯 Обнаружено {result.changes_detected} изменений:")
        print("1. Проверьте файл schema_changes.json")
        print("2. Запустите: python auto_update_schemas.py")
        print("3. Проверьте тесты: python test_schemas_integration.py")
    else:
        print("\n✅ Все схемы актуальны")

if __name__ == "__main__":
    main() 