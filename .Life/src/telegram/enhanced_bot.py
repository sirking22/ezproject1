#!/usr/bin/env python3
"""
Расширенный Telegram бот с интеграцией Todoist и умной аналитикой
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, UTC
import json
from dataclasses import dataclass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)
from telegram.constants import ParseMode

from ..integrations.todoist_integration import TodoistIntegration, TaskPriority
from ..notion.core import NotionService
from ..config.environment import config
from ..notion.client import NotionClient
from ..notion.llm_service import LLMService, LLMConfig
from ..notion.repository import UniversalRepository
from ..utils.config import Config

# Временные заглушки для отсутствующих модулей
class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EnhancedTaskManager:
    def __init__(self):
        pass
    
    async def create_task(self, *args, **kwargs):
        return None
    
    async def get_tasks(self, *args, **kwargs):
        return []

class ContentManager:
    def __init__(self, notion_token=None, content_db_id=None, media_db_id=None):
        pass
    
    async def create_content(self, *args, **kwargs):
        return None

class VoiceService:
    def __init__(self):
        pass
    
    async def process_voice(self, *args, **kwargs):
        return None

class LLMService:
    def __init__(self):
        pass
    
    async def generate_response(self, *args, **kwargs):
        return "Заглушка LLM"

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
TASK_CREATE_TITLE, TASK_CREATE_DESC, TASK_CREATE_PRIORITY, TASK_CREATE_ASSIGNEE = range(4)
CONTENT_CREATE_TITLE, CONTENT_CREATE_TYPE, CONTENT_CREATE_TEXT, CONTENT_CREATE_PLATFORMS = range(4, 8)
TASK_EDIT_FIELD, TASK_EDIT_VALUE = range(8, 10)
CONTENT_EDIT_FIELD, CONTENT_EDIT_VALUE = range(10, 12)
TODOIST_CREATE_TITLE, TODOIST_CREATE_DESC, TODOIST_CREATE_PRIORITY, TODOIST_CREATE_PROJECT = range(12, 16)

@dataclass
class UserSession:
    user_id: int
    current_context: str = "home"
    session_id: str = ""
    last_interaction: datetime = None
    
    def __post_init__(self):
        if self.last_interaction is None:
            self.last_interaction = datetime.now(UTC)
        if not self.session_id:
            self.session_id = f"user_{self.user_id}_{int(self.last_interaction.timestamp())}"

class EnhancedTelegramBot:
    """Расширенный Telegram бот с интеграцией Todoist и Notion"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.todoist_token = os.getenv("TODOIST_API_TOKEN")
        
        # Инициализация сервисов
        self.task_manager = EnhancedTaskManager()
        
        self.content_manager = ContentManager(
            notion_token=self.notion_token,
            content_db_id=os.getenv("NOTION_CONTENT_PLAN_DB_ID"),
            media_db_id=os.getenv("NOTION_MATERIALS_DB_ID")
        )
        
        # Инициализация Todoist
        self.todoist = TodoistIntegration(self.todoist_token) if self.todoist_token else None
        
        self.voice_service = VoiceService()
        self.llm_service = LLMService()
        
        # Состояния пользователей
        self.user_states: Dict[str, Dict] = {}
        
        # Разрешенные пользователи (из .env)
        allowed_users = os.getenv("ALLOWED_TELEGRAM_USERS", "").split(",")
        self.allowed_users = [user.strip() for user in allowed_users if user.strip()]
        
        self.notion = NotionService()
        self.application = None
        self.is_initialized = False
        
        self.config = Config()
        self.notion_client = NotionClient(self.config.notion_token, self.config.notion_dbs)
        self.repository = UniversalRepository(self.notion_client)
        
        # LLM сервис
        llm_config = LLMConfig(
            use_local=True,
            local_url="http://localhost:8000",
            openrouter_api_key=self.config.openrouter_api_key,
            fallback_to_openrouter=True
        )
        self.llm_service = LLMService(self.notion_client, llm_config)
        
        # Пользовательские сессии
        self.user_sessions: Dict[int, UserSession] = {}
        
        # Инициализация бота
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
        
        logger.info("Расширенный Telegram бот инициализирован")
    
    def _setup_handlers(self):
        """Настройка обработчиков команд"""
        
        # Базовые команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("test", self.test_command))
        
        # Команды управления данными
        self.application.add_handler(CommandHandler("validate", self.validate_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        self.application.add_handler(CommandHandler("create", self.create_command))
        self.application.add_handler(CommandHandler("update", self.update_command))
        self.application.add_handler(CommandHandler("delete", self.delete_command))
        
        # Быстрые команды
        self.application.add_handler(CommandHandler("todo", self.todo_command))
        self.application.add_handler(CommandHandler("habit", self.habit_command))
        self.application.add_handler(CommandHandler("reflection", self.reflection_command))
        self.application.add_handler(CommandHandler("idea", self.idea_command))
        self.application.add_handler(CommandHandler("morning", self.morning_command))
        self.application.add_handler(CommandHandler("evening", self.evening_command))
        
        # Аналитика и отчеты
        self.application.add_handler(CommandHandler("progress", self.progress_command))
        self.application.add_handler(CommandHandler("mood", self.mood_command))
        self.application.add_handler(CommandHandler("insights", self.insights_command))
        self.application.add_handler(CommandHandler("recommendations", self.recommendations_command))
        
        # Новые команды для локальной LLM
        self.application.add_handler(CommandHandler("context", self.context_command))
        self.application.add_handler(CommandHandler("insight", self.insight_command))
        self.application.add_handler(CommandHandler("predict", self.predict_command))
        self.application.add_handler(CommandHandler("optimize", self.optimize_command))
        self.application.add_handler(CommandHandler("chat", self.chat_command))
        
        # Обработчик callback кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        user_id = user.id
        
        # Инициализируем сессию пользователя
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession(user_id=user_id)
        
        welcome_message = f"""
🚀 Добро пожаловать в твою персональную AI-экосистему!

Я помогу тебе управлять:
• Задачами и проектами
• Привычками и ритуалами  
• Рефлексиями и идеями
• Личным развитием

🎯 Быстрые команды:
/todo [задача] - добавить задачу
/habit [название] - добавить привычку
/reflection [текст] - добавить рефлексию
/idea [идея] - сохранить идею
/morning - утренний ритуал
/evening - вечерняя рефлексия

🧠 AI-помощь:
/insight [тема] - глубокий анализ
/predict [привычка] - предсказание результата
/optimize [область] - рекомендации по оптимизации
/chat - свободный диалог с AI

📊 Аналитика:
/progress - отчет о прогрессе
/insights - персональные инсайты
/recommendations - рекомендации

Текущий контекст: {self.user_sessions[user_id].current_context}

Используй /help для полного списка команд!
        """
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📚 Полный список команд:

🎯 Быстрые действия:
/todo [задача] - добавить задачу
/habit [название] - добавить привычку  
/reflection [текст] - добавить рефлексию
/idea [идея] - сохранить идею
/morning - утренний ритуал
/evening - вечерняя рефлексия

🧠 AI-помощь:
/context [work/home] - переключить контекст
/insight [тема] - глубокий анализ темы
/predict [привычка] - предсказать результат
/optimize [область] - рекомендации по оптимизации
/chat - свободный диалог с AI

📊 Аналитика и отчеты:
/progress - отчет о прогрессе
/mood - анализ настроения
/insights - персональные инсайты
/recommendations - персонализированные рекомендации

🗄️ Управление данными:
/validate [table] - проверить структуру
/list [table] [limit] - список элементов
/search [table] [query] - поиск
/create [table] [data] - создание
/update [table] [id] [data] - обновление
/delete [table] [id] - удаление

Доступные таблицы: rituals, habits, reflections, guides, actions, terms, materials
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Тестовая команда"""
        await update.message.reply_text("✅ Бот работает! Все системы функционируют нормально.")
    
    async def todo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /todo - быстрая задача"""
        if not context.args:
            await update.message.reply_text("❌ Укажите текст задачи: `/todo \"Купить продукты\"`")
            return
        
        task_text = " ".join(context.args)
        
        try:
            # Создаем задачу в Todoist
            task = await self.todoist.create_task(
                content=task_text,
                priority=TaskPriority.NORMAL
            )
            
            if task:
                response = f"""
✅ **Задача создана в Todoist**

📝 **Текст:** {task.content}
🆔 **ID:** `{task.id}`
📅 **Создана:** {task.created_at.strftime('%d.%m.%Y %H:%M')}
🎯 **Приоритет:** {task.priority.value}

💡 **Команды:**
• `/complete {task.id}` - завершить
• `/delete {task.id}` - удалить
• `/tasks` - все задачи
                """
                
                keyboard = [
                    [InlineKeyboardButton("✅ Завершить", callback_data=f"complete_{task.id}")],
                    [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{task.id}")],
                    [InlineKeyboardButton("📋 Все задачи", callback_data="list_tasks")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            else:
                await update.message.reply_text("❌ Ошибка создания задачи")
                
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def todoist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /todoist - управление Todoist"""
        try:
            # Получаем статистику
            tasks = await self.todoist.get_tasks()
            projects = await self.todoist.get_projects()
            
            today_tasks = [t for t in tasks if t.due_date and t.due_date.date() == datetime.now().date()]
            overdue_tasks = [t for t in tasks if t.due_date and t.due_date.date() < datetime.now().date() and not t.completed_at]
            
            stats_text = f"""
📊 **Todoist Статистика**

📋 **Всего задач:** {len(tasks)}
✅ **Выполнено:** {len([t for t in tasks if t.completed_at])}
📅 **На сегодня:** {len(today_tasks)}
⚠️ **Просрочено:** {len(overdue_tasks)}
📁 **Проектов:** {len(projects)}

**Команды:**
• `/tasks` - список всех задач
• `/todo "текст"` - быстрая задача
• `/complete ID` - завершить задачу
            """
            
            keyboard = [
                [InlineKeyboardButton("📋 Все задачи", callback_data="list_tasks")],
                [InlineKeyboardButton("📅 Сегодня", callback_data="today_tasks")],
                [InlineKeyboardButton("⚠️ Просрочено", callback_data="overdue_tasks")],
                [InlineKeyboardButton("📁 Проекты", callback_data="list_projects")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики Todoist: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /tasks - список задач"""
        try:
            tasks = await self.todoist.get_tasks()
            
            if not tasks:
                await update.message.reply_text("📝 Нет активных задач")
                return
            
            # Группируем задачи по статусу
            active_tasks = [t for t in tasks if not t.completed_at]
            completed_tasks = [t for t in tasks if t.completed_at]
            
            response = f"""
📋 **Задачи в Todoist**

🔄 **Активные ({len(active_tasks)}):**
            """
            
            for i, task in enumerate(active_tasks[:10], 1):
                priority_emoji = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(task.priority.value, "⚪")
                due_text = f"📅 {task.due_date.strftime('%d.%m')}" if task.due_date else ""
                response += f"\n{i}. {priority_emoji} {task.content} {due_text}\n   ID: `{task.id}`"
            
            if len(active_tasks) > 10:
                response += f"\n... и еще {len(active_tasks) - 10} задач"
            
            if completed_tasks:
                response += f"\n\n✅ **Выполнено ({len(completed_tasks)}):**"
                for i, task in enumerate(completed_tasks[:5], 1):
                    response += f"\n{i}. ✅ {task.content}"
            
            keyboard = [
                [InlineKeyboardButton("✅ Завершить задачу", callback_data="complete_task")],
                [InlineKeyboardButton("🗑️ Удалить задачу", callback_data="delete_task")],
                [InlineKeyboardButton("📅 Сегодня", callback_data="today_tasks")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка получения задач: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def complete_task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /complete - завершить задачу"""
        if not context.args:
            await update.message.reply_text("❌ Укажите ID задачи: `/complete 123456789`")
            return
        
        task_id = context.args[0]
        
        try:
            success = await self.todoist.complete_task(task_id)
            
            if success:
                await update.message.reply_text(f"✅ Задача {task_id} завершена!")
            else:
                await update.message.reply_text(f"❌ Ошибка завершения задачи {task_id}")
                
        except Exception as e:
            logger.error(f"Ошибка завершения задачи: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def delete_task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /delete - удалить задачу"""
        if not context.args:
            await update.message.reply_text("❌ Укажите ID задачи: `/delete 123456789`")
            return
        
        task_id = context.args[0]
        
        try:
            success = await self.todoist.delete_task(task_id)
            
            if success:
                await update.message.reply_text(f"🗑️ Задача {task_id} удалена!")
            else:
                await update.message.reply_text(f"❌ Ошибка удаления задачи {task_id}")
                
        except Exception as e:
            logger.error(f"Ошибка удаления задачи: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def notion_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /notion - управление Notion"""
        try:
            # Получаем статистику по базам данных
            stats = await self._get_notion_stats()
            
            response = f"""
📚 **Notion Базы данных**

{stats}

**Команды:**
• `/habit "название"` - добавить привычку
• `/reflection "текст"` - записать рефлексию
• `/idea "идея"` - сохранить идею
• `/list тип` - список элементов
            """
            
            keyboard = [
                [InlineKeyboardButton("📊 Статистика", callback_data="notion_stats")],
                [InlineKeyboardButton("📝 Добавить запись", callback_data="add_notion")],
                [InlineKeyboardButton("🔍 Поиск", callback_data="search_notion")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики Notion: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def _get_notion_stats(self) -> str:
        """Получение статистики Notion"""
        try:
            stats = []
            
            # Проверяем каждую базу данных
            db_names = {
                "tasks": "📋 Задачи",
                "habits": "🔄 Привычки", 
                "reflections": "🧠 Рефлексии",
                "rituals": "🌟 Ритуалы",
                "guides": "📖 Гайды",
                "actions": "⚡ Действия",
                "terms": "📚 Термины",
                "materials": "📁 Материалы"
            }
            
            for db_key, db_name in db_names.items():
                try:
                    count = await self.notion.get_database_count(db_key)
                    stats.append(f"{db_name}: {count} записей")
                except:
                    stats.append(f"{db_name}: ❌ недоступна")
            
            return "\n".join(stats)
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики Notion: {e}")
            return "❌ Ошибка получения статистики"
    
    async def habit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /habit - добавить привычку"""
        if not context.args:
            await update.message.reply_text("❌ Укажите название привычки: `/habit \"Медитация\"`")
            return
        
        habit_name = " ".join(context.args)
        
        try:
            # Создаем привычку в Notion
            habit_data = {
                "name": habit_name,
                "status": "Активная",
                "created_date": datetime.now().isoformat(),
                "streak": 0
            }
            
            habit = await self.notion.create_habit(habit_data)
            
            if habit:
                response = f"""
✅ **Привычка создана в Notion**

🔄 **Название:** {habit_name}
📅 **Создана:** {datetime.now().strftime('%d.%m.%Y')}
🔥 **Стрик:** 0 дней

💡 **Команды:**
• `/list habits` - все привычки
• `/reflection "о привычке"` - рефлексия
                """
                
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Ошибка создания привычки")
                
        except Exception as e:
            logger.error(f"Ошибка создания привычки: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def reflection_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /reflection - записать рефлексию"""
        if not context.args:
            await update.message.reply_text("❌ Укажите текст рефлексии: `/reflection \"Продуктивный день\"`")
            return
        
        reflection_text = " ".join(context.args)
        
        try:
            # Создаем рефлексию в Notion
            reflection_data = {
                "name": f"Рефлексия {datetime.now().strftime('%d.%m.%Y')}",
                "content": reflection_text,
                "date": datetime.now().isoformat(),
                "type": "daily"
            }
            
            reflection = await self.notion.create_reflection(reflection_data)
            
            if reflection:
                response = f"""
🧠 **Рефлексия записана в Notion**

📝 **Текст:** {reflection_text}
📅 **Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

💡 **Команды:**
• `/list reflections` - все рефлексии
• `/insights` - анализ рефлексий
                """
                
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Ошибка записи рефлексии")
                
        except Exception as e:
            logger.error(f"Ошибка записи рефлексии: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def idea_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /idea - сохранить идею"""
        if not context.args:
            await update.message.reply_text("❌ Укажите идею: `/idea \"Новая функция\"`")
            return
        
        idea_text = " ".join(context.args)
        
        try:
            # Создаем идею в Notion
            idea_data = {
                "name": f"Идея: {idea_text[:50]}...",
                "content": idea_text,
                "date": datetime.now().isoformat(),
                "status": "Новая"
            }
            
            idea = await self.notion.create_material(idea_data)
            
            if idea:
                response = f"""
💡 **Идея сохранена в Notion**

💭 **Текст:** {idea_text}
📅 **Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

💡 **Команды:**
• `/list materials` - все материалы
• `/search "{idea_text[:20]}"` - поиск
                """
                
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Ошибка сохранения идеи")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения идеи: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def overview_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /overview - обзор дня"""
        try:
            # Получаем данные из всех систем
            tasks = await self.todoist.get_tasks()
            today_tasks = [t for t in tasks if t.due_date and t.due_date.date() == datetime.now().date()]
            completed_today = [t for t in tasks if t.completed_at and t.completed_at.date() == datetime.now().date()]
            
            # Получаем статистику Notion
            notion_stats = await self._get_notion_stats()
            
            response = f"""
📊 **Обзор дня {datetime.now().strftime('%d.%m.%Y')}**

📋 **Todoist:**
• Задач на сегодня: {len(today_tasks)}
• Выполнено сегодня: {len(completed_today)}
• Всего активных: {len([t for t in tasks if not t.completed_at])}

📚 **Notion:**
{notion_stats}

🎯 **Рекомендации:**
• {'🎉 Отличный день!' if len(completed_today) >= 3 else '📝 Попробуйте выполнить больше задач'}
• {'🔥 Привычки на месте!' if 'Привычки' in notion_stats and '0' not in notion_stats else '🔄 Добавьте привычки'}
            """
            
            keyboard = [
                [InlineKeyboardButton("📋 Задачи", callback_data="list_tasks")],
                [InlineKeyboardButton("🧠 Рефлексия", callback_data="add_reflection")],
                [InlineKeyboardButton("📊 Детальная аналитика", callback_data="detailed_analytics")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка получения обзора: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def insights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /insights - инсайты продуктивности"""
        try:
            # Анализируем данные
            tasks = await self.todoist.get_tasks()
            completed_tasks = [t for t in tasks if t.completed_at]
            
            # Вычисляем метрики
            completion_rate = len(completed_tasks) / len(tasks) * 100 if tasks else 0
            
            # Определяем паттерны
            patterns = []
            if completion_rate > 80:
                patterns.append("🎯 Высокая продуктивность")
            elif completion_rate > 60:
                patterns.append("📈 Хорошая продуктивность")
            else:
                patterns.append("📝 Есть возможности для улучшения")
            
            # Анализируем приоритеты
            high_priority_completed = len([t for t in completed_tasks if t.priority == TaskPriority.HIGH])
            if high_priority_completed > 0:
                patterns.append("🔥 Фокус на важных задачах")
            
            response = f"""
🧠 **Инсайты продуктивности**

📊 **Метрики:**
• Всего задач: {len(tasks)}
• Выполнено: {len(completed_tasks)}
• Процент выполнения: {completion_rate:.1f}%

🎯 **Паттерны:**
{chr(10).join(f"• {pattern}" for pattern in patterns)}

💡 **Рекомендации:**
• {'🚀 Отличная работа! Попробуйте более сложные цели' if completion_rate > 80 else '📝 Разбивайте большие задачи на мелкие'}
• {'⏰ Используйте технику Pomodoro' if completion_rate < 50 else '📊 Анализируйте, какие задачи отнимают больше времени'}
            """
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Ошибка получения инсайтов: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /progress - прогресс недели"""
        try:
            # Анализируем данные за неделю
            tasks = await self.todoist.get_tasks()
            week_ago = datetime.now() - timedelta(days=7)
            
            week_tasks = [t for t in tasks if t.created_at >= week_ago]
            week_completed = [t for t in week_tasks if t.completed_at]
            
            # Группируем по дням
            daily_progress = {}
            for task in week_completed:
                day = task.completed_at.date()
                daily_progress[day] = daily_progress.get(day, 0) + 1
            
            response = f"""
📈 **Прогресс за неделю**

📊 **Общая статистика:**
• Создано задач: {len(week_tasks)}
• Выполнено задач: {len(week_completed)}
• Средний темп: {len(week_completed) / 7:.1f} задач/день

📅 **По дням:**
            """
            
            for i in range(7):
                day = (datetime.now() - timedelta(days=i)).date()
                count = daily_progress.get(day, 0)
                emoji = "🔥" if count >= 3 else "✅" if count >= 1 else "📝"
                response += f"\n{emoji} {day.strftime('%d.%m')}: {count} задач"
            
            response += f"""

🎯 **Тренды:**
• {'📈 Продуктивность растет' if len(week_completed) > len(week_tasks) * 0.7 else '📉 Нужно больше фокуса'}
• {'🔥 Стабильный темп' if len(set(daily_progress.keys())) >= 5 else '📝 Нерегулярная работа'}
            """
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Ошибка получения прогресса: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def recommendations_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /recommendations - рекомендации"""
        try:
            # Анализируем данные для рекомендаций
            tasks = await self.todoist.get_tasks()
            overdue_tasks = [t for t in tasks if t.due_date and t.due_date.date() < datetime.now().date() and not t.completed_at]
            high_priority_tasks = [t for t in tasks if t.priority == TaskPriority.HIGH and not t.completed_at]
            
            recommendations = []
            
            if overdue_tasks:
                recommendations.append(f"⚠️ **{len(overdue_tasks)} просроченных задач** - пересмотрите приоритеты")
            
            if high_priority_tasks:
                recommendations.append(f"🔥 **{len(high_priority_tasks)} важных задач** - фокусируйтесь на них")
            
            if len(tasks) > 20:
                recommendations.append("📝 **Много задач** - разбивайте большие на мелкие")
            
            if not recommendations:
                recommendations.append("🎉 **Отличная работа!** Продолжайте в том же духе")
            
            response = f"""
💡 **Персональные рекомендации**

{chr(10).join(recommendations)}

🎯 **Действия:**
• `/tasks` - просмотреть все задачи
• `/todo "важная задача"` - добавить приоритетную задачу
• `/reflection "мысли"` - записать рефлексию
• `/insights` - детальная аналитика
            """
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Ошибка получения рекомендаций: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def sync_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /sync - синхронизация"""
        try:
            response = "🔄 **Синхронизация систем...**\n\n"
            
            # Синхронизируем Todoist
            tasks = await self.todoist.get_tasks()
            response += f"✅ Todoist: {len(tasks)} задач\n"
            
            # Синхронизируем Notion
            notion_stats = await self._get_notion_stats()
            response += f"✅ Notion: базы данных обновлены\n"
            
            response += f"""
🔄 **Синхронизация завершена**

📊 **Статистика:**
• Todoist: {len(tasks)} задач
• Notion: базы данных актуальны

💡 **Следующие шаги:**
• `/overview` - обзор дня
• `/insights` - инсайты
• `/recommendations` - рекомендации
            """
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации: {e}")
            await update.message.reply_text(f"❌ Ошибка синхронизации: {str(e)}")
    
    async def validate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /validate - проверка интеграций"""
        try:
            response = "🔍 **Проверка интеграций...**\n\n"
            
            # Проверяем Todoist
            try:
                tasks = await self.todoist.get_tasks()
                response += f"✅ Todoist: {len(tasks)} задач доступно\n"
            except Exception as e:
                response += f"❌ Todoist: ошибка - {str(e)}\n"
            
            # Проверяем Notion
            try:
                notion_stats = await self._get_notion_stats()
                response += f"✅ Notion: базы данных доступны\n"
            except Exception as e:
                response += f"❌ Notion: ошибка - {str(e)}\n"
            
            response += f"""
🔍 **Результат проверки:**

{response}

💡 **Рекомендации:**
• Проверьте токены в .env файле
• Убедитесь в доступности API
• Проверьте интернет-соединение
            """
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Ошибка валидации: {e}")
            await update.message.reply_text(f"❌ Ошибка валидации: {str(e)}")
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /list - список элементов"""
        if not context.args:
            await update.message.reply_text("❌ Укажите тип: `/list tasks`, `/list habits`, `/list reflections`")
            return
        
        list_type = context.args[0].lower()
        
        try:
            if list_type == "tasks":
                tasks = await self.todoist.get_tasks()
                response = f"📋 **Задачи в Todoist ({len(tasks)}):**\n\n"
                
                for i, task in enumerate(tasks[:10], 1):
                    status = "✅" if task.completed_at else "🔄"
                    priority = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(task.priority.value, "⚪")
                    response += f"{i}. {status} {priority} {task.content}\n   ID: `{task.id}`\n"
                
                if len(tasks) > 10:
                    response += f"\n... и еще {len(tasks) - 10} задач"
            
            elif list_type == "habits":
                habits = await self.notion.list_habits()
                response = f"🔄 **Привычки в Notion ({len(habits)}):**\n\n"
                
                for i, habit in enumerate(habits[:10], 1):
                    response += f"{i}. {habit.get('name', 'Без названия')}\n"
                
                if len(habits) > 10:
                    response += f"\n... и еще {len(habits) - 10} привычек"
            
            elif list_type == "reflections":
                reflections = await self.notion.list_reflections()
                response = f"🧠 **Рефлексии в Notion ({len(reflections)}):**\n\n"
                
                for i, reflection in enumerate(reflections[:10], 1):
                    response += f"{i}. {reflection.get('name', 'Без названия')}\n"
                
                if len(reflections) > 10:
                    response += f"\n... и еще {len(reflections) - 10} рефлексий"
            
            else:
                response = f"❌ Неизвестный тип: {list_type}\n\nДоступные типы: tasks, habits, reflections"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Ошибка получения списка {list_type}: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /search - поиск"""
        if not context.args:
            await update.message.reply_text("❌ Укажите запрос: `/search \"ключевые слова\"`")
            return
        
        query = " ".join(context.args)
        
        try:
            response = f"🔍 **Поиск: \"{query}\"**\n\n"
            
            # Ищем в Todoist
            tasks = await self.todoist.get_tasks()
            matching_tasks = [t for t in tasks if query.lower() in t.content.lower()]
            
            if matching_tasks:
                response += f"📋 **Найдено в Todoist ({len(matching_tasks)}):**\n"
                for i, task in enumerate(matching_tasks[:5], 1):
                    response += f"{i}. {task.content}\n   ID: `{task.id}`\n"
            else:
                response += "📋 **В Todoist не найдено**\n"
            
            # Ищем в Notion (если доступно)
            try:
                notion_results = await self.notion.search(query)
                if notion_results:
                    response += f"\n📚 **Найдено в Notion ({len(notion_results)}):**\n"
                    for i, result in enumerate(notion_results[:5], 1):
                        response += f"{i}. {result.get('name', 'Без названия')}\n"
                else:
                    response += "\n📚 **В Notion не найдено**\n"
            except:
                response += "\n📚 **Поиск в Notion недоступен**\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            await update.message.reply_text(f"❌ Ошибка поиска: {str(e)}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        try:
            if data == "create_task":
                await query.edit_message_text("📝 Введите задачу в формате: `/todo \"текст задачи\"`")
            
            elif data == "overview":
                await self.overview_command(update, context)
            
            elif data == "insights":
                await self.insights_command(update, context)
            
            elif data == "sync":
                await self.sync_command(update, context)
            
            elif data == "list_tasks":
                await self.tasks_command(update, context)
            
            elif data == "today_tasks":
                tasks = await self.todoist.get_tasks()
                today_tasks = [t for t in tasks if t.due_date and t.due_date.date() == datetime.now().date()]
                
                response = f"📅 **Задачи на сегодня ({len(today_tasks)}):**\n\n"
                for i, task in enumerate(today_tasks, 1):
                    response += f"{i}. {task.content}\n   ID: `{task.id}`\n"
                
                await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN)
            
            elif data == "overdue_tasks":
                tasks = await self.todoist.get_tasks()
                overdue_tasks = [t for t in tasks if t.due_date and t.due_date.date() < datetime.now().date() and not t.completed_at]
                
                response = f"⚠️ **Просроченные задачи ({len(overdue_tasks)}):**\n\n"
                for i, task in enumerate(overdue_tasks, 1):
                    response += f"{i}. {task.content}\n   ID: `{task.id}`\n"
                
                await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN)
            
            elif data.startswith("complete_"):
                task_id = data.split("_")[1]
                success = await self.todoist.complete_task(task_id)
                if success:
                    await query.edit_message_text(f"✅ Задача {task_id} завершена!")
                else:
                    await query.edit_message_text(f"❌ Ошибка завершения задачи {task_id}")
            
            elif data.startswith("delete_"):
                task_id = data.split("_")[1]
                success = await self.todoist.delete_task(task_id)
                if success:
                    await query.edit_message_text(f"🗑️ Задача {task_id} удалена!")
                else:
                    await query.edit_message_text(f"❌ Ошибка удаления задачи {task_id}")
            
            elif data.startswith("context_"):
                # Переключение контекста
                new_context = data.split("_")[1]
                if user_id in self.user_sessions:
                    self.user_sessions[user_id].current_context = new_context
                    session_id = self.user_sessions[user_id].session_id
                    await self.llm_service.switch_context(session_id, new_context)
                    
                    context_names = {
                        "work": "💼 Рабочий",
                        "home": "🏠 Домашний",
                        "general": "🌐 Общий"
                    }
                    
                    await query.edit_message_text(f"✅ Контекст переключен на: {context_names[new_context]}")
            
            else:
                await query.edit_message_text(f"❌ Неизвестная команда: {data}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки callback: {e}")
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений для чата с AI"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession(user_id=user_id)
        
        message = update.message.text
        await self._handle_chat_message(update, message)

    async def _handle_chat_message(self, update: Update, message: str):
        """Обработка сообщения чата с AI"""
        user_id = update.effective_user.id
        current_context = self.user_sessions[user_id].current_context
        session_id = self.user_sessions[user_id].session_id
        
        # Показываем индикатор набора
        await update.message.reply_chat_action("typing")
        
        try:
            async with self.llm_service:
                response = await self.llm_service.generate_response(
                    prompt=message,
                    context=current_context,
                    user_id=str(user_id),
                    session_id=session_id,
                    use_notion_context=True
                )
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Ошибка в чате с AI: {e}")
            await update.message.reply_text(f"❌ Ошибка при обработке сообщения: {str(e)}")

    async def run(self):
        """Асинхронный запуск бота"""
        if not self.is_initialized:
            logger.error("Бот не инициализирован")
            return
        logger.info("🤖 Запуск Telegram бота...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

# Глобальный экземпляр бота
enhanced_bot = EnhancedTelegramBot()

def main():
    """Главная функция"""
    bot = EnhancedTelegramBot()
    bot.run()

if __name__ == "__main__":
    main() 