"""
Сервис для обработки отчётов дизайнеров
Интеграция с Notion для автоматического обновления задач
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

from notion_client import Client
from config.designer_bot_config import config

logger = logging.getLogger(__name__)

@dataclass
class WorkReport:
    """Отчёт о работе дизайнера"""
    designer_name: str
    project_name: str
    task_name: str
    work_description: str
    time_spent_hours: float
    materials_added: List[str] = None
    links_added: List[str] = None
    comments: str = ""
    timestamp: str = None
    status_changed: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.materials_added is None:
            self.materials_added = []
        if self.links_added is None:
            self.links_added = []

class DesignerReportService:
    """Сервис для обработки отчётов дизайнеров"""
    
    def __init__(self):
        self.notion = Client(auth=config.notion.token)
        self.schemas = config.get_database_schemas()
    
    def parse_quick_report(self, text: str) -> Optional[WorkReport]:
        """Парсинг быстрого отчёта из текста"""
        for pattern in config.quick_report_patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) >= 3:
                    # Формат: "Проект - Задача - Описание Время"
                    project_task = groups[0].strip()
                    description = groups[1].strip()
                    time_spent = float(groups[2])
                elif len(groups) >= 2:
                    # Формат: "Проект Время" или "Проект - Время"
                    project_task = groups[0].strip()
                    time_spent = float(groups[1])
                    description = "Общая работа"
                else:
                    continue
                
                # Разделить проект и задачу
                project_parts = project_task.split()
                if len(project_parts) >= 2:
                    task = project_parts[-1]
                    project = ' '.join(project_parts[:-1])
                else:
                    project = project_task
                    task = "Общая работа"
                
                return WorkReport(
                    designer_name="",  # Будет установлено позже
                    project_name=project,
                    task_name=task,
                    work_description=description,
                    time_spent_hours=time_spent
                )
        
        return None
    
    def parse_report(self, text: str) -> Dict[str, Any]:
        """Парсинг отчета в универсальном формате для бота"""
        result = {
            'time_spent': 0,
            'description': '',
            'status': 'В процессе',
            'materials': [],
            'title': 'Отчет о работе'
        }
        
        # Извлекаем время
        time_patterns = [
            r'потратил\s+(\d+(?:\.\d+)?)\s*(?:час|часа|часов|ч)',
            r'работал\s+(\d+(?:\.\d+)?)\s*(?:час|часа|часов|ч)',
            r'(\d+(?:\.\d+)?)\s*(?:час|часа|часов|ч)',
            r'(\d+)\s*минут'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                time_value = float(match.group(1))
                if 'минут' in pattern:
                    time_value = time_value / 60  # Конвертируем минуты в часы
                result['time_spent'] = time_value
                break
        
        # Извлекаем описание
        # Убираем время из текста для получения описания
        clean_text = re.sub(r'потратил\s+\d+(?:\.\d+)?\s*(?:час|часа|часов|ч)', '', text, flags=re.IGNORECASE)
        clean_text = re.sub(r'работал\s+\d+(?:\.\d+)?\s*(?:час|часа|часов|ч)', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\d+(?:\.\d+)?\s*(?:час|часа|часов|ч)', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\d+\s*минут', '', clean_text, flags=re.IGNORECASE)
        
        # Убираем статус
        status_patterns = [
            r'статус:\s*(завершено|в процессе|проблемы|готово)',
            r'(завершено|в процессе|проблемы|готово)'
        ]
        
        for pattern in status_patterns:
            status_match = re.search(pattern, clean_text.lower())
            if status_match:
                result['status'] = status_match.group(1).title()
                clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
                break
        
        # Очищаем текст от лишних символов
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        if clean_text:
            result['description'] = clean_text
            result['title'] = clean_text[:50] + '...' if len(clean_text) > 50 else clean_text
        
        # Извлекаем материалы
        result['materials'] = self.extract_materials_from_text(text)
        
        return result
    
    def find_task_in_notion(self, task_name: str, project_name: str = "") -> Optional[Dict]:
        """Найти задачу в Notion"""
        try:
            filters = []
            
            # Фильтр по названию задачи
            filters.append({
                "property": "Задача",
                "title": {
                    "contains": task_name
                }
            })
            
            # Если указан проект, добавить фильтр по проекту
            if project_name:
                project_id = self.find_project_id(project_name)
                if project_id:
                    filters.append({
                        "property": "Проект",
                        "relation": {
                            "contains": project_id
                        }
                    })
            
            response = self.notion.databases.query(
                database_id=config.notion.tasks_database_id,
                filter={
                    "and": filters
                } if len(filters) > 1 else filters[0]
            )
            
            if response["results"]:
                return response["results"][0]
            
            return None
        
        except Exception as e:
            logger.error(f"Ошибка поиска задачи: {e}")
            return None
    
    def find_project_id(self, project_name: str) -> Optional[str]:
        """Найти ID проекта по названию"""
        try:
            response = self.notion.databases.query(
                database_id=config.notion.projects_database_id,
                filter={
                    "property": "Name",
                    "title": {
                        "contains": project_name
                    }
                }
            )
            
            if response["results"]:
                return response["results"][0]["id"]
            
            return None
        
        except Exception as e:
            logger.error(f"Ошибка поиска проекта: {e}")
            return None
    
    def update_task_in_notion(self, report: WorkReport) -> bool:
        """Обновить задачу в Notion"""
        try:
            task = self.find_task_in_notion(report.task_name, report.project_name)
            
            if not task:
                logger.warning(f"Задача не найдена: {report.task_name}")
                return False
            
            task_id = task["id"]
            current_properties = task["properties"]
            
            # Подготовить обновления
            updates = {}
            
            # Обновить затраченное время
            current_time = current_properties.get("Затрачено_минут", {}).get("number", 0)
            new_time = current_time + int(report.time_spent_hours * 60)
            
            updates["Затрачено_минут"] = {
                "number": new_time
            }
            
            # Добавить комментарий
            if report.work_description:
                current_comments = current_properties.get("Комментарии", {}).get("rich_text", [])
                
                new_comment = {
                    "text": {
                        "content": f"[{datetime.now().strftime('%H:%M')}] {report.designer_name}: {report.work_description}"
                    }
                }
                
                if report.materials_added:
                    new_comment["text"]["content"] += f"\n📎 Материалы: {', '.join(report.materials_added)}"
                
                if report.links_added:
                    new_comment["text"]["content"] += f"\n🔗 Ссылки: {', '.join(report.links_added)}"
                
                current_comments.append(new_comment)
                
                updates["Комментарии"] = {
                    "rich_text": current_comments
                }
            
            # Обновить статус если указан
            if report.status_changed:
                updates["Статус"] = {
                    "status": {
                        "name": report.status_changed
                    }
                }
            
            # Применить обновления
            self.notion.pages.update(
                page_id=task_id,
                properties=updates
            )
            
            logger.info(f"Обновлена задача: {report.task_name} (время: +{report.time_spent_hours}ч)")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка обновления задачи: {e}")
            return False
    
    def create_material_in_notion(self, report: WorkReport, file_url: str = "") -> bool:
        """Создать материал в Notion"""
        try:
            material_properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": f"{report.project_name} - {report.task_name}"
                            }
                        }
                    ]
                },
                "Описание": {
                    "rich_text": [
                        {
                            "text": {
                                "content": f"Материал от {report.designer_name}: {report.work_description}"
                            }
                        }
                    ]
                },
                "Статус": {
                    "status": {
                        "name": "В работе"
                    }
                },
                "Теги": {
                    "multi_select": [
                        {"name": "Дизайн"},
                        {"name": report.project_name}
                    ]
                }
            }
            
            if file_url:
                material_properties["URL"] = {
                    "url": file_url
                }
            
            self.notion.pages.create(
                parent={"database_id": config.notion.materials_database_id},
                properties=material_properties
            )
            
            logger.info(f"Создан материал: {report.project_name} - {report.task_name}")
            return True
        
        except Exception as e:
            logger.error(f"Ошибка создания материала: {e}")
            return False
    
    def get_daily_summary(self, designer_name: str, date: datetime = None) -> Dict[str, Any]:
        """Получить сводку за день"""
        if date is None:
            date = datetime.now()
        
        # Здесь можно добавить логику получения сводки из Notion
        # Пока возвращаем базовую структуру
        return {
            "designer": designer_name,
            "date": date.strftime("%Y-%m-%d"),
            "total_time": 0,
            "tasks_count": 0,
            "projects": []
        }
    
    def validate_report(self, report: WorkReport) -> Tuple[bool, str]:
        """Валидация отчёта"""
        errors = []
        
        if not report.designer_name:
            errors.append("Не указано имя дизайнера")
        
        if not report.project_name:
            errors.append("Не указан проект")
        
        if not report.task_name:
            errors.append("Не указана задача")
        
        if report.time_spent_hours <= 0:
            errors.append("Время должно быть больше 0")
        
        if report.time_spent_hours > config.reports.max_time_per_report:
            errors.append(f"Время превышает лимит ({config.reports.max_time_per_report}ч)")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, ""
    
    def extract_links_from_text(self, text: str) -> List[str]:
        """Извлечь ссылки из текста"""
        url_pattern = r'https?://[^\s]+'
        return re.findall(url_pattern, text)
    
    def extract_materials_from_text(self, text: str) -> List[str]:
        """Извлечь упоминания материалов из текста"""
        materials = []
        
        # Паттерны для разных типов материалов
        patterns = {
            "figma": r'figma\.com/file/[a-zA-Z0-9]+',
            "drive": r'drive\.google\.com/[^\s]+',
            "yandex": r'disk\.yandex\.ru/[^\s]+',
            "lightshot": r'prnt\.sc/[a-zA-Z0-9]+',  # LightShot ссылки
            "image": r'\.(jpg|jpeg|png|gif|svg)\b',
            "video": r'\.(mp4|avi|mov|mkv)\b'
        }
        
        for material_type, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                materials.append(material_type)
        
        return materials

    def process_lightshot_link(self, url: str) -> Dict[str, str]:
        """Особая обработка для LightShot ссылок"""
        try:
            # Извлекаем код из URL
            code = url.split('/')[-1]
            
            return {
                "preview": f"https://prnt.sc/thumb/{code}.jpg",
                "type": "screenshot",
                "original_url": url,
                "code": code
            }
        except Exception as e:
            logger.error(f"Ошибка обработки LightShot ссылки: {e}")
            return {"type": "screenshot", "original_url": url}
    
    def process_report(self, report: WorkReport) -> Tuple[bool, str]:
        """Обработать отчёт"""
        # Валидация
        is_valid, error_msg = self.validate_report(report)
        if not is_valid:
            return False, error_msg
        
        # Извлечь ссылки и материалы из описания
        if report.work_description:
            report.links_added = self.extract_links_from_text(report.work_description)
            report.materials_added = self.extract_materials_from_text(report.work_description)
        
        # Обновить задачу в Notion
        success = self.update_task_in_notion(report)
        
        if success:
            return True, "Отчёт успешно обработан"
        else:
            return False, "Ошибка обновления в Notion"
    
    def get_active_projects(self) -> List[str]:
        """Получить список активных проектов"""
        try:
            response = self.notion.databases.query(
                database_id=config.notion.projects_database_id,
                filter={
                    "property": "Статус",
                    "status": {
                        "does_not_equal": "Завершён"
                    }
                }
            )
            
            projects = []
            for page in response["results"]:
                name_prop = page["properties"].get("Name", {})
                if name_prop.get("title"):
                    projects.append(name_prop["title"][0]["plain_text"])
            
            return projects[:10]  # Максимум 10 проектов
        
        except Exception as e:
            logger.error(f"Ошибка получения проектов: {e}")
            return ["Коробки мультиварки RMP04", "Брендинг", "Дизайн сайта"]
    
    def get_tasks_for_project(self, project_name: str) -> List[str]:
        """Получить задачи для проекта"""
        try:
            project_id = self.find_project_id(project_name)
            if not project_id:
                return ["Общая работа"]
            
            response = self.notion.databases.query(
                database_id=config.notion.tasks_database_id,
                filter={
                    "property": "Проект",
                    "relation": {
                        "contains": project_id
                    }
                }
            )
            
            tasks = []
            for page in response["results"]:
                name_prop = page["properties"].get("Задача", {})
                if name_prop.get("title"):
                    tasks.append(name_prop["title"][0]["plain_text"])
            
            return tasks[:8] if tasks else ["Общая работа"]
        
        except Exception as e:
            logger.error(f"Ошибка получения задач: {e}")
            return ["Верстка", "Дизайн", "Брендинг", "Общая работа"]

# Глобальный экземпляр сервиса
service = DesignerReportService() 