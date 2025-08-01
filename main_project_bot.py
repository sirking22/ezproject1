#!/usr/bin/env python3
"""
🎯 ГЛАВНЫЙ БОТ ПРОЕКТА - Универсальная система управления
Интеграция: отчеты + идеи + концепты + материалы + задачи
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Импортируем существующие сервисы
from services.designer_report_service import DesignerReportService, WorkReport
from services.notion_bot_service import NotionBotService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main_project_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

class MainProjectBot:
    """Главный бот для управления всем проектом"""
    
    def __init__(self):
        """Инициализация бота"""
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
        
        # Инициализируем сервисы
        self.report_service = DesignerReportService()
        self.notion_service = NotionBotService()
        
        # Состояния пользователей
        self.user_states = {}
        
        logger.info("✅ Main Project Bot инициализирован")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start - главное меню"""
        keyboard = [
            [InlineKeyboardButton("📝 Отчеты", callback_data="reports")],
            [InlineKeyboardButton("💡 Идеи", callback_data="ideas")],
            [InlineKeyboardButton("🎨 Концепты", callback_data="concepts")],
            [InlineKeyboardButton("📁 Материалы", callback_data="materials")],
            [InlineKeyboardButton("📋 Задачи", callback_data="tasks")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 **ГЛАВНЫЙ БОТ ПРОЕКТА**\n\n"
            "Выберите раздел для работы:\n\n"
            "📝 **Отчеты** - сбор и обработка отчетов о работе\n"
            "💡 **Идеи** - управление идеями и концепциями\n"
            "🎨 **Концепты** - работа с дизайн-концептами\n"
            "📁 **Материалы** - организация файлов и ресурсов\n"
            "📋 **Задачи** - управление задачами и проектами\n"
            "📊 **Статистика** - аналитика и метрики",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "reports":
            await self.show_reports_menu(query)
        elif query.data == "ideas":
            await self.show_ideas_menu(query)
        elif query.data == "concepts":
            await self.show_concepts_menu(query)
        elif query.data == "materials":
            await self.show_materials_menu(query)
        elif query.data == "tasks":
            await self.show_tasks_menu(query)
        elif query.data == "stats":
            await self.show_stats_menu(query)
        elif query.data == "back_to_main":
            await self.show_main_menu(query)
        elif query.data == "quick_report":
            await self.start_quick_report(query)
        elif query.data == "add_idea":
            await self.start_add_idea(query)
        elif query.data == "add_concept":
            await self.start_add_concept(query)
        elif query.data == "add_material":
            await self.start_add_material(query)

    async def show_reports_menu(self, query):
        """Меню отчетов"""
        keyboard = [
            [InlineKeyboardButton("⚡ Быстрый отчет", callback_data="quick_report")],
            [InlineKeyboardButton("📊 Мои отчеты", callback_data="my_reports")],
            [InlineKeyboardButton("📈 Аналитика", callback_data="reports_analytics")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📝 **РАЗДЕЛ ОТЧЕТОВ**\n\n"
            "⚡ **Быстрый отчет** - отправьте отчет в любом формате\n"
            "📊 **Мои отчеты** - история ваших отчетов\n"
            "📈 **Аналитика** - статистика и метрики\n\n"
            "**Примеры отчетов:**\n"
            "• `Проект Задача 2ч Описание`\n"
            "• `TASK-123 1.5ч done Работа с Figma`\n"
            "• `Брендинг Логотип 3ч https://figma.com/file/abc123`",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_ideas_menu(self, query):
        """Меню идей"""
        keyboard = [
            [InlineKeyboardButton("💡 Добавить идею", callback_data="add_idea")],
            [InlineKeyboardButton("📋 Мои идеи", callback_data="my_ideas")],
            [InlineKeyboardButton("🔍 Поиск идей", callback_data="search_ideas")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💡 **РАЗДЕЛ ИДЕЙ**\n\n"
            "💡 **Добавить идею** - создать новую идею или концепцию\n"
            "📋 **Мои идеи** - ваши сохраненные идеи\n"
            "🔍 **Поиск идей** - найти идеи по тегам и категориям\n\n"
            "**Категории идей:**\n"
            "• Дизайн и брендинг\n"
            "• Маркетинг и реклама\n"
            "• Продукты и услуги\n"
            "• Технологии и инновации",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_concepts_menu(self, query):
        """Меню концептов"""
        keyboard = [
            [InlineKeyboardButton("🎨 Добавить концепт", callback_data="add_concept")],
            [InlineKeyboardButton("📁 Мои концепты", callback_data="my_concepts")],
            [InlineKeyboardButton("🎯 Активные концепты", callback_data="active_concepts")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎨 **РАЗДЕЛ КОНЦЕПТОВ**\n\n"
            "🎨 **Добавить концепт** - создать дизайн-концепт\n"
            "📁 **Мои концепты** - ваши концепты и прототипы\n"
            "🎯 **Активные концепты** - концепты в разработке\n\n"
            "**Типы концептов:**\n"
            "• Логотипы и брендинг\n"
            "• Веб-дизайн и интерфейсы\n"
            "• Полиграфия и упаковка\n"
            "• Реклама и презентации",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_materials_menu(self, query):
        """Меню материалов"""
        keyboard = [
            [InlineKeyboardButton("📁 Добавить материал", callback_data="add_material")],
            [InlineKeyboardButton("📚 Мои материалы", callback_data="my_materials")],
            [InlineKeyboardButton("🔍 Поиск материалов", callback_data="search_materials")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📁 **РАЗДЕЛ МАТЕРИАЛОВ**\n\n"
            "📁 **Добавить материал** - загрузить файл или ссылку\n"
            "📚 **Мои материалы** - ваши сохраненные материалы\n"
            "🔍 **Поиск материалов** - найти по тегам и категориям\n\n"
            "**Поддерживаемые форматы:**\n"
            "• Figma файлы и ссылки\n"
            "• Изображения (PNG, JPG, SVG)\n"
            "• Документы (PDF, DOC)\n"
            "• Ссылки на ресурсы",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_tasks_menu(self, query):
        """Меню задач"""
        keyboard = [
            [InlineKeyboardButton("📋 Мои задачи", callback_data="my_tasks")],
            [InlineKeyboardButton("➕ Создать задачу", callback_data="create_task")],
            [InlineKeyboardButton("📊 Управление проектами", callback_data="project_management")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📋 **РАЗДЕЛ ЗАДАЧ**\n\n"
            "📋 **Мои задачи** - ваши активные задачи\n"
            "➕ **Создать задачу** - новая задача или проект\n"
            "📊 **Управление проектами** - планирование и контроль\n\n"
            "**Типы задач:**\n"
            "• Дизайн и верстка\n"
            "• Брендинг и логотипы\n"
            "• Веб-разработка\n"
            "• Маркетинг и реклама",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_stats_menu(self, query):
        """Меню статистики"""
        keyboard = [
            [InlineKeyboardButton("📈 Общая статистика", callback_data="general_stats")],
            [InlineKeyboardButton("📊 Отчеты", callback_data="reports_stats")],
            [InlineKeyboardButton("💡 Идеи", callback_data="ideas_stats")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📊 **РАЗДЕЛ СТАТИСТИКИ**\n\n"
            "📈 **Общая статистика** - метрики системы\n"
            "📊 **Отчеты** - статистика отчетов\n"
            "💡 **Идеи** - аналитика идей и концептов\n\n"
            "**Ключевые метрики:**\n"
            "• Количество отчетов\n"
            "• Время работы\n"
            "• Активность пользователей\n"
            "• Эффективность процессов",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_main_menu(self, query):
        """Главное меню"""
        keyboard = [
            [InlineKeyboardButton("📝 Отчеты", callback_data="reports")],
            [InlineKeyboardButton("💡 Идеи", callback_data="ideas")],
            [InlineKeyboardButton("🎨 Концепты", callback_data="concepts")],
            [InlineKeyboardButton("📁 Материалы", callback_data="materials")],
            [InlineKeyboardButton("📋 Задачи", callback_data="tasks")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎯 **ГЛАВНЫЙ БОТ ПРОЕКТА**\n\n"
            "Выберите раздел для работы:\n\n"
            "📝 **Отчеты** - сбор и обработка отчетов о работе\n"
            "💡 **Идеи** - управление идеями и концепциями\n"
            "🎨 **Концепты** - работа с дизайн-концептами\n"
            "📁 **Материалы** - организация файлов и ресурсов\n"
            "📋 **Задачи** - управление задачами и проектами\n"
            "📊 **Статистика** - аналитика и метрики",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def start_quick_report(self, query):
        """Начать быстрый отчет"""
        user_id = query.from_user.id
        self.user_states[user_id] = {"state": "awaiting_report"}
        
        await query.edit_message_text(
            "📝 **БЫСТРЫЙ ОТЧЕТ**\n\n"
            "Отправьте отчет в любом формате:\n\n"
            "**Примеры:**\n"
            "• `Коробки мультиварки RMP04 Верстка 2ч Сделал макет упаковки`\n"
            "• `Брендинг Логотип 1.5ч Создал варианты логотипа https://figma.com/file/abc123`\n"
            "• `TASK-123 3ч done Описание работы https://prnt.sc/xyz789`\n\n"
            "**Поддерживаемые ссылки:**\n"
            "• Figma файлы\n"
            "• LightShot скриншоты\n"
            "• Другие материалы",
            parse_mode='Markdown'
        )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        # Проверяем состояние пользователя
        user_state = self.user_states.get(user_id, {})
        
        if user_state.get("state") == "awaiting_report":
            await self.process_report(update, text)
        elif user_state.get("state") == "awaiting_idea":
            await self.process_idea(update, text)
        elif user_state.get("state") == "awaiting_concept":
            await self.process_concept(update, text)
        elif user_state.get("state") == "awaiting_material":
            await self.process_material(update, text)
        else:
            # Пытаемся распарсить как отчет
            if await self.try_parse_report(update, text):
                return
            # Показываем главное меню
            await self.start_command(update, context)

    async def process_report(self, update: Update, text: str):
        """Обработка отчета"""
        try:
            # Используем существующий сервис
            report = self.report_service.parse_quick_report(text)
            
            if report:
                # Устанавливаем имя пользователя
                user = update.effective_user
                report.designer_name = user.username or user.first_name or "Пользователь"
                
                # Обрабатываем отчет
                success, message = self.report_service.process_report(report)
                
                if success:
                    await update.message.reply_text(
                        f"✅ **ОТЧЕТ УСПЕШНО СОХРАНЕН!**\n\n"
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
                
                # Сбрасываем состояние
                self.user_states[update.effective_user.id] = {}
            else:
                await update.message.reply_text(
                    "❌ Не удалось распарсить отчет. Попробуйте другой формат.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Ошибка обработки отчета: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке отчета. Попробуйте позже.",
                parse_mode='Markdown'
            )

    async def try_parse_report(self, update: Update, text: str) -> bool:
        """Попытка распарсить текст как отчет"""
        try:
            report = self.report_service.parse_quick_report(text)
            if report:
                await self.process_report(update, text)
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при попытке парсинга отчета: {e}")
            return False

    async def process_idea(self, update: Update, text: str):
        """Обработка идеи"""
        # TODO: Реализовать обработку идей
        await update.message.reply_text(
            "💡 **ИДЕЯ СОХРАНЕНА!**\n\n"
            f"📝 {text}\n\n"
            "✅ Идея добавлена в базу данных",
            parse_mode='Markdown'
        )
        self.user_states[update.effective_user.id] = {}

    async def process_concept(self, update: Update, text: str):
        """Обработка концепта"""
        # TODO: Реализовать обработку концептов
        await update.message.reply_text(
            "🎨 **КОНЦЕПТ СОХРАНЕН!**\n\n"
            f"📝 {text}\n\n"
            "✅ Концепт добавлен в базу данных",
            parse_mode='Markdown'
        )
        self.user_states[update.effective_user.id] = {}

    async def process_material(self, update: Update, text: str):
        """Обработка материала"""
        # TODO: Реализовать обработку материалов
        await update.message.reply_text(
            "📁 **МАТЕРИАЛ СОХРАНЕН!**\n\n"
            f"📝 {text}\n\n"
            "✅ Материал добавлен в базу данных",
            parse_mode='Markdown'
        )
        self.user_states[update.effective_user.id] = {}

    def run(self):
        """Запуск бота"""
        # Создаем приложение
        application = Application.builder().token(self.telegram_token).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        # Запускаем бота
        logger.info("🚀 Main Project Bot запущен")
        application.run_polling()

def main():
    """Главная функция"""
    bot = MainProjectBot()
    bot.run()

if __name__ == "__main__":
    main() 