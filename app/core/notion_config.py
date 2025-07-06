import os
from typing import Dict, List
from dotenv import load_dotenv
from src.config import settings

# Загружаем переменные окружения
load_dotenv()

# Все ID баз данных из переменных окружения
NOTION_DATABASES = {
    'tasks': os.getenv('NOTION_TASKS_DB_ID'),
    'subtasks': os.getenv('NOTION_SUBTASKS_DB_ID'),
    'projects': os.getenv('NOTION_PROJECTS_DB_ID'),
    'ideas': os.getenv('NOTION_IDEAS_DB_ID'),
    'materials': os.getenv('NOTION_MATERIALS_DB_ID'),
    'marketing_tasks': os.getenv('NOTION_MARKETING_TASKS_DB_ID'),
    'content_plan': os.getenv('NOTION_CONTENT_PLAN_DB_ID'),
    'platforms': os.getenv('NOTION_PLATFORMS_DB_ID'),
    'kpi': os.getenv('NOTION_KPI_DB_ID'),
    'teams': os.getenv('NOTION_TEAMS_DB_ID'),
    'learning': os.getenv('NOTION_LEARNING_DB_ID'),
    'guides': os.getenv('NOTION_GUIDES_DB_ID'),
    'super_guides': os.getenv('NOTION_SUPER_GUIDES_DB_ID'),
    'epics': os.getenv('NOTION_EPICS_DB_ID'),
    'concepts': os.getenv('NOTION_CONCEPTS_DB_ID'),
    'links': os.getenv('NOTION_LINKS_DB_ID'),
    'clients': os.getenv('NOTION_CLIENTS_DB_ID'),
    'competitors': os.getenv('NOTION_COMPETITORS_DB_ID'),
    'products': os.getenv('NOTION_PRODUCTS_DB_ID'),
    'rdt': os.getenv('NOTION_RDT_DB_ID'),
    'tasks_templates': os.getenv('NOTION_TASKS_TEMPLATES_DB_ID'),
}

# Маппинги полей для каждой базы
FIELD_MAPPINGS = {
    "tasks": {
        "title": "Задача",
        "assignees": "Участники",
        "status": "Статус",
        "project": "Проект",
        "subtasks": "Под задачи",
        "materials": "Материалы",
        "category": "Категория",
        "priority": "! Задачи",
        "due_date": "Дата",
        "description": "Описание",
        "crm_url": "CRM задачи",
        "reference": "Ориентир"
    },
    "subtasks": {
        "title": "Подзадачи",
        "assignee": "Исполнитель",
        "status": " Статус",
        "task": "Задачи",
        "direction": "Направление",
        "priority": "Приоритет",
        "due_date": "Дата",
        "description": "Описание",
        "hours": "Часы",
        "crm_url": "CRM"
    },
    "marketing_tasks": {
        "title": " Задача",
        "assignees": "Участники",
        "status": "Статус",
        "project": "Проект",
        "tags": " Теги",
        "priority": "! Задачи",
        "due_date": "Дата",
        "description": "Описание",
        "crm_url": "CRM задачи",
        "reference": "Ориентир",
        "feedback": "Отзыв ?",
        "comment": "Комент"
    },
    "content_plan": {
        "title": "Name",
        "status": "Статус",
        "platform": "Платформа",
        "publish_date": "Дата публикации",
        "description": "Описание"
    },
    "platforms": {
        "title": "Platform",
        "status": "Status",
        "responsible": "Responsible",
        "metrics": "Metrics"
    },
    "materials": {
        "title": "Name",
        "status": "Статус",
        "tags": "Теги",
        "weight": "Вес",
        "url": "URL",
        "date": "Date",
        "description": "Описание",
        "purpose": "Для чего?"
    },
    "ideas": {
        "title": "Name",
        "status": "Статус",
        "tags": "Теги",
        "weight": "Вес",
        "url": "URL",
        "date": "Date",
        "description": "Описание",
        "purpose": "Для чего?",
        "whats_good": "Что классно?"
    }
}

def get_database_id(db_name: str) -> str:
    """Получить ID базы данных по имени"""
    db_id = NOTION_DATABASES.get(db_name)
    if not db_id:
        raise ValueError(f"Database ID not found for: {db_name}")
    return db_id

def get_field_mapping(db_name: str) -> dict:
    """Получить маппинг полей для базы данных"""
    return FIELD_MAPPINGS.get(db_name, {})

def validate_required_databases():
    """Проверить наличие всех необходимых ID баз данных"""
    required_dbs = [
        'NOTION_TASKS_DB_ID',
        'NOTION_SUBTASKS_DB_ID',
        'NOTION_MATERIALS_DB_ID',
        'NOTION_IDEAS_DB_ID',
        'NOTION_MARKETING_TASKS_DB_ID',
        'NOTION_CONTENT_PLAN_DB_ID'
    ]
    
    missing_dbs = []
    for db_var in required_dbs:
        if not os.getenv(db_var):
            missing_dbs.append(db_var)
    
    if missing_dbs:
        raise ValueError(f"Missing required database IDs: {missing_dbs}")
    
    return True

# Настройки синхронизации
SYNC_SETTINGS = {
    "auto_sync_interval": 300,  # Интервал автосинхронизации в секундах (5 минут)
    "sync_on_startup": True,    # Синхронизировать при запуске
    "two_way_sync": True,       # Двусторонняя синхронизация
} 