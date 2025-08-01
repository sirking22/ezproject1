"""
Централизованные схемы всех баз данных Notion
Единственный источник истины для всех параметров, статусов, тегов и связей
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class DatabaseSchema:
    """Схема базы данных Notion"""
    name: str
    database_id: str
    description: str
    properties: Dict[str, Dict[str, Any]]
    status_options: Dict[str, List[str]]
    select_options: Dict[str, List[str]]
    multi_select_options: Dict[str, List[str]]
    relations: Dict[str, str]  # property_name -> target_database_id

# Загружаем переменные окружения
load_dotenv()

# Схемы всех баз данных с реальными ID из .env
DATABASE_SCHEMAS = {
    "tasks": DatabaseSchema(
        name="Задачи дизайн-отдела",
        database_id=os.getenv("NOTION_TASKS_DB_ID", ""),
        description="Основные задачи дизайнеров с участниками, статусами и связями",
        properties={
            "Задача": {"type": "title"},
            "Участники": {"type": "people"},
            "Статус": {"type": "status"},
            "Проект": {"type": "relation"},
            "Под задачи": {"type": "relation"},
            "Материалы": {"type": "relation"},
            "Категория": {"type": "multi_select"},
            "Ориентир": {"type": "number"},  # Примерное время на задачу (ОСНОВНОЕ ПОЛЕ ВРЕМЕНИ)
            "Сложность": {"type": "select"},  # Поле сложности (НАЙДЕНО!)
            "Часы": {"type": "formula"},  # Formula поле, НЕ использовать в формулах
            "Число правок": {"type": "number"},
            "Оценка": {"type": "number"},
            "CRM задачи": {"type": "url"},
            "Описание": {"type": "rich_text"},
            "Дата": {"type": "date"},
            "! Задачи": {"type": "multi_select"},
            "KPI": {"type": "relation"},
            "Время за день": {"type": "formula"},
            "Время за неделю": {"type": "formula"},
            "За месяц": {"type": "formula"},
            "Среднее время": {"type": "formula"},
            "Отклонение": {"type": "formula"},
            "Отклонение Raw %": {"type": "formula"},
            "Is Blocking": {"type": "relation"},
            "Blocked By": {"type": "relation"},
            "Created time": {"type": "created_time"},
            "Last edited timeы": {"type": "last_edited_time"},
            # НОВЫЕ ПОЛЯ НАЙДЕННЫЕ ИНСТРУМЕНТОМ:
            "Ф задачи": {"type": "url"},
            "Сроки": {"type": "formula"},
            "Типовые задачи": {"type": "relation"},  # ВАЖНО для формул!
            "Отчеты": {"type": "relation"},
            "Срок проекта": {"type": "rollup"},
            "Статус проекта": {"type": "rollup"},
            "Саша за неделю": {"type": "formula"},
            "Арс за неделю": {"type": "formula"},
            "CRM проекта": {"type": "rollup"},
            "Эпик проекта": {"type": "rollup"},
            "Ф проекта": {"type": "rollup"},
            "📬 Гайды": {"type": "relation"},
            "Вика за месяц": {"type": "formula"},
            "Гайды/Концепты": {"type": "rollup"},
            "Чек листы": {"type": "relation"},
            "! Проекта": {"type": "rollup"},
            "Вика за неделю": {"type": "formula"},
            "Маша за месяц": {"type": "formula"},
            "Маша за неделю": {"type": "formula"},
            "Саша за месяц": {"type": "formula"},
            "Отзыв ": {"type": "rich_text"},
            "Арс за месяц": {"type": "formula"},
            "Концепты/Сценарии": {"type": "relation"},
            "Аня за неделю": {"type": "formula"},
            "Аня за месяц": {"type": "formula"},
            "Комент": {"type": "rich_text"},
            "Участник (стата)": {"type": "relation"},
        },
        status_options={
            "Статус": ["Regular", "Backlog", "To do", "Paused", "Review", "In Progress", "Done out date", "Done", "In Production", "Canceled"]
        },
        select_options={
            "Сложность": ["Простая", "Средняя", "Высокая"],  # АКТУАЛЬНЫЕ ОПЦИИ ПОДТВЕРЖДЕНЫ
        },
        multi_select_options={
            "Категория": ["Полиграфия", "Маркет", "Видео", "Активности", "Веб", "Бренд", "Копирайт", "SMM", "Фото", "Дизайн", "Стратегия", "Орг", "Материалы", "Аналитика", "Полиграфия товаров"],  # АКТУАЛЬНЫЕ ИЗ NOTION
            "! Задачи": ["!!!", "!!", "!", ".", "тест"]
        },
        relations={
            "Проект": "342f18c67a5e41fead73dcec00770f4e",
            "Под задачи": "9c5f4269d61449b6a7485579a3c21da3",
            "Материалы": "1d9ace03d9ff804191a4d35aeedcbbd4",
            "KPI": "1d6ace03d9ff80bfb809ed21dfd2150c",
            "Типовые задачи": "195ace03d9ff80c1a1b0d236ec3564d2",  # НОВАЯ СВЯЗЬ
        }
    ),
    
    "subtasks": DatabaseSchema(
        name="Подзадачи/чек-листы",
        database_id=os.getenv("NOTION_SUBTASKS_DB_ID", ""),
        description="Чек-листы внутри задач",
        properties={
            "Подзадачи": {"type": "title"},
            "Исполнитель": {"type": "people"},
            " Статус": {"type": "status"},
            "Задачи": {"type": "relation"},
            "Материалы": {"type": "relation"},
            "Направление": {"type": "multi_select"},
            "Приоритет": {"type": "select"},
            "Дата": {"type": "date"},
            "Описание": {"type": "rich_text"},
            "Часы": {"type": "number"},
            "CRM": {"type": "url"},
        },
        status_options={
            " Статус": ["needs review", "in progress", "complete", "To do", "In progress"]
        },
        select_options={
            "Приоритет": ["!!!", "!!", "!", ".", ">>", ">", "Средний"]
        },
        multi_select_options={
            "Направление": ["Продукт", "Бренд", "Маркет", "Соц сети", "Видео", "Фото", "Дизайн", "Веб", "Стратегия", "Аналитика", "Копирайт", "Орг"]
        },
        relations={
            "Задачи": os.getenv("NOTION_TASKS_DB_ID", ""),
            "Материалы": os.getenv("NOTION_MATERIALS_DB_ID", "")
        }
    ),
    
    "projects": DatabaseSchema(
        name="Управление проектами",
        database_id=os.getenv("NOTION_PROJECTS_DB_ID", ""),
        description="Основные проекты компании",
        properties={
            " Проект": {"type": "title"},
            "Участники": {"type": "people"},
            "Статус": {"type": "status"},
            "Эпик": {"type": "relation"},
            "Дизайн": {"type": "relation"},
            "СММ": {"type": "relation"},
            "Маркет": {"type": "relation"},
            " Теги": {"type": "multi_select"},
            "Приоритет": {"type": "select"},
            "Дата": {"type": "date"},
            "CRM": {"type": "url"},
            "Описание": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Regular", "Backlog", "Paused", "Planning", "In Progress", "Review", "In Production", "Done", "Canceled", "Archived"]
        },
        select_options={
            "Приоритет": ["!!!", "!!", "!", "."]
        },
        multi_select_options={
            " Теги": ["Полиграфия товаров", "Полиграфия", "Маркет", "Бренд", "Веб", "SMM", "Видео", "Фото", "Орг", "Активности", "Копирайт", "Дизайн", "Стратегия", "Материалы"]
        },
        relations={
            "Эпик": os.getenv("NOTION_EPICS_DB_ID", ""),
            "Дизайн": os.getenv("NOTION_TASKS_DB_ID", ""),
            "СММ": os.getenv("NOTION_SMM_TASKS_DB_ID", ""),
            "Маркет": os.getenv("NOTION_MARKETING_TASKS_DB_ID", "")
        }
    ),
    
    "ideas": DatabaseSchema(
        name="Идеи и концепции",
        database_id=os.getenv("NOTION_IDEAS_DB_ID", ""),
        description="Хранение идей и концепций",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Теги": {"type": "multi_select"},
            "Вес": {"type": "number"},
            "URL": {"type": "url"},
            "Date": {"type": "date"},
            "Описание": {"type": "rich_text"},
            "Для чего?": {"type": "rich_text"},
            "Что классно?": {"type": "multi_select"},
        },
        status_options={
            "Статус": ["Backlog", "To do", "In progress", "+\\-", "К релизу", "Ок", "Сторонние", "Архив"]
        },
        select_options={},
        multi_select_options={
            "Теги": ["Продукт", "Маркет", "Бренд", "Дизайн", "Веб", "Фото", "Видео", "Стратегия", "СММ", "Копирайт"],
            "Что классно?": ["Цвета", "Свет", "Композиция", "Динамика", "Живость", "Эмоции", "Идея", "Информат", "Формат", "Сценарий", "Графика", "Монтаж", "Функционал", "тест"]
        },
        relations={}
    ),
    
    "materials": DatabaseSchema(
        name="Файлы и ресурсы",
        database_id=os.getenv("NOTION_MATERIALS_DB_ID", ""),
        description="Хранение материалов и ресурсов",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Теги": {"type": "multi_select"},
            "Вес": {"type": "number"},
            "URL": {"type": "url"},
            "Date": {"type": "date"},
            "Описание": {"type": "rich_text"},
            "Для чего?": {"type": "rich_text"},
            "Files & media": {"type": "files"},
        },
        status_options={
            "Статус": ["Backlog", "To do", "In progress", "+\\-", "К релизу", "Ок", "Сторонние", "Архив"]
        },
        select_options={},
        multi_select_options={
            "Теги": ["Продукт", "Маркет", "Бренд", "Дизайн", "Веб", "Фото", "Видео", "Стратегия", "СММ", "Копирайт"]
        },
        relations={}
    ),
    
    "marketing_tasks": DatabaseSchema(
        name="Маркетинговые задачи",
        database_id=os.getenv("NOTION_MARKETING_TASKS_DB_ID", ""),
        description="Задачи маркетингового отдела",
        properties={
            " Задача": {"type": "title"},
            "Участники": {"type": "people"},
            "Статус": {"type": "status"},
            "Проект": {"type": "relation"},
            " Теги": {"type": "multi_select"},
            "! Задачи": {"type": "select"},
            "Дата": {"type": "date"},
            "Ориентир": {"type": "number"},
            "CRM задачи": {"type": "url"},
            "Описание": {"type": "rich_text"},
            "Отзыв ?": {"type": "rich_text"},
            "Комент": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Regular", "Backlog", "To do", "Paused", "Review", "In Progress", "In Production", "Done", "Canceled"]
        },
        select_options={
            "! Задачи": ["!!!", "!!", "!"]
        },
        multi_select_options={
            " Теги": ["Продукт", "Маркет", "Видео", "Активности", "Веб", "Бренд", "Копирайт", "SMM", "Фото", "Дизайн", "Стратегия", "Орг", "Материалы", "Аналитика", "KPI", "Дашборд", "Отчет", "Производительность", "AI", "Анализ", "Автоматизация", "Оптимизация", "Категоризация", "Сводный отчет", "Системы"]
        },
        relations={
            "Проект": os.getenv("NOTION_PROJECTS_DB_ID", "")
        }
    ),
    
    "platforms": DatabaseSchema(
        name="Платформы соцсетей",
        database_id=os.getenv("NOTION_PLATFORMS_DB_ID", ""),
        description="Информация о платформах",
        properties={
            "Platform": {"type": "title"},
            "Status": {"type": "status"},
            "Responsible": {"type": "people"},
            "Metrics": {"type": "rich_text"},
        },
        status_options={
            "Status": ["Active", "Inactive", "Testing", "Archived"]
        },
        select_options={},
        multi_select_options={},
        relations={}
    ),
    
    "smm_tasks": DatabaseSchema(
        name="SMM задачи",
        database_id=os.getenv("NOTION_SMM_TASKS_DB_ID", ""),
        description="Задачи SMM отдела",
        properties={
            " Задача": {"type": "title"},
            "Участники": {"type": "people"},
            "Статус": {"type": "status"},
            "Проект": {"type": "relation"},
            " Теги": {"type": "multi_select"},
            "! Задачи": {"type": "select"},
            "Дата": {"type": "date"},
            "Ориентир": {"type": "number"},
            "CRM задачи": {"type": "url"},
            "Описание": {"type": "rich_text"},
            "Отзыв ?": {"type": "rich_text"},
            "Комент": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Regular", "Backlog", "To do", "Paused", "Review", "In Progress", "In Production", "Done", "Canceled"]
        },
        select_options={
            "! Задачи": ["!!!", "!!", "!"]
        },
        multi_select_options={
            " Теги": ["Полиграфия товаров", "Полиграфия", "Маркет", "Бренд", "Веб", "SMM", "Видео", "Фото", "Орг", "Активности", "Копирайт", "Дизайн", "Стратегия", "Материалы"]
        },
        relations={
            "Проект": os.getenv("NOTION_PROJECTS_DB_ID", "")
        }
    ),
    
    "kpi": DatabaseSchema(
        name="KPI",
        database_id=os.getenv("NOTION_KPI_DB_ID", ""),
        description="Система KPI и метрик",
        properties={
            "Name": {"type": "title"},
            "Тип контента / направление": {"type": "select"},
            "Тип KPI": {"type": "select"},
            "Цель / задача": {"type": "number"},
            "Факт (результат)": {"type": "number"},
            "Достижение (%)": {"type": "number"},
            "Период": {"type": "select"},
            "Команда": {"type": "multi_select"},
            "Сотрудники": {"type": "people"},
            "Дата периода": {"type": "date"},
            "Комментарий": {"type": "rich_text"},
            "Время выполнения": {"type": "number"},
            "Охват": {"type": "number"},
            "Вовлечённость": {"type": "number"},
            "Конверсия": {"type": "number"},
            "CTR": {"type": "number"},
            "ROI": {"type": "number"},
            "Стартовое значение": {"type": "number"},
            "Значение по умолчанию": {"type": "number"},
            "%": {"type": "number"},
            "Формула расчёта": {"type": "rich_text"},
            "Контент план": {"type": "relation"},
            "Задачи сотрудника": {"type": "relation"},
            "Задачи полиграфии": {"type": "relation"},
            "Задачи SMM": {"type": "relation"},
            "Задачи маркетинг": {"type": "relation"},
            "Материалы": {"type": "relation"},
            "Дизайн": {"type": "relation"},
            "📬 Гайды": {"type": "relation"},
            "1 правок": {"type": "relation"},
        },
        status_options={},
        select_options={
            "Тип контента / направление": ["YouTube", "Instagram", "Telegram", "Полиграфия", "Веб", "Видео", "Фото", "SMM", "Маркетинг"],
            "Тип KPI": ["Просмотры", "Подписчики", "Лайки", "Комментарии", "Репосты", "Конверсия", "Продажи", "Охват", "Вовлечённость", "CTR", "ROI"],
            "Период": ["День", "Неделя", "Месяц", "Квартал", "Год"]
        },
        multi_select_options={
            "Команда": ["Дизайн", "SMM", "Маркетинг", "Полиграфия", "Веб", "Видео", "Фото", "Аналитика"]
        },
        relations={
            "Контент план": os.getenv("NOTION_CONTENT_PLAN_DB_ID", ""),
            "Задачи сотрудника": os.getenv("NOTION_TASKS_DB_ID", ""),
            "Задачи полиграфии": os.getenv("NOTION_TASKS_DB_ID", ""),
            "Задачи SMM": os.getenv("NOTION_SMM_TASKS_DB_ID", ""),
            "Задачи маркетинг": os.getenv("NOTION_MARKETING_TASKS_DB_ID", ""),
            "Материалы": os.getenv("NOTION_MATERIALS_DB_ID", ""),
            "Дизайн": os.getenv("NOTION_TASKS_DB_ID", ""),
            "📬 Гайды": os.getenv("NOTION_GUIDES_DB_ID", ""),
            "1 правок": os.getenv("NOTION_SUBTASKS_DB_ID", "")
        }
    ),
    
    "teams": DatabaseSchema(
        name="Команды",
        database_id=os.getenv("NOTION_TEAMS_DB_ID", ""),
        description="Управление командами",
        properties={
            "Name": {"type": "title"},
            "Участники": {"type": "people"},
            "Статус": {"type": "status"},
            "Описание": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Active", "Inactive", "Archived"]
        },
        select_options={},
        multi_select_options={},
        relations={}
    ),
    
    "learning": DatabaseSchema(
        name="Обучение",
        database_id=os.getenv("NOTION_LEARNING_DB_ID", ""),
        description="Обучение и развитие",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Тип": {"type": "select"},
            "Сложность": {"type": "select"},
            "Описание": {"type": "rich_text"},
            "Ссылка": {"type": "url"},
        },
        status_options={
            "Статус": ["Not started", "In progress", "Completed", "Abandoned"]
        },
        select_options={
            "Тип": ["Курс", "Книга", "Статья", "Видео", "Практика"],
            "Сложность": ["Начинающий", "Средний", "Продвинутый"]
        },
        multi_select_options={},
        relations={}
    ),
    
    "guides": DatabaseSchema(
        name="Гайды",
        database_id=os.getenv("NOTION_GUIDES_DB_ID", ""),
        description="Гайды и инструкции",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Категория": {"type": "select"},
            "Описание": {"type": "rich_text"},
            "Ссылка": {"type": "url"},
        },
        status_options={
            "Статус": ["Draft", "In Review", "Published", "Archived"]
        },
        select_options={
            "Категория": ["Дизайн", "Маркетинг", "SMM", "Разработка", "Управление"]
        },
        multi_select_options={},
        relations={}
    ),
    
    "super_guides": DatabaseSchema(
        name="Супергайды",
        database_id=os.getenv("NOTION_SUPER_GUIDES_DB_ID", ""),
        description="Сборники гайдов",
        properties={
            "Name": {"type": "title"},
            "Status": {"type": "status"},
            "В цепочке": {"type": "status"},
            "Супер сборник": {"type": "relation"},
            "Мини сборник": {"type": "relation"},
        },
        status_options={
            "Status": ["Not started", "In progress", "Done"],
            "В цепочке": ["Сторонний", "Планирование", "Предпроизводство", "Производство", "Продвижение", "Поддержка", "Закрыт"]
        },
        select_options={},
        multi_select_options={},
        relations={
            "Супер сборник": os.getenv("NOTION_SUPER_GUIDES_DB_ID", ""),
            "Мини сборник": os.getenv("NOTION_SUPER_GUIDES_DB_ID", "")
        }
    ),
    
    "epics": DatabaseSchema(
        name="Эпики",
        database_id=os.getenv("NOTION_EPICS_DB_ID", ""),
        description="Эпики проектов",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Описание": {"type": "rich_text"},
            "Приоритет": {"type": "select"},
        },
        status_options={
            "Статус": ["Not started", "In progress", "Done", "Canceled"]
        },
        select_options={
            "Приоритет": ["High", "Medium", "Low"]
        },
        multi_select_options={},
        relations={}
    ),
    
    "concepts": DatabaseSchema(
        name="Концепты",
        database_id=os.getenv("NOTION_CONCEPTS_DB_ID", ""),
        description="Концепты и сценарии",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Тип": {"type": "select"},
            "Описание": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Draft", "In Review", "Approved", "Rejected"]
        },
        select_options={
            "Тип": ["Концепт", "Сценарий", "Идея", "Прототип"]
        },
        multi_select_options={},
        relations={}
    ),
    
    "links": DatabaseSchema(
        name="Ссылки",
        database_id=os.getenv("NOTION_LINKS_DB_ID", ""),
        description="Полезные ссылки",
        properties={
            "Name": {"type": "title"},
            "URL": {"type": "url"},
            "Категория": {"type": "select"},
            "Описание": {"type": "rich_text"},
        },
        status_options={},
        select_options={
            "Категория": ["Инструмент", "Ресурс", "Статья", "Видео", "Другое"]
        },
        multi_select_options={},
        relations={}
    ),
    
    "clients": DatabaseSchema(
        name="Клиенты",
        database_id=os.getenv("NOTION_CLIENTS_DB_ID", ""),
        description="База клиентов",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Email": {"type": "email"},
            "Телефон": {"type": "phone_number"},
            "Описание": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Lead", "Active", "Inactive", "Lost"]
        },
        select_options={},
        multi_select_options={},
        relations={}
    ),
    
    "competitors": DatabaseSchema(
        name="Конкуренты",
        database_id=os.getenv("NOTION_COMPETITORS_DB_ID", ""),
        description="Анализ конкурентов",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Сайт": {"type": "url"},
            "Описание": {"type": "rich_text"},
            "Сильные стороны": {"type": "rich_text"},
            "Слабые стороны": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Active", "Inactive", "Analyzed"]
        },
        select_options={},
        multi_select_options={},
        relations={}
    ),
    
    "products": DatabaseSchema(
        name="Продукты",
        database_id=os.getenv("NOTION_PRODUCTS_DB_ID", ""),
        description="Продукты компании",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Категория": {"type": "select"},
            "Описание": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Development", "Active", "Discontinued"]
        },
        select_options={
            "Категория": ["Услуга", "Продукт", "Сервис"]
        },
        multi_select_options={},
        relations={}
    ),
    
    "rdt": DatabaseSchema(
        name="Сотрудники",
        database_id=os.getenv("NOTION_RDT_DB_ID", ""),
        description="База сотрудников",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Роль": {"type": "select"},
            "Описание": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Active", "Inactive", "Former"]
        },
        select_options={
            "Роль": ["Дизайнер", "Маркетолог", "SMM", "Разработчик", "Менеджер"]
        },
        multi_select_options={},
        relations={}
    ),
    
    "tasks_templates": DatabaseSchema(
        name="Типовые задачи",
        database_id=os.getenv("NOTION_TASKS_TEMPLATES_DB_ID", ""),
        description="Шаблоны типовых задач",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Категория": {"type": "select"},
            "Описание": {"type": "rich_text"},
            "Время": {"type": "number"},
            "Сложность": {"type": "select"},
            "Дизайн": {"type": "relation"},
        },
        status_options={
            "Статус": ["Active", "Inactive", "Archived", "Регулярные"]
        },
        select_options={
            "Категория": ["Дизайн", "Маркетинг", "SMM", "Разработка", "Управление"],
            "Сложность": ["Простая", "Средняя", "Высокая"]
        },
        multi_select_options={},
        relations={
            "Дизайн": os.getenv("NOTION_TASKS_DB_ID", "")
        }
    ),
    
    "content_plan": DatabaseSchema(
        name="Контент-план",
        database_id=os.getenv("NOTION_CONTENT_PLAN_DB_ID", ""),
        description="Планирование контента",
        properties={
            "Name": {"type": "title"},
            "Статус": {"type": "status"},
            "Платформа": {"type": "select"},
            "Дата публикации": {"type": "date"},
            "Описание": {"type": "rich_text"},
        },
        status_options={
            "Статус": ["Draft", "In Progress", "Scheduled", "Published"]
        },
        select_options={
            "Платформа": ["Instagram", "VK", "Telegram", "YouTube", "TikTok"]
        },
        multi_select_options={},
        relations={}
    ),
    
    "product_lines": DatabaseSchema(
        name="Линейки продуктов",
        database_id=os.getenv("PRODUCT_LINES_DB", ""),
        description="Линейки продуктов компании с артикулами и категориями",
        properties={
            "Name": {"type": "title"},
            "Артикул": {"type": "select"},
            "Категория": {"type": "select"},
            "Серия": {"type": "select"},
            "Статус": {"type": "status"},
            "Проекты полиграфии продуктов": {"type": "relation"},
            "Эпики": {"type": "relation"},
            "Контент план": {"type": "relation"},
            "Прогресс": {"type": "rollup"},
            "лайков": {"type": "formula"},
        },
        status_options={
            "Статус": ["Предпроизводство", "Производство", "Продвижение", "Поддержка", "Архив"]
        },
        select_options={
            "Артикул": ["BDC-03", "IDF-01", "RMF-01", "IDF-02", "BDG-03", "RMS-01", "RCK-21", "RVB-02", "RMV-01", "RCK-13", "RMP-01", "RMG-01", "RCK-09", "RMK-21", "RMH-01", "BDM-03", "JDM-80", "RPI-01", "RPV-01-A", "RVJ-02", "RGJ-04", "RPV-01", "RMV-02", "RFV-05", "RCK-18", "RPV-01 max", "RAR-01", "BDM-07"],
            "Категория": ["Блендер", "Турмалиновый стакан", "Климатический комплекс", "Турмалиновая палочка", "Датчик частиц PM2.5", "Нож Шеф 21", "Беспроводной Пылесос", "Нож Универсальный", "Очиститель воздуха", "Мельница", "Нож Для овощей", "Мойка воздуха", "Соковыжималка", "Ирригатор", "Авто комплект аксессуаров", "Авто пылесос", "Беспроводной моющий пылесос", "Нож Сантоку 18", "Авто пылесос макс.комплект", "Ополаскиватель кувшинов"],
            "Серия": ["Classic", "Flask", "Modern", "Stick", "Greenery 2", "Vitamin 2", "Mini", "Mini new", "Portable", "Vitamin", "Greenery", "Future", "RAR-01"]
        },
        multi_select_options={},
        relations={
            "Проекты полиграфии продуктов": os.getenv("PROJECTS_DB", ""),
            "Эпики": os.getenv("NOTION_EPICS_DB_ID", ""),
            "Контент план": os.getenv("NOTION_CONTENT_PLAN_DB_ID", "")
        }
    ),
    
    "advices": DatabaseSchema(
        name="Советы и чек-листы",
        database_id="23eace03-d9ff-8149-9313-fffa4c15c5e2",
        description="База для хранения советов, чек-листов и обучающих материалов",
        properties={
            "Title": {"type": "title"},
            "Content Type": {"type": "select"},
            "Category": {"type": "select"},
            "Priority": {"type": "number"},
            "Actionable": {"type": "checkbox"},
            "Confidence": {"type": "number"},
            "Content": {"type": "rich_text"},
            "Technical Details": {"type": "rich_text"},
            "Tags": {"type": "multi_select"},
            "Created Date": {"type": "date"},
            "URL": {"type": "url"},
            "Files & media": {"type": "files"}
        },
        status_options={},
        select_options={
            "Content Type": ["advice", "checklist", "guide", "tutorial", "tip"],
            "Category": ["настройки_камеры", "освещение", "композиция", "постобработка", "оборудование", "общие"]
        },
        multi_select_options={
            "Tags": ["фото_гайды", "медиа", "тест", "обучение", "практика"]
        },
        relations={}
    )
}

# --- KPI DATABASE SCHEMA ---
# ОБЯЗАТЕЛЬНЫЙ СТАНДАРТ ДЛЯ ВСЕХ KPI:
# 1. Название KPI (Name): только метрика (без направления/группы)
#    Пример: "Просмотры", "Клики", "Конверсия", "Продажи", "Охват", "Вовлечённость", "Время выполнения", "Качество выполнения", "Переходы", "Подписчики", "CTR"
# 2. Тип контента / направление: определяет группу ("Карточки товаров", "Соцсети", "Полиграфия", "YouTube" и т.д.)
# 3. Цель / задача: только число (int/float), без текста и единиц
# 4. Тип KPI: определяет, что за метрика (например, "Просмотры", "Клики" и т.д.)
# 5. Любое создание/обновление KPI сверяется с этой схемой, любые отклонения — ошибка
# 6. Менять структуру KPI можно только через изменение этой схемы
# --- END KPI STANDARD ---

def get_database_schema(db_name: str) -> Optional[DatabaseSchema]:
    """Получить схему базы данных по имени"""
    return DATABASE_SCHEMAS.get(db_name)

def get_database_schema_by_id(database_id: str) -> Optional[DatabaseSchema]:
    """Получить схему базы данных по ID"""
    for schema in DATABASE_SCHEMAS.values():
        if schema.database_id == database_id:
            return schema
    return None

def get_all_database_ids() -> Dict[str, str]:
    """Получить все ID баз данных из переменных окружения"""
    return {
        "tasks": os.getenv("NOTION_TASKS_DB_ID", ""),
        "subtasks": os.getenv("NOTION_SUBTASKS_DB_ID", ""),
        "projects": os.getenv("NOTION_PROJECTS_DB_ID", ""),
        "ideas": os.getenv("NOTION_IDEAS_DB_ID", ""),
        "materials": os.getenv("NOTION_MATERIALS_DB_ID", ""),
        "marketing_tasks": os.getenv("NOTION_MARKETING_TASKS_DB_ID", ""),
        "platforms": os.getenv("NOTION_PLATFORMS_DB_ID", ""),
        "kpi": os.getenv("NOTION_KPI_DB_ID", ""),
        "teams": os.getenv("NOTION_TEAMS_DB_ID", ""),
        "learning": os.getenv("NOTION_LEARNING_DB_ID", ""),
        "guides": os.getenv("NOTION_GUIDES_DB_ID", ""),
        "super_guides": os.getenv("NOTION_SUPER_GUIDES_DB_ID", ""),
        "epics": os.getenv("NOTION_EPICS_DB_ID", ""),
        "concepts": os.getenv("NOTION_CONCEPTS_DB_ID", ""),
        "links": os.getenv("NOTION_LINKS_DB_ID", ""),
        "clients": os.getenv("NOTION_CLIENTS_DB_ID", ""),
        "competitors": os.getenv("NOTION_COMPETITORS_DB_ID", ""),
        "products": os.getenv("NOTION_PRODUCTS_DB_ID", ""),
        "rdt": os.getenv("NOTION_RDT_DB_ID", ""),
        "tasks_templates": os.getenv("NOTION_TASKS_TEMPLATES_DB_ID", ""),
        "content_plan": os.getenv("NOTION_CONTENT_PLAN_DB_ID", ""),
        "product_lines": os.getenv("PRODUCT_LINES_DB", "")
    }

def get_database_id(db_name: str) -> str:
    """Получить ID базы данных по имени"""
    schema = get_database_schema(db_name)
    return schema.database_id if schema else ""

def get_status_options(db_name: str, property_name: str) -> List[str]:
    """Получить варианты статусов для поля базы данных"""
    schema = get_database_schema(db_name)
    if schema and property_name in schema.status_options:
        return schema.status_options[property_name]
    return []

def get_select_options(db_name: str, property_name: str) -> List[str]:
    """Получить варианты выбора для поля базы данных"""
    schema = get_database_schema(db_name)
    if schema and property_name in schema.select_options:
        return schema.select_options[property_name]
    return []

def get_select_options_by_id(database_id: str, property_name: str) -> List[str]:
    """Получить варианты выбора для поля базы данных по ID"""
    schema = get_database_schema_by_id(database_id)
    if schema and property_name in schema.select_options:
        return schema.select_options[property_name]
    return []
    
def get_multi_select_options(db_name: str, property_name: str) -> List[str]:
    """Получить варианты множественного выбора для поля базы данных"""
    schema = get_database_schema(db_name)
    if schema and property_name in schema.multi_select_options:
        return schema.multi_select_options[property_name]
    return []

def get_multi_select_options_by_id(database_id: str, property_name: str) -> List[str]:
    """Получить варианты множественного выбора для поля базы данных по ID"""
    schema = get_database_schema_by_id(database_id)
    if schema and property_name in schema.multi_select_options:
        return schema.multi_select_options[property_name]
    return []

def get_relations(db_name: str) -> Dict[str, str]:
    """Получить связи базы данных"""
    schema = get_database_schema(db_name)
    return schema.relations if schema else {}

def validate_property_value(db_name: str, property_name: str, value: str) -> bool:
    """Проверить, что значение поля корректно для базы данных"""
    schema = get_database_schema(db_name)
    if not schema:
        return False
    
    # Проверка статусов
    if property_name in schema.status_options:
        return value in schema.status_options[property_name]
    
    # Проверка выборов
    if property_name in schema.select_options:
        return value in schema.select_options[property_name]
    
    # Проверка множественных выборов
    if property_name in schema.multi_select_options:
        return value in schema.multi_select_options[property_name]
    
    return True

def get_all_schemas() -> Dict[str, DatabaseSchema]:
    """Возвращает все схемы баз данных для MCP сервера"""
    return DATABASE_SCHEMAS 