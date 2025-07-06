"""
Telegram бот для быстрого ведения отчётов дизайнерами
Интеграция с Notion для автоматического обновления задач
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from notion_client import Client

# Настройка логирования
logging.basicConfig(level=logging.INFO)
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
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.materials_added is None:
            self.materials_added = []
        if self.links_added is None:
            self.links_added = []

@dataclass
class DesignerSession:
    """Сессия дизайнера для сбора отчётов"""
    user_id: int
    designer_name: str
    current_project: str = ""
    current_task: str = ""
    reports_today: List[WorkReport] = None
    state: str = "idle"  # idle, waiting_project, waiting_task, waiting_description, waiting_time
    
    def __post_init__(self):
        if self.reports_today is None:
            self.reports_today = []

class DesignerReportBot:
    """Бот для ведения отчётов дизайнеров"""
    
    def __init__(self):
        # Загрузка переменных окружения
        from dotenv import load_dotenv
        load_dotenv()
        
        # Проверка обязательных переменных
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "NOTION_TOKEN",
            "NOTION_TASKS_DB_ID",
            "NOTION_MATERIALS_DB_ID",
            "NOTION_PROJECTS_DB_ID"
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {missing_vars}")
        
        self.bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        
        # Настройки из переменных окружения (без дефолтов)
        self.tasks_database_id = os.getenv("NOTION_TASKS_DB_ID")
        self.materials_database_id = os.getenv("NOTION_MATERIALS_DB_ID")
        self.projects_database_id = os.getenv("NOTION_PROJECTS_DB_ID")
        
        # Логирование конфигурации
        logger.info(f"Bot initialized with:")
        logger.info(f"  Tasks DB: {self.tasks_database_id}")
        logger.info(f"  Materials DB: {self.materials_database_id}")
        logger.info(f"  Projects DB: {self.projects_database_id}")
        
        # Сессии пользователей
        self.sessions: Dict[int, DesignerSession] = {}
        
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

Я помогу тебе быстро вести отчёты о работе.

📋 Доступные команды:
/report - Добавить отчёт о работе
/today - Посмотреть отчёты за сегодня
/help - Помощь

💡 Пример отчёта:
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
        
        for project in projects[:8]:  # Максимум 8 кнопок
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
    
    def handle_help(self, message: Message):
        """Показать справку"""
        help_text = """
🎨 Справка по боту отчётов

📋 Команды:
/report - Добавить отчёт о работе
/today - Посмотреть отчёты за сегодня
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
            # Сохранить описание во временное поле
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
                    work_description=getattr(session, 'temp_description', ''),
                    time_spent_hours=time_spent
                )
                
                # Добавить в сессию
                session.reports_today.append(report)
                
                # Обновить в Notion
                self.update_notion_task(report)
                
                # Сбросить состояние
                session.state = "idle"
                session.current_project = ""
                session.current_task = ""
                
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
        # Паттерны для быстрого формата
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
        user_id = message.from_user.id
        session = self.sessions[user_id]
        
        # Парсинг быстрого отчёта
        # Пример: "Коробки мультиварки RMP04 - верстка 2 часа"
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
                    # Последнее слово - задача, остальное - проект
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
            
            return projects[:10]  # Максимум 10 проектов
        
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
    
    def run(self):
        """Запустить бота"""
        logger.info("🚀 Запуск Designer Report Bot...")
        self.bot.polling(none_stop=True)

def main():
    """Главная функция"""
    bot = DesignerReportBot()
    bot.run()

if __name__ == "__main__":
    main() 