"""
Конфигурация для Designer Report Bot
Настройки интеграции с Notion и Telegram
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class NotionConfig:
    """Конфигурация Notion"""
    token: str
    tasks_database_id: str = "d09df250ce7e4e0d9fbe4e036d320def"
    materials_database_id: str = "1d9ace03d9ff804191a4d35aeedcbbd4"
    projects_database_id: str = "342f18c67a5e41fead73dcec00770f4e"
    time_log_database_id: str = ""  # Будет создана автоматически

@dataclass
class TelegramConfig:
    """Конфигурация Telegram"""
    bot_token: str
    admin_user_ids: List[int] = None  # type: ignore
    
    def __post_init__(self):
        if self.admin_user_ids is None:
            self.admin_user_ids = []

@dataclass
class ReportConfig:
    """Конфигурация отчётов"""
    max_reports_per_day: int = 50
    max_time_per_report: float = 24.0  # часов
    auto_save_interval: int = 300  # секунд
    backup_enabled: bool = True

class DesignerBotConfig:
    """Основная конфигурация бота"""
    
    def __init__(self):
        self.notion = NotionConfig(
            token=os.getenv("NOTION_TOKEN", ""),
            tasks_database_id=os.getenv("NOTION_TASKS_DB_ID", "d09df250ce7e4e0d9fbe4e036d320def"),
            materials_database_id=os.getenv("NOTION_MATERIALS_DB_ID", "1d9ace03d9ff804191a4d35aeedcbbd4"),
            projects_database_id=os.getenv("NOTION_PROJECTS_DB_ID", "342f18c67a5e41fead73dcec00770f4e")
        )
        
        self.telegram = TelegramConfig(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            admin_user_ids=[int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.isdigit()]
        )
        
        self.reports = ReportConfig()
        
        # Шаблоны быстрых отчётов
        self.quick_report_patterns = [
            r'(.+?) - (.+?) (\d+(?:\.\d+)?)\s*(?:час|ч|часа|часов)',
            r'(.+?) (\d+(?:\.\d+)?)\s*(?:час|ч|часа|часов)',
            r'(.+?) - (\d+(?:\.\d+)?)\s*(?:час|ч|часа|часов)'
        ]
        
        # Статусы задач
        self.task_statuses = {
            "in_progress": "In Progress",
            "done": "Done", 
            "to_do": "To do",
            "backlog": "Backlog"
        }
        
        # Типы материалов
        self.material_types = {
            "figma": "Figma макет",
            "drive": "Google Drive файл",
            "yandex": "Яндекс.Диск файл",
            "image": "Изображение",
            "video": "Видео",
            "document": "Документ"
        }
    
    def validate(self) -> bool:
        """Проверить корректность конфигурации"""
        errors = []
        
        if not self.notion.token:
            errors.append("NOTION_TOKEN не установлен")
        
        if not self.telegram.bot_token:
            errors.append("TELEGRAM_BOT_TOKEN не установлен")
        
        if not self.notion.tasks_database_id:
            errors.append("NOTION_TASKS_DB_ID не установлен")
        
        if errors:
            print("❌ Ошибки конфигурации:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def get_database_schemas(self) -> Dict[str, Any]:
        """Получить схемы баз данных"""
        return {
            "tasks": {
                "id": self.notion.tasks_database_id,
                "properties": {
                    "Задача": "title",
                    "Статус": "status", 
                    "Участники": "people",
                    "Проект": "relation",
                    "Затрачено_минут": "number",
                    "Комментарии": "rich_text"
                }
            },
            "materials": {
                "id": self.notion.materials_database_id,
                "properties": {
                    "Name": "title",
                    "Описание": "rich_text",
                    "Статус": "status",
                    "Теги": "multi_select",
                    "URL": "url",
                    "Важность": "number"
                }
            },
            "projects": {
                "id": self.notion.projects_database_id,
                "properties": {
                    "Name": "title",
                    "Статус": "status",
                    "Участники": "people",
                    "Задачи": "relation"
                }
            }
        }

# Глобальный экземпляр конфигурации
config = DesignerBotConfig() 