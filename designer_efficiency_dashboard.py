"""
🎨 Designer Efficiency Dashboard
Интегрированная система для отчётов, метрик и KPI дизайнеров
Объединяет отчёты, эффективность, актуальные задачи и аналитику
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from notion_client import Client

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DesignerKPI:
    """KPI дизайнера"""
    designer_name: str
    efficiency: float = 0.0  # Эффективность (0-1)
    overdue_tasks: float = 0.0  # Просрочки (0-1)
    quality: float = 0.0  # Качество (0-1)
    report_coverage: float = 0.0  # Покрытие отчётами (0-1)
    total_time_hours: float = 0.0
    tasks_completed: int = 0
    projects_active: int = 0
    
    def calculate_bonus(self, base_salary: float = 100000) -> float:
        """Расчёт бонуса по формуле"""
        bonus_multiplier = (1 + self.efficiency * 0.2 + self.quality * 0.3 - self.overdue_tasks * 0.3)
        return base_salary * bonus_multiplier

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

@dataclass
class DesignerSession:
    """Сессия дизайнера"""
    user_id: int
    designer_name: str
    current_project: str = ""
    current_task: str = ""
    reports_today: List[WorkReport] = None
    state: str = "idle"
    temp_description: str = ""
    
    def __post_init__(self):
        if self.reports_today is None:
            self.reports_today = []

class DesignerEfficiencyDashboard:
    """Интегрированный дашборд эффективности дизайнеров"""
    
    def __init__(self):
        # Проверка переменных окружения
        required_vars = ["TELEGRAM_BOT_TOKEN", "NOTION_TOKEN"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {missing_vars}")
        
        self.bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        
        # Базы данных
        self.tasks_database_id = os.getenv("NOTION_TASKS_DB_ID", "d09df250ce7e4e0d9fbe4e036d320def")
        self.materials_database_id = os.getenv("NOTION_MATERIALS_DB_ID", "1d9ace03d9ff804191a4d35aeedcbbd4")
        self.projects_database_id = os.getenv("NOTION_PROJECTS_DB_ID", "342f18c67a5e41fead73dcec00770f4e")
        self.time_log_database_id = os.getenv("NOTION_TIME_LOG_DB_ID", "")  # Будет создана
        
        # Сессии пользователей
        self.sessions: Dict[int, DesignerSession] = {}
        
        # KPI кэш
        self.kpi_cache: Dict[str, DesignerKPI] = {}
        
        # Логирование конфигурации
        logger.info("🎨 Designer Efficiency Dashboard initialized")
        logger.info(f"  Tasks DB: {self.tasks_database_id}")
        logger.info(f"  Materials DB: {self.materials_database_id}")
        logger.info(f"  Projects DB: {self.projects_database_id}")
        
        # Регистрация обработчиков
        self.register_handlers()
    
    def register_handlers(self):
        """Регистрация обработчиков команд"""
        
        @self.bot.message_handler(commands=['start'])
        def start_command(message: Message):
            self.handle_start(message)
        
        @self.bot.message_handler(commands=['report'])
        def report_command(message: Message):
            self.handle_report(message)
        
        @self.bot.message_handler(commands=['today'])
        def today_command(message: Message):
            self.handle_today(message)
        
        @self.bot.message_handler(commands=['kpi'])
        def kpi_command(message: Message):
            self.handle_kpi(message)
        
        @self.bot.message_handler(commands=['tasks'])
        def tasks_command(message: Message):
            self.handle_tasks(message)
        
        @self.bot.message_handler(commands=['efficiency'])
        def efficiency_command(message: Message):
            self.handle_efficiency(message)
        
        @self.bot.message_handler(commands=['help'])
        def help_command(message: Message):
            self.handle_help(message)
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_text(message: Message):
            self.handle_text_message(message)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call: CallbackQuery):
            self.handle_callback_query(call)
    
    def handle_start(self, message: Message):
        """Обработка команды /start"""
        user_id = message.from_user.id
        designer_name = message.from_user.first_name
        
        # Создать или обновить сессию
        if user_id not in self.sessions:
            self.sessions[user_id] = DesignerSession(
                user_id=user_id,
                designer_name=designer_name
            )
        
        welcome_text = f"""
🎨 Привет, {designer_name}! 

Я - Designer Efficiency Dashboard - твой помощник для:
📊 Отчётов о работе
📈 KPI и эффективности  
📋 Актуальных задач
🎯 Метрик производительности

📋 Доступные команды:
/report - Добавить отчёт о работе
/today - Отчёты за сегодня
/kpi - Твои KPI и эффективность
/tasks - Актуальные задачи
/efficiency - Детальная аналитика
/help - Подробная справка

💡 Пример быстрого отчёта:
"Коробки мультиварки RMP04 - верстка 2 часа"

Готов начать? Нажми /report
        """
        
        self.bot.reply_to(message, welcome_text.strip())
    
    def handle_report(self, message: Message):
        """Обработка команды /report"""
        user_id = message.from_user.id
        
        if user_id not in self.sessions:
            self.sessions[user_id] = DesignerSession(
                user_id=user_id,
                designer_name=message.from_user.first_name
            )
        
        session = self.sessions[user_id]
        session.state = "waiting_project"
        
        # Показать кнопки с проектами
        projects = self.get_active_projects()
        keyboard = InlineKeyboardMarkup()
        
        for project in projects[:8]:
            keyboard.add(InlineKeyboardButton(
                text=project,
                callback_data=f"project:{project}"
            ))
        
        keyboard.add(InlineKeyboardButton(
            text="➕ Ввести вручную",
            callback_data="project:manual"
        ))
        
        self.bot.reply_to(
            message,
            "📋 Выбери проект или введи название:",
            reply_markup=keyboard
        )
    
    def handle_today(self, message: Message):
        """Показать отчёты за сегодня"""
        user_id = message.from_user.id
        
        if user_id not in self.sessions:
            self.bot.reply_to(message, "❌ Сначала начни сессию: /start")
            return
        
        session = self.sessions[user_id]
        reports = session.reports_today
        
        if not reports:
            self.bot.reply_to(message, "📝 У тебя пока нет отчётов за сегодня. Начни с /report")
            return
        
        # Формировать отчёт
        total_time = sum(r.time_spent_hours for r in reports)
        
        report_text = f"📊 Отчёты за сегодня ({len(reports)} задач):\n\n"
        
        for i, report in enumerate(reports, 1):
            report_text += f"{i}. {report.project_name} - {report.task_name}\n"
            report_text += f"   ⏱️ {report.time_spent_hours} ч\n"
            report_text += f"   📝 {report.work_description}\n"
            
            if report.materials_added:
                report_text += f"   📎 Материалы: {', '.join(report.materials_added)}\n"
            
            if report.links_added:
                report_text += f"   🔗 Ссылки: {', '.join(report.links_added)}\n"
            
            report_text += "\n"
        
        report_text += f"⏰ Общее время: {total_time} часов"
        
        self.bot.reply_to(message, report_text)
    
    def handle_kpi(self, message: Message):
        """Показать KPI дизайнера"""
        user_id = message.from_user.id
        
        if user_id not in self.sessions:
            self.bot.reply_to(message, "❌ Сначала начни сессию: /start")
            return
        
        session = self.sessions[user_id]
        designer_name = session.designer_name
        
        # Получить KPI
        kpi = self.calculate_designer_kpi(designer_name)
        
        kpi_text = f"""
📈 KPI для {designer_name}

🎯 Эффективность: {kpi.efficiency:.1%}
⏰ Просрочки: {kpi.overdue_tasks:.1%}
✨ Качество: {kpi.quality:.1%}
📊 Покрытие отчётами: {kpi.report_coverage:.1%}

📋 Статистика:
⏱️ Общее время: {kpi.total_time_hours:.1f} ч
✅ Завершённых задач: {kpi.tasks_completed}
📁 Активных проектов: {kpi.projects_active}

💰 Расчётный бонус: {kpi.calculate_bonus():,.0f} ₽
        """
        
        self.bot.reply_to(message, kpi_text.strip())
    
    def handle_tasks(self, message: Message):
        """Показать актуальные задачи"""
        user_id = message.from_user.id
        
        if user_id not in self.sessions:
            self.bot.reply_to(message, "❌ Сначала начни сессию: /start")
            return
        
        session = self.sessions[user_id]
        designer_name = session.designer_name
        
        # Получить задачи дизайнера
        tasks = self.get_designer_tasks(designer_name)
        
        if not tasks:
            self.bot.reply_to(message, "📝 У тебя нет активных задач")
            return
        
        tasks_text = f"📋 Актуальные задачи для {designer_name}:\n\n"
        
        for i, task in enumerate(tasks[:10], 1):
            tasks_text += f"{i}. {task['name']}\n"
            tasks_text += f"   📁 Проект: {task['project']}\n"
            tasks_text += f"   📊 Статус: {task['status']}\n"
            tasks_text += f"   ⏱️ Время: {task['time_spent']} мин\n"
            tasks_text += "\n"
        
        if len(tasks) > 10:
            tasks_text += f"... и ещё {len(tasks) - 10} задач"
        
        self.bot.reply_to(message, tasks_text)
    
    def handle_efficiency(self, message: Message):
        """Показать детальную аналитику эффективности"""
        user_id = message.from_user.id
        
        if user_id not in self.sessions:
            self.bot.reply_to(message, "❌ Сначала начни сессию: /start")
            return
        
        session = self.sessions[user_id]
        designer_name = session.designer_name
        
        # Получить детальную аналитику
        analytics = self.get_designer_analytics(designer_name)
        
        analytics_text = f"""
📊 Детальная аналитика для {designer_name}

⏱️ Временные метрики:
   Среднее время на задачу: {analytics['avg_time_per_task']:.1f} мин
   Эффективность планирования: {analytics['planning_efficiency']:.1%}
   Время в потоке: {analytics['flow_time']:.1f} ч

📈 Качественные метрики:
   Процент завершённых задач: {analytics['completion_rate']:.1%}
   Средняя оценка качества: {analytics['avg_quality']:.1f}/5
   Количество ревизий: {analytics['revisions_count']}

🎯 Рекомендации:
{analytics['recommendations']}
        """
        
        self.bot.reply_to(message, analytics_text.strip())
    
    def handle_help(self, message: Message):
        """Показать справку"""
        help_text = """
🎨 Designer Efficiency Dashboard - Справка

📋 Основные команды:
/report - Добавить отчёт о работе
/today - Посмотреть отчёты за сегодня
/kpi - Твои KPI и эффективность
/tasks - Актуальные задачи
/efficiency - Детальная аналитика
/help - Эта справка

💡 Форматы отчётов:

1. Быстрый формат:
"Коробки мультиварки RMP04 - верстка 2 часа"

2. Подробный формат:
Проект: Коробки мультиварки RMP04
Задача: Верстка макета
Описание: Создал адаптивную верстку
Время: 2 часа
Материалы: figma.com/file/abc123
Ссылки: drive.google.com/file/xyz

3. С комментариями:
"RMP04 - верстка 2ч + добавил комментарии к макету"

🔄 Автоматически обновляется в Notion:
- Время в задачах
- Статусы
- Материалы
- Комментарии
- KPI и метрики

📊 KPI рассчитываются по формуле:
бонус = base * (1 + эффективность*0.2 + качество*0.3 − просрочки*0.3)
        """
        
        self.bot.reply_to(message, help_text.strip())
    
    def handle_text_message(self, message: Message):
        """Обработка текстовых сообщений"""
        user_id = message.from_user.id
        text = message.text.strip()
        
        if user_id not in self.sessions:
            self.bot.reply_to(message, "❌ Сначала начни сессию: /start")
            return
        
        session = self.sessions[user_id]
        
        # Проверить быстрый формат
        if self.is_quick_report_format(text):
            self.process_quick_report(message, text)
            return
        
        # Обработка по состоянию
        if session.state == "waiting_project":
            session.current_project = text
            session.state = "waiting_task"
            self.bot.reply_to(message, "📝 Теперь введи название задачи:")
        
        elif session.state == "waiting_task":
            session.current_task = text
            session.state = "waiting_description"
            self.bot.reply_to(message, "📝 Опиши, что ты делал:")
        
        elif session.state == "waiting_description":
            session.state = "waiting_time"
            session.temp_description = text
            self.bot.reply_to(message, "⏱️ Сколько времени потратил? (например: 2.5 часа)")
        
        elif session.state == "waiting_time":
            time_match = re.search(r'(\d+(?:\.\d+)?)', text)
            if time_match:
                time_spent = float(time_match.group(1))
                
                # Создать отчёт
                report = WorkReport(
                    designer_name=session.designer_name,
                    project_name=session.current_project,
                    task_name=session.current_task,
                    work_description=session.temp_description,
                    time_spent_hours=time_spent
                )
                
                # Добавить в сессию
                session.reports_today.append(report)
                
                # Обновить в Notion
                self.update_notion_task(report)
                
                # Обновить KPI
                self.update_designer_kpi(session.designer_name)
                
                # Сбросить состояние
                session.state = "idle"
                session.current_project = ""
                session.current_task = ""
                session.temp_description = ""
                
                self.bot.reply_to(
                    message,
                    f"✅ Отчёт сохранён!\n\n"
                    f"📋 Проект: {report.project_name}\n"
                    f"📝 Задача: {report.task_name}\n"
                    f"⏱️ Время: {report.time_spent_hours} ч\n"
                    f"📄 Описание: {report.work_description}\n\n"
                    f"Продолжить? /report"
                )
            else:
                self.bot.reply_to(message, "❌ Не понял время. Введи число (например: 2.5):")
    
    def handle_callback_query(self, call: CallbackQuery):
        """Обработка callback запросов"""
        user_id = call.from_user.id
        data = call.data
        
        if user_id not in self.sessions:
            self.bot.answer_callback_query(call.id, "❌ Сессия не найдена")
            return
        
        session = self.sessions[user_id]
        
        if data.startswith("project:"):
            project = data.split(":", 1)[1]
            
            if project == "manual":
                session.state = "waiting_project"
                self.bot.edit_message_text(
                    "📝 Введи название проекта:",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
            else:
                session.current_project = project
                session.state = "waiting_task"
                
                # Показать задачи проекта
                tasks = self.get_tasks_for_project(project)
                keyboard = InlineKeyboardMarkup()
                
                for task in tasks[:8]:
                    keyboard.add(InlineKeyboardButton(
                        text=task,
                        callback_data=f"task:{task}"
                    ))
                
                keyboard.add(InlineKeyboardButton(
                    text="➕ Ввести вручную",
                    callback_data="task:manual"
                ))
                
                self.bot.edit_message_text(
                    f"📋 Выбери задачу для проекта '{project}':",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=keyboard
                )
        
        elif data.startswith("task:"):
            task = data.split(":", 1)[1]
            
            if task == "manual":
                session.state = "waiting_task"
                self.bot.edit_message_text(
                    "📝 Введи название задачи:",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
            else:
                session.current_task = task
                session.state = "waiting_description"
                
                self.bot.edit_message_text(
                    f"📝 Опиши, что ты делал для задачи '{task}':",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
    
    def is_quick_report_format(self, text: str) -> bool:
        """Проверить, является ли текст быстрым отчётом"""
        import re
        patterns = [
            r'.+ - .+ \d+(?:\.\d+)?\s*(?:час|ч|часа|часов)',
            r'.+ \d+(?:\.\d+)?\s*(?:час|ч|часа|часов)',
            r'.+ - \d+(?:\.\d+)?\s*(?:час|ч|часа|часов)'
        ]
        
        for pattern in patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def process_quick_report(self, message: Message, text: str):
        """Обработать быстрый отчёт"""
        import re
        user_id = message.from_user.id
        session = self.sessions[user_id]
        
        # Парсинг быстрого отчёта
        parts = text.split(' - ')
        
        if len(parts) >= 2:
            project_task = parts[0].strip()
            description_time = parts[1].strip()
            
            # Извлечь время
            time_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:час|ч|часа|часов)', description_time, re.IGNORECASE)
            if time_match:
                time_spent = float(time_match.group(1))
                description = re.sub(r'\d+(?:\.\d+)?\s*(?:час|ч|часа|часов)', '', description_time).strip()
                
                # Разделить проект и задачу
                project_parts = project_task.split()
                if len(project_parts) >= 2:
                    task = project_parts[-1]
                    project = ' '.join(project_parts[:-1])
                else:
                    project = project_task
                    task = "Общая работа"
                
                # Создать отчёт
                report = WorkReport(
                    designer_name=session.designer_name,
                    project_name=project,
                    task_name=task,
                    work_description=description,
                    time_spent_hours=time_spent
                )
                
                # Добавить в сессию
                session.reports_today.append(report)
                
                # Обновить в Notion
                self.update_notion_task(report)
                
                # Обновить KPI
                self.update_designer_kpi(session.designer_name)
                
                self.bot.reply_to(
                    message,
                    f"✅ Быстрый отчёт сохранён!\n\n"
                    f"📋 Проект: {report.project_name}\n"
                    f"📝 Задача: {report.task_name}\n"
                    f"⏱️ Время: {report.time_spent_hours} ч\n"
                    f"📄 Описание: {report.work_description}\n\n"
                    f"Продолжить? /report"
                )
            else:
                self.bot.reply_to(message, "❌ Не понял время в отчёте. Используй формат: 'Проект - описание 2 часа'")
        else:
            self.bot.reply_to(message, "❌ Неправильный формат. Используй: 'Проект - описание 2 часа'")
    
    def get_active_projects(self) -> List[str]:
        """Получить список активных проектов"""
        try:
            response = self.notion.databases.query(
                database_id=self.projects_database_id,
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
            
            return projects[:10]
        
        except Exception as e:
            logger.error(f"Ошибка получения проектов: {e}")
            return ["Коробки мультиварки RMP04", "Брендинг", "Дизайн сайта"]
    
    def get_tasks_for_project(self, project_name: str) -> List[str]:
        """Получить задачи для проекта"""
        try:
            # Сначала найти проект
            project_response = self.notion.databases.query(
                database_id=self.projects_database_id,
                filter={
                    "property": "Name",
                    "title": {
                        "equals": project_name
                    }
                }
            )
            
            if not project_response["results"]:
                return ["Общая работа"]
            
            project_id = project_response["results"][0]["id"]
            
            # Найти задачи для проекта
            tasks_response = self.notion.databases.query(
                database_id=self.tasks_database_id,
                filter={
                    "property": "Проект",
                    "relation": {
                        "contains": project_id
                    }
                }
            )
            
            tasks = []
            for page in tasks_response["results"]:
                name_prop = page["properties"].get("Задача", {})
                if name_prop.get("title"):
                    tasks.append(name_prop["title"][0]["plain_text"])
            
            return tasks[:8] if tasks else ["Общая работа"]
        
        except Exception as e:
            logger.error(f"Ошибка получения задач: {e}")
            return ["Верстка", "Дизайн", "Брендинг", "Общая работа"]
    
    def update_notion_task(self, report: WorkReport):
        """Обновить задачу в Notion"""
        try:
            # Найти задачу по названию
            response = self.notion.databases.query(
                database_id=self.tasks_database_id,
                filter={
                    "property": "Задача",
                    "title": {
                        "contains": report.task_name
                    }
                }
            )
            
            if response["results"]:
                task_id = response["results"][0]["id"]
                
                # Обновить время и статус
                update_data = {
                    "properties": {
                        "Затрачено_минут": {
                            "number": int(report.time_spent_hours * 60)
                        }
                    }
                }
                
                # Добавить комментарий
                if report.work_description:
                    update_data["properties"]["Комментарии"] = {
                        "rich_text": [
                            {
                                "text": {
                                    "content": f"{datetime.now().strftime('%H:%M')} - {report.work_description}"
                                }
                            }
                        ]
                    }
                
                self.notion.pages.update(page_id=task_id, **update_data)
                logger.info(f"Обновлена задача: {report.task_name}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления задачи: {e}")
    
    def calculate_designer_kpi(self, designer_name: str) -> DesignerKPI:
        """Рассчитать KPI дизайнера"""
        # Здесь будет логика расчёта KPI из Notion
        # Пока возвращаем тестовые данные
        return DesignerKPI(
            designer_name=designer_name,
            efficiency=0.85,
            overdue_tasks=0.05,
            quality=0.95,
            report_coverage=0.90,
            total_time_hours=8.5,
            tasks_completed=5,
            projects_active=3
        )
    
    def update_designer_kpi(self, designer_name: str):
        """Обновить KPI дизайнера"""
        # Обновить кэш KPI
        self.kpi_cache[designer_name] = self.calculate_designer_kpi(designer_name)
    
    def get_designer_tasks(self, designer_name: str) -> List[Dict]:
        """Получить задачи дизайнера"""
        try:
            response = self.notion.databases.query(
                database_id=self.tasks_database_id,
                filter={
                    "property": "Участники",
                    "people": {
                        "contains": designer_name
                    }
                }
            )
            
            tasks = []
            for page in response["results"]:
                task = {
                    "name": page["properties"].get("Задача", {}).get("title", [{}])[0].get("plain_text", ""),
                    "project": "Не указан",
                    "status": page["properties"].get("Статус", {}).get("status", {}).get("name", "Не указан"),
                    "time_spent": page["properties"].get("Затрачено_минут", {}).get("number", 0)
                }
                tasks.append(task)
            
            return tasks[:10]
        
        except Exception as e:
            logger.error(f"Ошибка получения задач дизайнера: {e}")
            return []
    
    def get_designer_analytics(self, designer_name: str) -> Dict[str, Any]:
        """Получить детальную аналитику дизайнера"""
        # Здесь будет логика получения аналитики
        return {
            "avg_time_per_task": 120.0,
            "planning_efficiency": 0.85,
            "flow_time": 6.5,
            "completion_rate": 0.92,
            "avg_quality": 4.8,
            "revisions_count": 2,
            "recommendations": "Отличная работа! Рекомендуется больше времени проводить в состоянии потока."
        }
    
    def run(self):
        """Запустить дашборд"""
        logger.info("🚀 Запуск Designer Efficiency Dashboard...")
        self.bot.polling(none_stop=True)

def main():
    """Главная функция"""
    dashboard = DesignerEfficiencyDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 