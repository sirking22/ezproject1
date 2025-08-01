#!/usr/bin/env python3
"""
🎯 ROLE-BASED MATERIALS BOT - Система логирования с ролевым доступом
Трехуровневая система: Администратор -> Менеджер -> Исполнитель
Персональная фильтрация задач по исполнителям
"""

import os
import asyncio
import logging
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from notion_client import AsyncClient
import httpx
from openai import AsyncOpenAI
from session_manager import SessionManager, UserProfile
from services.designer_report_service import DesignerReportService, WorkReport

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('role_based_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

class RoleBasedMaterialsBot:
    def __init__(self):
        """Инициализация бота"""
        # Загружаем переменные окружения
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.materials_db_id = os.getenv('MATERIALS_DB')
        self.tasks_db_id = os.getenv('NOTION_TASKS_DB_ID')
        self.subtasks_db_id = os.getenv('NOTION_SUBTASKS_DB_ID')
        
        # LLM интеграция
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.llm_client = None
        if self.deepseek_api_key:
            self.llm_client = AsyncOpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com/v1"
            )
        
        # Инициализация клиентов
        self.notion_client = None
        if self.notion_token:
            self.notion_client = AsyncClient(auth=self.notion_token)
        
        # Менеджер сессий
        self.session_manager = SessionManager()
        
        # Временные данные сессий (для material_info и т.д.)
        self.session_data = {}
        
        # Кэш задач
        self.tasks_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 минут
        
        # Статистика
        self.stats = {
            'materials_created': 0,
            'tasks_linked': 0,
            'llm_queries': 0,
            'errors': 0
        }
        
        # Интеграция с существующим сервисом отчетов
        self.report_service = DesignerReportService()
        
        logger.info(f"✅ Role-Based Bot инициализирован: Telegram={bool(self.telegram_token)}, Notion={bool(self.notion_client)}, LLM={bool(self.llm_client)}")

    def get_user_session(self, user_id: int) -> Optional[UserProfile]:
        """Получить сессию пользователя"""
        return self.session_manager.get_session(user_id)

    def create_user_session(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> UserProfile:
        """Создать новую сессию пользователя"""
        return self.session_manager.create_session(user_id, username, first_name, last_name)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        user = update.effective_user
        
        # Создаем или получаем сессию пользователя
        session = self.get_user_session(user_id)
        if not session:
            username = user.username or user.first_name or str(user_id)
            session = self.create_user_session(
                user_id=user_id,
                username=username,
                first_name=user.first_name or "",
                last_name=user.last_name or ""
            )
        
        await self.show_welcome(update, session)

    async def show_welcome(self, update: Update, session: UserProfile):
        """Показать приветственное сообщение с выбором роли"""
        keyboard = [
            [InlineKeyboardButton("👑 Администратор", callback_data="role_admin")],
            [InlineKeyboardButton("📋 Менеджер", callback_data="role_manager")],
            [InlineKeyboardButton("🛠️ Исполнитель", callback_data="role_executor")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 **Добро пожаловать в систему управления материалами!**\n\n"
            "Выберите вашу роль для начала работы:\n\n"
            "👑 **Администратор** - полный доступ ко всем функциям\n"
            "📋 **Менеджер** - управление проектами и задачами\n"
            "🛠️ **Исполнитель** - работа с конкретными задачами",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_role_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора роли"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        session = self.get_user_session(user_id)
        if not session:
            session = self.create_user_session(user_id, query.from_user.username)
        
        role = query.data.replace("role_", "")
        session.role = role
        # Обновляем активность сессии
        self.session_manager.update_session_activity(user_id)
        
        if role == UserRole.EXECUTOR:
            # Для исполнителей показываем выбор конкретного исполнителя
            await self.show_executor_selection(query)
        else:
            # Для администраторов и менеджеров сразу показываем функции
            await self.show_role_functions(query, role)

    async def show_executor_selection(self, query):
        """Показать выбор конкретного исполнителя"""
        keyboard = [
            [InlineKeyboardButton("Арсений", callback_data="executor_arseniy")],
            [InlineKeyboardButton("Маша", callback_data="executor_masha")],
            [InlineKeyboardButton("Вика", callback_data="executor_vika")],
            [InlineKeyboardButton("Аня", callback_data="executor_anya")],
            [InlineKeyboardButton("Саша", callback_data="executor_sasha")],
            [InlineKeyboardButton("Аккаунт", callback_data="executor_account")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🛠️ **Выберите исполнителя:**\n\n"
            "Выберите ваше имя для персональной фильтрации задач:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_executor_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора исполнителя"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        session = self.get_user_session(user_id)
        if not session:
            return
        
        executor = query.data.replace("executor_", "")
        session.executor = executor
        # Обновляем активность сессии
        self.session_manager.update_session_activity(user_id)
        
        # Показываем функции для исполнителя
        await self.show_role_functions(query, UserRole.EXECUTOR, executor)

    async def show_role_functions(self, query, role: str, executor: str = None):
        """Показать функции для выбранной роли"""
        role_names = {
            UserRole.ADMIN: "👑 Администратор",
            UserRole.MANAGER: "📋 Менеджер", 
            UserRole.EXECUTOR: f"🛠️ Исполнитель ({executor})" if executor else "🛠️ Исполнитель"
        }
        
        role_text = role_names.get(role, role)
        
        keyboard = [
            [InlineKeyboardButton("📁 Добавить материал", callback_data="add_material")],
            [InlineKeyboardButton("📋 Мои задачи", callback_data="my_tasks")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        
        if role in [UserRole.ADMIN, UserRole.MANAGER]:
            keyboard.append([InlineKeyboardButton("⚙️ Управление", callback_data="management")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ **Роль установлена: {role_text}**\n\n"
            "Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка всех callback запросов"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        session = self.get_user_session(user_id)
        if not session:
            await query.edit_message_text("❌ Сессия не найдена. Используйте /start")
            return
        
        session.update_activity()
        
        if query.data.startswith("role_"):
            await self.handle_role_selection(update, context)
        elif query.data.startswith("executor_"):
            await self.handle_executor_selection(update, context)
        elif query.data == "add_material":
            await self.start_add_material(query, session)
        elif query.data == "my_tasks":
            await self.show_my_tasks(query, session)
        elif query.data == "stats":
            await self.show_stats(query, session)
        elif query.data == "help":
            await self.show_help(query, session)
        elif query.data == "management":
            await self.show_management(query, session)

    async def start_add_material(self, query, session: UserProfile):
        """Начать процесс добавления материала"""
        await query.edit_message_text(
            "📁 **Добавление материала**\n\n"
            "Отправьте ссылку на Figma файл или описание материала.\n\n"
            "Примеры:\n"
            "• https://www.figma.com/file/...\n"
            "• Логотип для сайта компании\n"
            "• Обложка для социальных сетей\n\n"
            "Бот автоматически найдет связанные задачи и создаст материал.",
            parse_mode='Markdown'
        )
        
        # Устанавливаем состояние ожидания материала
        session.material_info = {"state": "waiting_material"}

    async def show_my_tasks(self, query, session: UserProfile):
        """Показать задачи пользователя"""
        try:
            tasks = await self.get_user_tasks(session)
            
            if not tasks:
                await query.edit_message_text(
                    "📋 **Ваши задачи**\n\n"
                    "У вас нет активных задач.",
                    parse_mode='Markdown'
                )
                return
            
            # Показываем первые 5 задач
            tasks_text = "📋 **Ваши активные задачи:**\n\n"
            for i, task in enumerate(tasks[:5], 1):
                status = task.get('properties', {}).get('Статус', {}).get('status', {}).get('name', 'Неизвестно')
                name = task.get('properties', {}).get('Задача', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
                tasks_text += f"{i}. **{name}** ({status})\n"
            
            if len(tasks) > 5:
                tasks_text += f"\n... и еще {len(tasks) - 5} задач"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                tasks_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка при получении задач: {e}")
            await query.edit_message_text(
                "❌ Ошибка при получении задач. Попробуйте позже.",
                parse_mode='Markdown'
            )

    async def get_user_tasks(self, session: UserProfile) -> List[Dict]:
        """Получить задачи пользователя с фильтрацией по роли"""
        try:
            if not self.notion_client:
                return []
            
            # Получаем все активные задачи
            response = await self.notion_client.databases.query(
                database_id=self.tasks_db_id,
                filter={
                    "or": [
                        {"property": "Статус", "status": {"does_not_equal": "Done"}},
                        {"property": "Статус", "status": {"does_not_equal": "Canceled"}}
                    ]
                }
            )
            
            tasks = response.get('results', [])
            
            # Фильтруем по роли и исполнителю
            if session.role == UserRole.EXECUTOR and session.executor:
                # Для исполнителей показываем только их задачи
                filtered_tasks = []
                for task in tasks:
                    participants = task.get('properties', {}).get('Участники', {}).get('people', [])
                    # Проверяем, есть ли исполнитель в участниках
                    if self.is_executor_in_task(participants, session.executor):
                        filtered_tasks.append(task)
                return filtered_tasks
            else:
                # Для администраторов и менеджеров показываем все задачи
                return tasks
                
        except Exception as e:
            logger.error(f"❌ Ошибка при получении задач: {e}")
            return []

    def is_executor_in_task(self, participants: List[Dict], executor: str) -> bool:
        """Проверить, есть ли исполнитель в участниках задачи"""
        # Маппинг имен исполнителей на возможные варианты
        executor_mapping = {
            "arseniy": ["Арсений", "arseniy", "Арс"],
            "masha": ["Маша", "masha", "Мария"],
            "vika": ["Вика", "vika", "Виктория"],
            "anya": ["Аня", "anya", "Анна"],
            "sasha": ["Саша", "sasha", "Александр"],
            "account": ["Аккаунт", "account", "Общий"]
        }
        
        executor_variants = executor_mapping.get(executor, [executor])
        
        for participant in participants:
            name = participant.get('name', '').lower()
            for variant in executor_variants:
                if variant.lower() in name:
                    return True
        return False

    async def show_stats(self, query, session: UserProfile):
        """Показать статистику"""
        stats = self.session_manager.get_statistics()
        stats_text = f"📊 **Статистика системы**\n\n"
        stats_text += f"👥 **Пользователи:**\n"
        stats_text += f"• Активных сессий: {stats['active_sessions']}\n"
        stats_text += f"• Всего сессий: {stats['total_sessions']}\n"
        stats_text += f"• Недавняя активность: {stats['recent_activity']}\n\n"
        
        stats_text += f"📁 **Материалы:**\n"
        stats_text += f"• Создано: {self.stats['materials_created']}\n"
        stats_text += f"• Связано с задачами: {self.stats['tasks_linked']}\n\n"
        
        stats_text += f"🧠 **LLM запросы:** {self.stats['llm_queries']}\n"
        stats_text += f"❌ **Ошибки:** {self.stats['errors']}\n\n"
        
        stats_text += f"👤 **Ваша роль:** {session.role}"
        if session.executor:
            stats_text += f" ({session.executor})"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_help(self, query, session: UserProfile):
        """Показать справку"""
        help_text = "❓ **Справка по использованию**\n\n"
        
        help_text += "🎯 **Основные команды:**\n"
        help_text += "• /start - Начать работу с выбором роли\n"
        help_text += "• /help - Показать эту справку\n"
        help_text += "• /stats - Статистика системы\n\n"
        
        help_text += "📁 **Добавление материалов:**\n"
        help_text += "1. Выберите 'Добавить материал'\n"
        help_text += "2. Отправьте ссылку Figma или описание\n"
        help_text += "3. Бот найдет связанные задачи\n"
        help_text += "4. Подтвердите создание материала\n\n"
        
        help_text += "👥 **Роли и доступы:**\n"
        help_text += "• **Администратор** - полный доступ\n"
        help_text += "• **Менеджер** - управление проектами\n"
        help_text += "• **Исполнитель** - персональные задачи\n\n"
        
        help_text += "🛠️ **Исполнители:** Арсений, Маша, Вика, Аня, Саша, Аккаунт"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_management(self, query, session: UserProfile):
        """Показать функции управления для админов и менеджеров"""
        keyboard = [
            [InlineKeyboardButton("👥 Управление пользователями", callback_data="manage_users")],
            [InlineKeyboardButton("📊 Аналитика", callback_data="analytics")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ **Функции управления**\n\n"
            "Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        if not session:
            await update.message.reply_text("❌ Сессия не найдена. Начните с /start")
            return
        
        text = update.message.text.strip()
        text_lower = text.lower()
        
        # Проверяем команды
        if text_lower in ['/start', 'старт']:
            await self.start_command(update, None)
        elif text_lower in ['/help', 'помощь', 'help']:
            await self.show_help_text(update, session)
        elif text_lower in ['/tasks', 'задачи', 'мои задачи']:
            await self.show_my_tasks(update, session)
        elif text_lower in ['/stats', 'статистика']:
            await self.show_stats_text(update, session)
        elif text_lower in ['/report', 'отчет']:
            await self.report_command(update, context)
        else:
            # Проверяем, не является ли это отчетом
            if await self.try_parse_report(update, session, text):
                return
            # Обрабатываем как команду
            await self.process_command(update, session, text)

    async def process_material_input(self, update: Update, session: UserProfile, text: str):
        """Обработать ввод материала"""
        try:
            # Определяем тип материала
            if "figma.com" in text.lower():
                material_type = "figma"
                material_info = {"url": text, "type": material_type}
            else:
                material_type = "description"
                material_info = {"description": text, "type": material_type}
            
            # Сохраняем данные в session_data
            user_id = update.effective_user.id
            self.session_data[user_id] = material_info
            self.session_data[user_id]["state"] = "processing"
            
            # Показываем индикатор обработки
            await update.message.reply_text(
                "🔄 **Обрабатываю материал...**\n\n"
                "Ищу связанные задачи и подготавливаю создание материала.",
                parse_mode='Markdown'
            )
            
            # Ищем связанные задачи
            related_tasks = await self.find_related_tasks(session, material_info)
            
            if related_tasks:
                await self.show_task_selection(update, session, related_tasks)
            else:
                await self.show_no_tasks_found(update, session)
                
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке материала: {e}")
            self.stats['errors'] += 1
            await update.message.reply_text(
                "❌ Ошибка при обработке материала. Попробуйте позже."
            )

    async def find_related_tasks(self, session: UserProfile, material_info: Dict) -> List[Dict]:
        """Найти связанные задачи для материала"""
        try:
            user_tasks = await self.get_user_tasks(session)
            
            if not user_tasks:
                return []
            
            # Простой поиск по ключевым словам
            keywords = self.extract_keywords(material_info)
            
            related_tasks = []
            for task in user_tasks:
                task_name = task.get('properties', {}).get('Задача', {}).get('title', [{}])[0].get('text', {}).get('content', '').lower()
                task_desc = task.get('properties', {}).get('Описание', {}).get('rich_text', [{}])[0].get('text', {}).get('content', '').lower()
                
                # Проверяем совпадение ключевых слов
                for keyword in keywords:
                    if keyword.lower() in task_name or keyword.lower() in task_desc:
                        related_tasks.append(task)
                        break
            
            return related_tasks[:5]  # Возвращаем максимум 5 задач
            
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске задач: {e}")
            return []

    def extract_keywords(self, material_info: Dict) -> List[str]:
        """Извлечь ключевые слова из материала"""
        keywords = []
        
        if material_info.get("type") == "figma":
            # Извлекаем ключевые слова из Figma URL
            url = material_info.get("url", "")
            # Простое извлечение - можно улучшить
            keywords = ["figma", "дизайн", "макет"]
        else:
            # Извлекаем ключевые слова из описания
            description = material_info.get("description", "")
            # Простое разбиение на слова
            words = re.findall(r'\b\w+\b', description.lower())
            # Фильтруем короткие слова
            keywords = [word for word in words if len(word) > 3]
        
        return keywords

    async def show_task_selection(self, update: Update, session: UserProfile, tasks: List[Dict]):
        """Показать выбор задачи для связывания"""
        keyboard = []
        
        for i, task in enumerate(tasks):
            task_name = task.get('properties', {}).get('Задача', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            status = task.get('properties', {}).get('Статус', {}).get('status', {}).get('name', 'Неизвестно')
            button_text = f"{i+1}. {task_name[:30]}... ({status})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"select_task_{i}")])
        
        keyboard.append([InlineKeyboardButton("❌ Не связывать", callback_data="no_link")])
        keyboard.append([InlineKeyboardButton("🔄 Найти еще", callback_data="find_more")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 **Найдены связанные задачи:**\n\n"
            "Выберите задачу для связывания с материалом:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_no_tasks_found(self, update: Update, session: UserProfile):
        """Показать сообщение, если задачи не найдены"""
        keyboard = [
            [InlineKeyboardButton("📝 Создать новую задачу", callback_data="create_task")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_material")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ **Связанные задачи не найдены**\n\n"
            "Хотите создать новую задачу для этого материала?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def process_command(self, update: Update, session: UserProfile, text: str):
        """Обработать команду"""
        text_lower = text.lower()
        
        if text_lower in ['/start', 'старт', 'начать']:
            await self.start_command(update, None)
        elif text_lower in ['/help', 'помощь', 'справка']:
            await self.show_help_text(update, session)
        elif text_lower in ['/stats', 'статистика']:
            await self.show_stats_text(update, session)
        else:
            await update.message.reply_text(
                "❓ Неизвестная команда. Используйте /help для справки."
            )

    async def show_help_text(self, update: Update, session: UserProfile):
        """Показать справку в текстовом виде"""
        help_text = "❓ **Справка по использованию**\n\n"
        help_text += "🎯 **Основные команды:**\n"
        help_text += "• /start - Начать работу с выбором роли\n"
        help_text += "• /help - Показать эту справку\n"
        help_text += "• /stats - Статистика системы\n\n"
        help_text += f"👤 **Ваша роль:** {session.role}"
        if session.executor:
            help_text += f" ({session.executor})"
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def show_stats_text(self, update: Update, session: UserProfile):
        """Показать статистику в текстовом виде"""
        stats = self.session_manager.get_statistics()
        stats_text = f"📊 **Статистика системы**\n\n"
        stats_text += f"👥 Активных сессий: {stats['active_sessions']}\n"
        stats_text += f"📁 Создано материалов: {self.stats['materials_created']}\n"
        stats_text += f"🧠 LLM запросов: {self.stats['llm_queries']}\n"
        stats_text += f"❌ Ошибок: {self.stats['errors']}\n\n"
        stats_text += f"👤 Ваша роль: {session.role}"
        if session.executor:
            stats_text += f" ({session.executor})"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /report"""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        if not session:
            await update.message.reply_text("❌ Сессия не найдена. Начните с /start")
            return

        # Сохраняем состояние пользователя: ожидаем отчет
        self.session_data[user_id] = {"state": "awaiting_report"}
        await update.message.reply_text(
            "📝 **Введите отчет о работе**\n\n"
            "**Форматы:**\n"
            "• `Проект Задача 2ч Описание работы`\n"
            "• `Проект - Задача - Описание 1.5ч`\n"
            "• `TASK-123 3ч done Описание https://figma.com/...`\n\n"
            "**Примеры:**\n"
            "• `Коробки мультиварки RMP04 Верстка 2ч Сделал макет упаковки`\n"
            "• `Брендинг Логотип 1.5ч Создал варианты логотипа https://figma.com/file/abc123`",
            parse_mode='Markdown'
        )

    async def try_parse_report(self, update: Update, session: UserProfile, text: str) -> bool:
        """Пытается распарсить текст как отчет"""
        try:
            # Используем существующий парсер из designer_report_service
            report = self.report_service.parse_quick_report(text)
            
            if report:
                # Устанавливаем имя дизайнера из сессии
                report.designer_name = session.username or session.first_name or "Пользователь"
                
                # Обрабатываем отчет через существующий сервис
                success, message = self.report_service.process_report(report)
                
                if success:
                    await update.message.reply_text(
                        f"✅ **Отчет успешно сохранен!**\n\n"
                        f"📋 **Проект:** {report.project_name}\n"
                        f"🎯 **Задача:** {report.task_name}\n"
                        f"⏱ **Время:** {report.time_spent_hours}ч\n"
                        f"📝 **Описание:** {report.work_description}\n\n"
                        f"💾 {message}",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        f"❌ **Ошибка обработки отчета:**\n{message}",
                        parse_mode='Markdown'
                    )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге отчета: {e}")
            return False

    def run(self):
        """Запуск бота"""
        if not self.telegram_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN не найден в .env")
            return
        
        # Создаем приложение
        application = Application.builder().token(self.telegram_token).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.show_help_text))
        application.add_handler(CommandHandler("stats", self.show_stats_text))
        application.add_handler(CommandHandler("report", self.report_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        # Запускаем бота
        logger.info("🚀 Role-Based Bot запущен")
        application.run_polling()

def main():
    """Главная функция"""
    bot = RoleBasedMaterialsBot()
    bot.run()

if __name__ == "__main__":
    main() 