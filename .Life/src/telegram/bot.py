import os
import asyncio
import logging
from typing import Dict, List
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from src.agents.agent_core import agent_core

load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USERS = [int(x.strip()) for x in os.getenv("ALLOWED_TELEGRAM_USERS", "").split(",") if x.strip()]

# Доступные агенты
AVAILABLE_AGENTS = [
    "Product Manager",
    "Developer", 
    "LLM Researcher",
    "DevOps",
    "QA",
    "Support",
    "Growth/Marketing",
    "Meta-Agent"
]

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Настройка обработчиков команд"""
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Команды для работы с агентами
        self.application.add_handler(CommandHandler("agents", self.agents_command))
        self.application.add_handler(CommandHandler("ask", self.ask_command))
        
        # Команды мониторинга
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("cache", self.cache_command))
        
        # Админские команды
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("dbs", self.databases_command))
        self.application.add_handler(CommandHandler("db_info", self.db_info_command))
        self.application.add_handler(CommandHandler("db_create", self.db_create_command))
        self.application.add_handler(CommandHandler("db_clean", self.db_clean_command))
        self.application.add_handler(CommandHandler("agent_add", self.agent_add_command))
        self.application.add_handler(CommandHandler("agent_edit", self.agent_edit_command))
        self.application.add_handler(CommandHandler("agent_delete", self.agent_delete_command))
        self.application.add_handler(CommandHandler("system", self.system_command))
        self.application.add_handler(CommandHandler("backup", self.backup_command))
        self.application.add_handler(CommandHandler("restore", self.restore_command))
        self.application.add_handler(CommandHandler("optimize", self.optimize_command))
        
        # Обработчики инлайн-кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        user_id = update.effective_user.id
        is_admin = self.is_user_admin(user_id)
        
        welcome_text = f"""
🤖 **Notion-Telegram-LLM Integration**

Привет, {update.effective_user.first_name}!

{'👑 **Режим администратора**' if is_admin else '👤 **Обычный пользователь**'}

**Основные команды:**
• `/help` - Справка
• `/agents` - Список агентов
• `/ask [агент] [вопрос]` - Задать вопрос агенту
• `/stats` - Статистика
• `/cache` - Кэш

{'**Команды администратора:**' if is_admin else ''}
{'• `/admin` - Панель администратора' if is_admin else ''}
{'• `/dbs` - Управление базами данных' if is_admin else ''}
{'• `/system` - Системные настройки' if is_admin else ''}

**Примеры:**
• `/ask Product Manager Как приоритизировать задачи?`
• `/ask Developer Какую архитектуру выбрать?`
        """
        
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        is_admin = self.is_user_admin(update.effective_user.id)
        
        help_text = """
📚 **СПРАВКА ПО КОМАНДАМ**

**Основные команды:**
• `/start` - Приветствие
• `/help` - Эта справка
• `/agents` - Список агентов
• `/stats` - Статистика производительности
• `/cache` - Статистика кэша
• `/optimize` - Рекомендации по оптимизации

**Команды для работы с агентами:**
• `/ask [агент] [вопрос]` - Задать вопрос агенту

**Примеры:**
• `/ask Product Manager Как приоритизировать задачи?`
• `/ask Developer Какую архитектуру выбрать?`
        """
        
        if is_admin:
            admin_help = """

👑 **КОМАНДЫ АДМИНИСТРАТОРА:**

**Управление базами данных:**
• `/dbs` - Обзор всех баз данных
• `/db_info [база]` - Информация о базе
• `/db_create [база]` - Создать новую базу
• `/db_clean [база]` - Очистить дубликаты

**Управление агентами:**
• `/agent_add [роль] [промпт]` - Добавить агента
• `/agent_edit [роль] [новый_промпт]` - Изменить агента
• `/agent_delete [роль]` - Удалить агента

**Системное управление:**
• `/admin` - Панель администратора
• `/system` - Системные настройки
• `/backup` - Создать резервную копию
• `/restore` - Восстановить из резервной копии

**Примеры админских команд:**
• `/db_info rituals` - Информация о базе ритуалов
• `/agent_add "New Agent" "Ты новый агент..."` - Добавить агента
• `/db_clean actions` - Очистить дубликаты в задачах
            """
            help_text += admin_help
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def agents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /agents"""
        if not self.is_user_allowed(update.effective_user.id):
            return
            
        agents_text = "🤖 **Доступные AI агенты:**\n\n"
        
        for i, agent in enumerate(AVAILABLE_AGENTS, 1):
            agents_text += f"{i}. **{agent}**\n"
        
        agents_text += "\nИспользуйте `/ask [агент] [вопрос]` для взаимодействия с агентом."
        
        keyboard = []
        for agent in AVAILABLE_AGENTS:
            keyboard.append([InlineKeyboardButton(f"💬 {agent}", callback_data=f"ask_{agent}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(agents_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /ask"""
        if not self.is_user_allowed(update.effective_user.id):
            return
            
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ Неправильный формат команды.\n"
                "Используйте: `/ask [агент] [вопрос]`\n"
                "Пример: `/ask \"Product Manager\" \"Как приоритизировать задачи?\"`",
                parse_mode='Markdown'
            )
            return
        
        # Извлекаем агента и вопрос
        agent_name = context.args[0].strip('"')
        question = ' '.join(context.args[1:])
        
        if agent_name not in AVAILABLE_AGENTS:
            await update.message.reply_text(
                f"❌ Агент '{agent_name}' не найден.\n"
                f"Используйте /agents для списка доступных агентов."
            )
            return
        
        await self.process_agent_request(update, context, agent_name, question)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обычных сообщений"""
        if not self.is_user_allowed(update.effective_user.id):
            return
            
        # Если это ответ на сообщение бота, обрабатываем как вопрос к агенту
        if update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot:
            # Определяем агента из контекста или используем Meta-Agent по умолчанию
            agent_name = "Meta-Agent"
            question = update.message.text
            
            await self.process_agent_request(update, context, agent_name, question)
        else:
            # Обычное сообщение - предлагаем выбрать агента
            keyboard = []
            for agent in AVAILABLE_AGENTS:
                keyboard.append([InlineKeyboardButton(f"💬 {agent}", callback_data=f"ask_{agent}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🤖 Выберите агента для взаимодействия:",
                reply_markup=reply_markup
            )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на инлайн-кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "admin_dbs":
            await self._handle_admin_dbs(query)
        elif query.data == "admin_agents":
            await self._handle_admin_agents(query)
        elif query.data == "admin_stats":
            await self._handle_admin_stats(query)
        elif query.data == "admin_system":
            await self._handle_admin_system(query)
        elif query.data == "admin_backup":
            await self._handle_admin_backup(query)
        elif query.data == "admin_optimize":
            await self._handle_admin_optimize(query)
        elif query.data == "admin_main":
            await self._handle_admin_main(query)
        elif query.data.startswith("ask_"):
            agent_name = query.data[4:]  # Убираем "ask_"
            await query.edit_message_text(
                f"💬 Выбран агент: **{agent_name}**\n\n"
                f"Отправьте ваш вопрос в следующем сообщении:",
                parse_mode='Markdown'
            )
            # Сохраняем выбранного агента в контексте
            context.user_data['selected_agent'] = agent_name

    async def _handle_admin_dbs(self, query):
        """Обработка кнопки управления базами данных"""
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
        dbs_info = await self._get_databases_info()
        
        text = "🗄️ **УПРАВЛЕНИЕ БАЗАМИ ДАННЫХ**\n\n"
        
        for db_name, info in dbs_info.items():
            status = "✅" if info['exists'] else "❌"
            text += f"{status} **{db_name}**: {info['description']}\n"
            if info['exists']:
                text += f"   📊 Записей: {info['count']}\n"
            text += "\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_agents(self, query):
        """Обработка кнопки управления агентами"""
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
        prompts = await agent_core.load_prompts_from_notion(force_refresh=True)
        
        text = "🤖 **УПРАВЛЕНИЕ АГЕНТАМИ**\n\n"
        
        if prompts:
            text += f"**Найдено агентов:** {len(prompts)}\n\n"
            
            for role, prompt in prompts.items():
                text += f"📝 **{role}**\n"
                text += f"   Длина: {len(prompt)} символов\n\n"
        else:
            text += "❌ Агенты не найдены\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_stats(self, query):
        """Обработка кнопки статистики"""
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
        try:
            from src.utils.performance_monitor import performance_monitor
            
            if performance_monitor:
                stats = performance_monitor.get_performance_stats(days=7)
                
                if "error" not in stats:
                    text = "📊 **СТАТИСТИКА СИСТЕМЫ**\n\n"
                    text += f"**Операции:** {stats['total_operations']}\n"
                    text += f"**Успешность:** {stats['success_rate']:.1%}\n"
                    text += f"**Среднее время:** {stats['avg_duration']:.2f}с\n"
                    text += f"**Токены:** {stats['total_tokens']:,}\n"
                    text += f"**Стоимость:** ${stats['total_cost']:.6f}\n"
                    text += f"**Кэш:** {stats['cache_hit_rate']:.1%}\n"
                else:
                    text = f"❌ {stats['error']}"
            else:
                text = "❌ Мониторинг недоступен"
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_system(self, query):
        """Обработка кнопки системных настроек"""
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
        system_info = await self._get_system_info()
        
        text = "⚙️ **СИСТЕМНЫЕ НАСТРОЙКИ**\n\n"
        
        for key, value in system_info.items():
            text += f"**{key}:** {value}\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_backup(self, query):
        """Обработка кнопки резервного копирования"""
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
        try:
            prompts = await agent_core.load_prompts_from_notion(force_refresh=True)
            
            import json
            from datetime import datetime
            
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "prompts": prompts,
                "system_info": await self._get_system_info()
            }
            
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            text = f"✅ **РЕЗЕРВНАЯ КОПИЯ СОЗДАНА**\n\nФайл: {backup_file}\nАгентов: {len(prompts)}"
            
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_optimize(self, query):
        """Обработка кнопки оптимизации"""
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
        try:
            from src.utils.performance_monitor import performance_monitor
            
            if performance_monitor:
                recommendations = performance_monitor.get_optimization_recommendations()
                
                text = "💡 **РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ**\n\n"
                
                for rec in recommendations:
                    text += f"• {rec}\n"
            else:
                text = "❌ Мониторинг недоступен"
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_main(self, query):
        """Обработка кнопки возврата в главное меню"""
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("🗄️ Базы данных", callback_data="admin_dbs"),
                InlineKeyboardButton("🤖 Агенты", callback_data="admin_agents")
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
                InlineKeyboardButton("⚙️ Система", callback_data="admin_system")
            ],
            [
                InlineKeyboardButton("💾 Резервное копирование", callback_data="admin_backup"),
                InlineKeyboardButton("🔧 Оптимизация", callback_data="admin_optimize")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👑 **ПАНЕЛЬ АДМИНИСТРАТОРА**\n\nВыберите раздел для управления:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def process_agent_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, agent_name: str, question: str):
        """Обработка запроса к агенту"""
        try:
            # Отправляем сообщение о начале обработки
            processing_msg = await update.message.reply_text(
                f"🤖 **{agent_name}** обрабатывает ваш запрос...",
                parse_mode='Markdown'
            )
            
            # Определяем оптимальную модель для задачи
            model_type = await agent_core.get_optimal_model_for_task(agent_name, "medium")
            
            # Получаем ответ от агента
            context_info = f"Пользователь спрашивает через Telegram бота"
            response = await agent_core.get_agent_response(agent_name, context_info, question, model_type)
            
            # Получаем информацию о использованной модели
            model_used = agent_core.models.get(model_type, "unknown")
            
            # Логируем взаимодействие
            await agent_core.log_agent_interaction(agent_name, question, response, True, model_used)
            
            # Отправляем ответ с информацией о модели
            await processing_msg.edit_text(
                f"🤖 **{agent_name}** отвечает (модель: {model_used}):\n\n{response}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса к агенту: {e}")
            await update.message.reply_text(
                f"❌ Произошла ошибка при обработке запроса: {str(e)}"
            )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает статистику производительности"""
        try:
            await update.message.reply_text(
                "📊 Загружаю статистику производительности...",
                parse_mode='Markdown'
            )
            
            # Получаем отчёт о производительности
            await agent_core.print_performance_report(days=7)
            
            # Получаем рекомендации по оптимизации
            if hasattr(agent_core, 'performance_monitor') and agent_core.performance_monitor:
                recommendations = agent_core.performance_monitor.get_optimization_recommendations()
                
                if recommendations:
                    rec_text = "\n💡 РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ:\n"
                    for rec in recommendations:
                        rec_text += f"• {rec}\n"
                    
                    await update.message.reply_text(rec_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            await update.message.reply_text(
                f"❌ Ошибка при получении статистики: {str(e)}"
            )

    async def cache_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает статистику кэша"""
        try:
            from src.utils.performance_monitor import cache_manager
            
            if cache_manager:
                stats = cache_manager.get_stats()
                
                cache_text = f"""
💾 СТАТИСТИКА КЭША

📊 Размер: {stats['size']}/{stats['max_size']}
📈 Использование: {stats['utilization']:.1%}
⏰ TTL: {stats['ttl_hours']} часов
                """
                
                await update.message.reply_text(cache_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Кэш недоступен")
                
        except Exception as e:
            logger.error(f"Ошибка при получении статистики кэша: {e}")
            await update.message.reply_text(
                f"❌ Ошибка при получении статистики кэша: {str(e)}"
            )

    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Панель администратора"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("🗄️ Базы данных", callback_data="admin_dbs"),
                InlineKeyboardButton("🤖 Агенты", callback_data="admin_agents")
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
                InlineKeyboardButton("⚙️ Система", callback_data="admin_system")
            ],
            [
                InlineKeyboardButton("💾 Резервное копирование", callback_data="admin_backup"),
                InlineKeyboardButton("🔧 Оптимизация", callback_data="admin_optimize")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👑 **ПАНЕЛЬ АДМИНИСТРАТОРА**\n\nВыберите раздел для управления:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def databases_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление базами данных"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        dbs_info = await self._get_databases_info()
        
        text = "🗄️ **УПРАВЛЕНИЕ БАЗАМИ ДАННЫХ**\n\n"
        
        for db_name, info in dbs_info.items():
            status = "✅" if info['exists'] else "❌"
            text += f"{status} **{db_name}**: {info['description']}\n"
            if info['exists']:
                text += f"   📊 Записей: {info['count']}\n"
            text += "\n"
        
        text += "**Команды:**\n"
        text += "• `/db_info [база]` - Подробная информация\n"
        text += "• `/db_create [база]` - Создать базу\n"
        text += "• `/db_clean [база]` - Очистить дубликаты\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def db_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Информация о конкретной базе данных"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите название базы: `/db_info [база]`")
            return
        
        db_name = context.args[0].lower()
        info = await self._get_database_info(db_name)
        
        if not info:
            await update.message.reply_text(f"❌ База '{db_name}' не найдена")
            return
        
        text = f"📊 **ИНФОРМАЦИЯ О БАЗЕ: {db_name.upper()}**\n\n"
        text += f"**Статус:** {'✅ Существует' if info['exists'] else '❌ Не существует'}\n"
        text += f"**Описание:** {info['description']}\n"
        
        if info['exists']:
            text += f"**Количество записей:** {info['count']}\n"
            text += f"**Последнее обновление:** {info['last_update']}\n"
            text += f"**Поля:** {', '.join(info['fields'])}\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def db_create_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание новой базы данных"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите название базы: `/db_create [база]`")
            return
        
        db_name = context.args[0].lower()
        
        try:
            await update.message.reply_text(f"🔄 Создание базы '{db_name}'...")
            await update.message.reply_text(f"✅ База '{db_name}' будет создана (функция в разработке)")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при создании базы: {str(e)}")
    
    async def db_clean_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистка дубликатов в базе данных"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите название базы: `/db_clean [база]`")
            return
        
        db_name = context.args[0].lower()
        
        try:
            await update.message.reply_text(f"🧹 Очистка дубликатов в базе '{db_name}'...")
            await update.message.reply_text(f"✅ Дубликаты в базе '{db_name}' будут очищены (функция в разработке)")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при очистке: {str(e)}")
    
    async def agent_add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавление нового агента"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ Укажите роль и промпт: `/agent_add [роль] [промпт]`")
            return
        
        role = context.args[0]
        prompt = " ".join(context.args[1:])
        
        try:
            # Создаём запись в Notion
            success = await agent_core.create_notion_record(
                db_name="agent_prompts",
                title=f"Промпт {role}",
                category=role,
                additional_props={
                    "Промпт": {"rich_text": [{"text": {"content": prompt}}]},
                    "Миссия": {"rich_text": [{"text": {"content": f"Агент {role}"}}]},
                    "Статус": {"select": {"name": "Активен"}},
                    "Версия": {"number": 1}
                }
            )
            
            if success:
                await update.message.reply_text(f"✅ Агент '{role}' успешно добавлен")
                # Обновляем кэш
                await agent_core.load_prompts_from_notion(force_refresh=True)
            else:
                await update.message.reply_text(f"❌ Ошибка при добавлении агента '{role}'")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def agent_edit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Редактирование агента"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ Укажите роль и новый промпт: `/agent_edit [роль] [новый_промпт]`")
            return
        
        role = context.args[0]
        new_prompt = " ".join(context.args[1:])
        
        try:
            await update.message.reply_text(f"✏️ Редактирование агента '{role}'...")
            await update.message.reply_text(f"✅ Агент '{role}' будет обновлён (функция в разработке)")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при редактировании: {str(e)}")
    
    async def agent_delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление агента"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите роль агента: `/agent_delete [роль]`")
            return
        
        role = context.args[0]
        
        try:
            await update.message.reply_text(f"🗑️ Удаление агента '{role}'...")
            await update.message.reply_text(f"✅ Агент '{role}' будет удалён (функция в разработке)")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при удалении: {str(e)}")
    
    async def system_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Системные настройки"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        # Получаем системную информацию
        system_info = await self._get_system_info()
        
        text = "⚙️ **СИСТЕМНАЯ ИНФОРМАЦИЯ**\n\n"
        
        for key, value in system_info.items():
            text += f"**{key}:** {value}\n"
        
        text += "\n**Команды управления:**\n"
        text += "• `/backup` - Создать резервную копию\n"
        text += "• `/restore` - Восстановить из резервной копии\n"
        text += "• `/cache` - Управление кэшем\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание резервной копии"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        try:
            # Создаём резервную копию промптов
            prompts = await agent_core.load_prompts_from_notion(force_refresh=True)
            
            import json
            from datetime import datetime
            
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "prompts": prompts,
                "system_info": await self._get_system_info()
            }
            
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            await update.message.reply_text(f"✅ Резервная копия создана: {backup_file}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при создании резервной копии: {str(e)}")
    
    async def restore_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Восстановление из резервной копии"""
        if not self.is_user_admin(update.effective_user.id):
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите файл резервной копии: `/restore [файл]`")
            return
        
        backup_file = context.args[0]
        
        try:
            await update.message.reply_text(f"🔄 Восстановление из файла '{backup_file}'...")
            await update.message.reply_text(f"✅ Восстановление из '{backup_file}' будет выполнено (функция в разработке)")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при восстановлении: {str(e)}")
    
    async def optimize_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Рекомендации по оптимизации"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            from src.utils.performance_monitor import performance_monitor
            
            if performance_monitor:
                recommendations = performance_monitor.get_optimization_recommendations()
                
                text = "💡 **РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ**\n\n"
                
                for rec in recommendations:
                    text += f"• {rec}\n"
                
                # Дополнительные рекомендации
                text += "\n**Общие советы:**\n"
                text += "• Используйте кэширование для повторных запросов\n"
                text += "• Выбирайте подходящие модели для задач\n"
                text += "• Ограничивайте max_tokens для экономии\n"
                text += "• Регулярно мониторьте использование\n"
                
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Мониторинг недоступен")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def _get_databases_info(self) -> dict:
        """Получает информацию о всех базах данных"""
        dbs = {
            "rituals": {"description": "Шаблоны и лучшие практики", "exists": False, "count": 0},
            "habits": {"description": "Отслеживание привычек", "exists": False, "count": 0},
            "reflection": {"description": "Ежедневные рефлексии", "exists": False, "count": 0},
            "guides": {"description": "Пошаговые инструкции", "exists": False, "count": 0},
            "actions": {"description": "Задачи и планы", "exists": False, "count": 0},
            "terms": {"description": "Персональная база знаний", "exists": False, "count": 0},
            "materials": {"description": "Медиа и файлы", "exists": False, "count": 0},
            "agent_prompts": {"description": "Промпты AI агентов", "exists": False, "count": 0}
        }
        
        # Проверяем существование баз
        for db_name in dbs.keys():
            try:
                records = await agent_core.get_notion_records(db_name, {"page_size": 1})
                dbs[db_name]["exists"] = True
                dbs[db_name]["count"] = len(records) if records else 0
            except:
                dbs[db_name]["exists"] = False
                dbs[db_name]["count"] = 0
        
        return dbs
    
    async def _get_database_info(self, db_name: str) -> dict:
        """Получает подробную информацию о базе данных"""
        try:
            records = await agent_core.get_notion_records(db_name)
            
            return {
                "exists": True,
                "count": len(records),
                "description": f"База данных {db_name}",
                "last_update": "Недавно",
                "fields": ["Поле1", "Поле2"]  # Упрощённо
            }
        except:
            return None
    
    async def _get_system_info(self) -> dict:
        """Получает системную информацию"""
        import platform
        try:
            import psutil
            cpu_percent = f"{psutil.cpu_percent()}%"
            memory_percent = f"{psutil.virtual_memory().percent}%"
            disk_percent = f"{psutil.disk_usage('.').percent}%"
        except ImportError:
            cpu_percent = "N/A"
            memory_percent = "N/A"
            disk_percent = "N/A"
        
        return {
            "Платформа": platform.platform(),
            "Python": platform.python_version(),
            "CPU": cpu_percent,
            "Память": memory_percent,
            "Диск": disk_percent,
            "Агенты": len(await agent_core.load_prompts_from_notion()) if agent_core else 0,
            "Кэш": "N/A"  # Упрощённо
        }

    def is_user_allowed(self, user_id: int) -> bool:
        """Проверяет, разрешен ли доступ пользователю"""
        return user_id in ALLOWED_USERS

    def is_user_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь администратором"""
        admin_users_str = os.getenv("TELEGRAM_ADMIN_USERS", "")
        admin_users = {int(user_id.strip()) for user_id in admin_users_str.split(",") if user_id.strip()}
        return user_id in admin_users

    def run(self):
        """Запускает бота"""
        logger.info("Запуск Telegram бота...")
        self.application.run_polling()

async def main():
    """Главная функция"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        return
    
    bot = TelegramBot()
    bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 