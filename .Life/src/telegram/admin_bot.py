import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv
from datetime import datetime, UTC

# Импортируем основные модули
from src.agents.agent_core import agent_core
from src.notion.universal_repository import UniversalNotionRepository
from src.core.config import Settings

load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AdminBot:
    """Расширенный Telegram бот с функциями администратора"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.allowed_users = self._parse_allowed_users()
        self.admin_users = self._parse_admin_users()
        
        # Инициализация репозитория
        self.settings = Settings()
        self.notion_repo = UniversalNotionRepository(self.settings)
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
    
    def _parse_allowed_users(self) -> set:
        """Парсит список разрешённых пользователей"""
        users_str = os.getenv("TELEGRAM_ALLOWED_USERS", "")
        return {int(user_id.strip()) for user_id in users_str.split(",") if user_id.strip()}
    
    def _parse_admin_users(self) -> set:
        """Парсит список администраторов"""
        admins_str = os.getenv("TELEGRAM_ADMIN_USERS", "")
        return {int(user_id.strip()) for user_id in admins_str.split(",") if user_id.strip()}
    
    def _setup_handlers(self):
        """Настройка обработчиков команд"""
        # Тестовая команда (без проверки прав)
        self.application.add_handler(CommandHandler("test", self.test_command))
        
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        
        # Команды управления базами данных
        self.application.add_handler(CommandHandler("dbs", self.databases_command))
        self.application.add_handler(CommandHandler("db_info", self.db_info_command))
        self.application.add_handler(CommandHandler("db_create", self.db_create_command))
        self.application.add_handler(CommandHandler("db_clean", self.db_clean_command))
        
        # Команды работы с универсальным репозиторием
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(CommandHandler("create", self.create_command))
        self.application.add_handler(CommandHandler("get", self.get_command))
        self.application.add_handler(CommandHandler("update", self.update_command))
        self.application.add_handler(CommandHandler("delete", self.delete_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        self.application.add_handler(CommandHandler("validate", self.validate_command))
        
        # Быстрые команды для личностного развития
        self.application.add_handler(CommandHandler("todo", self.todo_command))
        self.application.add_handler(CommandHandler("habit", self.habit_command))
        self.application.add_handler(CommandHandler("reflection", self.reflection_command))
        self.application.add_handler(CommandHandler("idea", self.idea_command))
        self.application.add_handler(CommandHandler("morning", self.morning_command))
        self.application.add_handler(CommandHandler("evening", self.evening_command))
        
        # Команды аналитики и отчетов
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("progress", self.progress_command))
        self.application.add_handler(CommandHandler("mood", self.mood_command))
        self.application.add_handler(CommandHandler("insights", self.insights_command))
        self.application.add_handler(CommandHandler("recommendations", self.recommendations_command))
        
        # Команды управления агентами
        self.application.add_handler(CommandHandler("agents", self.agents_command))
        self.application.add_handler(CommandHandler("agent_add", self.agent_add_command))
        self.application.add_handler(CommandHandler("agent_edit", self.agent_edit_command))
        self.application.add_handler(CommandHandler("agent_delete", self.agent_delete_command))
        
        # Команды мониторинга и оптимизации
        self.application.add_handler(CommandHandler("cache", self.cache_command))
        self.application.add_handler(CommandHandler("optimize", self.optimize_command))
        
        # Команды системного управления
        self.application.add_handler(CommandHandler("system", self.system_command))
        self.application.add_handler(CommandHandler("backup", self.backup_command))
        self.application.add_handler(CommandHandler("restore", self.restore_command))
        
        # Команды интеграции с Xiaomi Watch S
        self.application.add_handler(CommandHandler("watch_sync", self.watch_sync_command))
        self.application.add_handler(CommandHandler("watch_biometrics", self.watch_biometrics_command))
        self.application.add_handler(CommandHandler("watch_voice", self.watch_voice_command))
        self.application.add_handler(CommandHandler("watch_settings", self.watch_settings_command))
        self.application.add_handler(CommandHandler("watch_notification", self.watch_notification_command))
        
        # Обработчики инлайн-кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def is_user_allowed(self, user_id: int) -> bool:
        """Проверяет, разрешен ли доступ пользователю"""
        return user_id in self.allowed_users
    
    def is_user_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return user_id in self.admin_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        print(f"🔍 Получена команда /start от пользователя {user_id}")
        print(f"🔍 Разрешённые пользователи: {self.allowed_users}")
        print(f"🔍 Админы: {self.admin_users}")
        
        if not self.is_user_allowed(user_id):
            print(f"❌ Пользователь {user_id} не имеет доступа")
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        is_admin = self.is_user_admin(user_id)
        print(f"✅ Пользователь {user_id} {'админ' if is_admin else 'обычный пользователь'}")
        
        welcome_text = f"""
🤖 **Notion-Telegram-LLM Admin Panel**

Привет, {update.effective_user.first_name}!

{'👑 **Режим администратора**' if is_admin else '👤 **Обычный пользователь**'}

**Основные команды:**
• `/help` - Справка
• `/agents` - Управление агентами
• `/stats` - Статистика
• `/cache` - Кэш

{'**Команды администратора:**' if is_admin else ''}
{'• `/admin` - Панель администратора' if is_admin else ''}
{'• `/dbs` - Управление базами данных' if is_admin else ''}
{'• `/system` - Системные настройки' if is_admin else ''}
        """
        
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)
        print(f"✅ Ответ отправлен пользователю {user_id}")
    
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

**🚀 Быстрые команды для развития:**
• `/todo [задача]` - Быстро добавить задачу
• `/habit [название]` - Быстро добавить привычку
• `/reflection [текст]` - Быстро добавить рефлексию
• `/idea [идея]` - Быстро сохранить идею
• `/morning` - Создать утренний ритуал
• `/evening` - Создать вечернюю рефлексию

**📊 Аналитика и отчеты:**
• `/progress` - Отчет о прогрессе
• `/mood` - Анализ настроения
• `/insights` - Персональные инсайты
• `/recommendations` - Персональные рекомендации

**📱 Интеграция с Xiaomi Watch S:**
• `/watch_sync` - Синхронизация с часами
• `/watch_biometrics` - Просмотр биометрических данных
• `/watch_voice` - Тест голосового интерфейса
• `/watch_settings` - Настройка уведомлений
• `/watch_notification` - Генерация умного уведомления

**Команды для работы с данными:**
• `/validate [table]` - Проверка структуры таблицы
• `/validate all` - Проверка всех таблиц
• `/list [table] [limit]` - Список элементов
• `/create [table] [title] [description]` - Создание элемента
• `/get [table] [id]` - Получение элемента по ID
• `/search [table] [query]` - Поиск элементов
• `/update [table] [id] [field] [value]` - Обновление элемента
• `/delete [table] [id]` - Удаление элемента

**Доступные таблицы:**
• `rituals` - Ритуалы
• `habits` - Привычки
• `reflections` - Размышления
• `guides` - Руководства
• `actions` - Действия/задачи
• `terms` - Термины
• `materials` - Материалы

**Примеры быстрого использования:**
• `/todo "Купить продукты"` - добавить задачу
• `/habit "Медитация"` - добавить привычку
• `/reflection "Сегодня был продуктивный день"` - добавить рефлексию
• `/morning` - создать утренний ритуал
• `/progress` - посмотреть прогресс
• `/recommendations` - получить рекомендации
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
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Панель администратора"""
        user_id = update.effective_user.id
        print(f"🔍 Получена команда /admin от пользователя {user_id}")
        
        if not self.is_user_admin(user_id):
            print(f"❌ Пользователь {user_id} не является админом")
            await update.message.reply_text("❌ Требуются права администратора")
            return
        
        print(f"✅ Пользователь {user_id} - админ, показываю панель")
        
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
        print(f"✅ Админ-панель отправлена пользователю {user_id}")
    
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
    
    async def agents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление агентами"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        is_admin = self.is_user_admin(update.effective_user.id)
        
        # Загружаем промпты агентов
        prompts = await agent_core.load_prompts_from_notion(force_refresh=True)
        
        text = "🤖 **УПРАВЛЕНИЕ АГЕНТАМИ**\n\n"
        
        if prompts:
            text += f"**Найдено агентов:** {len(prompts)}\n\n"
            
            for role, prompt in prompts.items():
                text += f"📝 **{role}**\n"
                text += f"   Длина промпта: {len(prompt)} символов\n"
                text += f"   Начало: {prompt[:50]}...\n\n"
        else:
            text += "❌ Агенты не найдены\n"
        
        if is_admin:
            text += "**Команды администратора:**\n"
            text += "• `/agent_add [роль] [промпт]` - Добавить агента\n"
            text += "• `/agent_edit [роль] [новый_промпт]` - Изменить агента\n"
            text += "• `/agent_delete [роль]` - Удалить агента\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
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
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Расширенная статистика"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        # Упрощённая статистика без performance_monitor
        text = "📊 **СТАТИСТИКА СИСТЕМЫ**\n\n"
        
        try:
            # Получаем количество агентов
            prompts = await agent_core.load_prompts_from_notion(force_refresh=True)
            text += f"**Агентов:** {len(prompts)}\n"
            
            # Системная информация
            import platform
            try:
                import psutil
                text += f"**CPU:** {psutil.cpu_percent()}%\n"
                text += f"**Память:** {psutil.virtual_memory().percent}%\n"
                text += f"**Диск:** {psutil.disk_usage('.').percent}%\n"
            except ImportError:
                text += "**CPU:** N/A\n"
                text += "**Память:** N/A\n"
                text += "**Диск:** N/A\n"
            
            text += f"**Платформа:** {platform.platform()}\n"
            text += f"**Python:** {platform.python_version()}\n"
            
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при получении статистики: {str(e)}")
    
    async def optimize_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Рекомендации по оптимизации"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        text = "💡 **РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ**\n\n"
        
        # Общие рекомендации
        text += "**Общие советы:**\n"
        text += "• Используйте кэширование для повторных запросов\n"
        text += "• Выбирайте подходящие модели для задач\n"
        text += "• Ограничивайте max_tokens для экономии\n"
        text += "• Регулярно мониторьте использование\n"
        text += "• Обновляйте промпты агентов для лучших результатов\n"
        text += "• Используйте OpenRouter для оптимизации стоимости\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
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
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на инлайн-кнопки"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
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
    
    async def _handle_admin_dbs(self, query):
        """Обработка кнопки управления базами данных"""
        dbs_info = await self._get_databases_info()
        
        text = "🗄️ **УПРАВЛЕНИЕ БАЗАМИ ДАННЫХ**\n\n"
        
        for db_name, info in dbs_info.items():
            status = "✅" if info['exists'] else "❌"
            text += f"{status} **{db_name}**: {info['description']}\n"
            if info['exists']:
                text += f"   📊 Записей: {info['count']}\n"
            text += "\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")],
            [InlineKeyboardButton("📊 Статистика БД", callback_data="admin_db_stats")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_agents(self, query):
        """Обработка кнопки управления агентами"""
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
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")],
            [InlineKeyboardButton("➕ Добавить агента", callback_data="admin_agent_add")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_stats(self, query):
        """Обработка кнопки статистики"""
        if not self.is_user_admin(query.from_user.id):
            await query.edit_message_text("❌ Требуются права администратора")
            return
        
        try:
            # Упрощённая статистика
            text = "📊 **СТАТИСТИКА СИСТЕМЫ**\n\n"
            
            # Получаем количество агентов
            prompts = await agent_core.load_prompts_from_notion(force_refresh=True)
            text += f"**Агентов:** {len(prompts)}\n"
            
            # Системная информация
            import platform
            try:
                import psutil
                text += f"**CPU:** {psutil.cpu_percent()}%\n"
                text += f"**Память:** {psutil.virtual_memory().percent}%\n"
                text += f"**Диск:** {psutil.disk_usage('.').percent}%\n"
            except ImportError:
                text += "**CPU:** N/A\n"
                text += "**Память:** N/A\n"
                text += "**Диск:** N/A\n"
            
            text += f"**Платформа:** {platform.platform()}\n"
            text += f"**Python:** {platform.python_version()}\n"
            
        except Exception as e:
            text = f"❌ Ошибка: {str(e)}"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_system(self, query):
        """Обработка кнопки системных настроек"""
        system_info = await self._get_system_info()
        
        text = "⚙️ **СИСТЕМНЫЕ НАСТРОЙКИ**\n\n"
        
        for key, value in system_info.items():
            text += f"**{key}:** {value}\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")],
            [InlineKeyboardButton("💾 Резервная копия", callback_data="admin_backup")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _handle_admin_backup(self, query):
        """Обработка кнопки резервного копирования"""
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
        
        text = "💡 **РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ**\n\n"
        
        # Общие рекомендации
        text += "**Общие советы:**\n"
        text += "• Используйте кэширование для повторных запросов\n"
        text += "• Выбирайте подходящие модели для задач\n"
        text += "• Ограничивайте max_tokens для экономии\n"
        text += "• Регулярно мониторьте использование\n"
        text += "• Обновляйте промпты агентов для лучших результатов\n"
        text += "• Используйте OpenRouter для оптимизации стоимости\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
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
        import psutil
        
        return {
            "Платформа": platform.platform(),
            "Python": platform.python_version(),
            "CPU": f"{psutil.cpu_percent()}%",
            "Память": f"{psutil.virtual_memory().percent}%",
            "Диск": f"{psutil.disk_usage('.').percent}%",
            "Агенты": len(await agent_core.load_prompts_from_notion()) if agent_core else 0,
            "Кэш": "Интегрирован в систему"
        }
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text
        print(f"🔍 Получено сообщение от {user_id}: {message_text}")
        
        if not self.is_user_allowed(user_id):
            print(f"❌ Пользователь {user_id} не имеет доступа")
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        # Здесь можно добавить обработку текстовых команд
        await update.message.reply_text("💬 Используйте команды для управления системой. /help для справки.")
        print(f"✅ Ответ отправлен пользователю {user_id}")
    
    async def run(self):
        print("🤖 Запуск Admin Telegram бота...")
        await self.application.initialize()
        await self.application.start()
        await self.application.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Бот запущен. Ожидание сообщений...")
        await self.application.run_polling(allowed_updates=Update.ALL_TYPES, close_loop=False)

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
            # Здесь можно добавить логику создания базы в Notion
            await update.message.reply_text(f"🔄 Создание базы '{db_name}'...")
            
            # Пока что просто сообщаем о намерении
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
            
            # Здесь можно добавить логику очистки дубликатов
            await update.message.reply_text(f"✅ Дубликаты в базе '{db_name}' будут очищены (функция в разработке)")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при очистке: {str(e)}")
    
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
            
            # Здесь можно добавить логику обновления в Notion
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
            
            # Здесь можно добавить логику удаления из Notion
            await update.message.reply_text(f"✅ Агент '{role}' будет удалён (функция в разработке)")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при удалении: {str(e)}")
    
    async def cache_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление кэшем"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        text = "💾 **УПРАВЛЕНИЕ КЭШЕМ**\n\n"
        text += "**Статус:** Кэш интегрирован в систему\n"
        text += "**Функции:**\n"
        text += "• Автоматическое кэширование промптов\n"
        text += "• Кэширование ответов агентов\n"
        text += "• Оптимизация производительности\n"
        text += "\n**Команды:**\n"
        text += "• `/stats` - Статистика системы\n"
        text += "• `/optimize` - Рекомендации по оптимизации\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
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
            
            # Здесь можно добавить логику восстановления
            await update.message.reply_text(f"✅ Восстановление из '{backup_file}' будет выполнено (функция в разработке)")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при восстановлении: {str(e)}")

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Тестовая команда для проверки работы бота"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        print(f"🔍 Тестовая команда от {user_id} ({user_name})")
        
        test_message = f"""
🧪 **ТЕСТ БОТА**

✅ Бот работает!
👤 Пользователь: {user_name} (ID: {user_id})
🔧 Версия: Admin Bot v1.0
⏰ Время: {update.message.date}

**Доступные команды:**
• /start - Приветствие
• /help - Справка
• /admin - Админ-панель (если есть права)
• /test - Этот тест
        """
        
        await update.message.reply_text(test_message, parse_mode=ParseMode.MARKDOWN)
        print(f"✅ Тестовый ответ отправлен пользователю {user_id}")

    # Новые команды для работы с универсальным репозиторием
    async def validate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверка структуры баз данных"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите таблицу: `/validate [table]` или `/validate all`")
            return
        
        table_name = context.args[0].lower()
        
        try:
            if table_name == "all":
                await update.message.reply_text("🔍 Проверка всех таблиц...")
                results = []
                for table in ['rituals', 'habits', 'reflections', 'guides', 'actions', 'terms', 'materials']:
                    is_valid, message = await self.notion_repo.validate_database(table)
                    status = "✅" if is_valid else "❌"
                    results.append(f"{status} {table}: {message}")
                
                response = "**Результаты проверки:**\n\n" + "\n".join(results)
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                is_valid, message = await self.notion_repo.validate_database(table_name)
                status = "✅" if is_valid else "❌"
                response = f"**Проверка таблицы {table_name}:**\n\n{status} {message}"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при проверке: {str(e)}")

    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Список элементов из таблицы"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите таблицу: `/list [table] [limit]`")
            return
        
        table_name = context.args[0].lower()
        limit = int(context.args[1]) if len(context.args) > 1 else 10
        
        try:
            await update.message.reply_text(f"📋 Получение списка из {table_name}...")
            items = await self.notion_repo.list_items(table_name, limit=limit)
            
            if not items:
                await update.message.reply_text(f"📭 Таблица {table_name} пуста")
                return
            
            response = f"**Список элементов из {table_name} ({len(items)}):**\n\n"
            for i, item in enumerate(items[:limit], 1):
                title = item.get('title', 'Без названия')
                status = item.get('status', 'Не указан')
                response += f"{i}. **{title}** ({status})\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при получении списка: {str(e)}")

    async def create_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание элемента в таблице"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ Укажите таблицу и данные: `/create [table] [title] [description]`")
            return
        
        table_name = context.args[0].lower()
        title = context.args[1]
        description = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        
        try:
            await update.message.reply_text(f"➕ Создание элемента в {table_name}...")
            
            # Базовая структура данных
            data = {
                'title': title,
                'description': description,
                'status': 'Active',
                'created_date': datetime.now(UTC)
            }
            
            # Добавляем специфичные поля для разных таблиц
            if table_name == 'rituals':
                data.update({
                    'category': 'General',
                    'frequency': 'Daily',
                    'priority': 'Medium'
                })
            elif table_name == 'habits':
                data.update({
                    'category': 'General',
                    'frequency': 'Daily',
                    'target_frequency': 7,
                    'current_frequency': 0
                })
            elif table_name == 'reflections':
                data.update({
                    'type': 'Daily',
                    'mood': 'Neutral'
                })
            elif table_name == 'guides':
                data.update({
                    'category': 'General',
                    'difficulty': 'Beginner',
                    'status': 'Draft'
                })
            elif table_name == 'actions':
                data.update({
                    'priority': 'Medium',
                    'category': 'General'
                })
            elif table_name == 'terms':
                data.update({
                    'category': 'General',
                    'mastery_level': 'Learning'
                })
            elif table_name == 'materials':
                data.update({
                    'type': 'Article',
                    'category': 'General',
                    'status': 'Active'
                })
            
            created_item = await self.notion_repo.create_item(table_name, data)
            
            if created_item:
                response = f"✅ Элемент создан в {table_name}:\n\n**{created_item['title']}**\nID: `{created_item['id']}`"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"❌ Не удалось создать элемент в {table_name}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при создании: {str(e)}")

    async def get_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение элемента по ID"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ Укажите таблицу и ID: `/get [table] [id]`")
            return
        
        table_name = context.args[0].lower()
        item_id = context.args[1]
        
        try:
            await update.message.reply_text(f"🔍 Получение элемента из {table_name}...")
            item = await self.notion_repo.get_item(table_name, item_id)
            
            if item:
                response = f"**Элемент из {table_name}:**\n\n"
                response += f"**Название:** {item.get('title', 'Не указано')}\n"
                response += f"**ID:** `{item['id']}`\n"
                response += f"**Статус:** {item.get('status', 'Не указан')}\n"
                response += f"**Создан:** {item.get('created_time', 'Не указано')}\n"
                
                if item.get('description'):
                    response += f"**Описание:** {item['description']}\n"
                
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"❌ Элемент не найден в {table_name}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при получении элемента: {str(e)}")

    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Поиск элементов в таблице"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ Укажите таблицу и запрос: `/search [table] [query]`")
            return
        
        table_name = context.args[0].lower()
        query = " ".join(context.args[1:])
        
        try:
            await update.message.reply_text(f"🔍 Поиск в {table_name}...")
            results = await self.notion_repo.search_items(table_name, query)
            
            if not results:
                await update.message.reply_text(f"🔍 По запросу '{query}' ничего не найдено в {table_name}")
                return
            
            response = f"**Результаты поиска в {table_name} ({len(results)}):**\n\n"
            for i, item in enumerate(results[:10], 1):
                title = item.get('title', 'Без названия')
                response += f"{i}. **{title}**\n"
            
            if len(results) > 10:
                response += f"\n... и ещё {len(results) - 10} результатов"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при поиске: {str(e)}")

    async def update_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обновление элемента"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if len(context.args) < 3:
            await update.message.reply_text("❌ Укажите таблицу, ID и данные: `/update [table] [id] [field] [value]`")
            return
        
        table_name = context.args[0].lower()
        item_id = context.args[1]
        field = context.args[2]
        value = " ".join(context.args[3:]) if len(context.args) > 3 else ""
        
        try:
            await update.message.reply_text(f"✏️ Обновление элемента в {table_name}...")
            
            update_data = {field: value}
            updated_item = await self.notion_repo.update_item(table_name, item_id, update_data)
            
            if updated_item:
                response = f"✅ Элемент обновлён в {table_name}:\n\n**{updated_item['title']}**\nПоле '{field}' изменено"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"❌ Не удалось обновить элемент в {table_name}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при обновлении: {str(e)}")

    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление элемента"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ Укажите таблицу и ID: `/delete [table] [id]`")
            return
        
        table_name = context.args[0].lower()
        item_id = context.args[1]
        
        try:
            await update.message.reply_text(f"🗑️ Удаление элемента из {table_name}...")
            deleted = await self.notion_repo.delete_item(table_name, item_id)
            
            if deleted:
                await update.message.reply_text(f"✅ Элемент удалён из {table_name}")
            else:
                await update.message.reply_text(f"❌ Не удалось удалить элемент из {table_name}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при удалении: {str(e)}")

    # Быстрые команды для личностного развития
    async def todo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Быстрое добавление задачи"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите задачу: `/todo [задача]`")
            return
        
        task_text = " ".join(context.args)
        
        try:
            await update.message.reply_text(f"📝 Добавление задачи...")
            
            task_data = {
                'title': task_text,
                'status': 'Pending',
                'priority': 'Medium',
                'category': 'General',
                'description': f"Задача: {task_text}",
                'tags': ['todo', 'quick'],
                'created_date': datetime.now(UTC)
            }
            
            created_task = await self.notion_repo.create_item('actions', task_data)
            
            if created_task:
                response = f"✅ Задача добавлена:\n\n**{created_task['title']}**\nID: `{created_task['id']}`\nСтатус: {created_task.get('status', 'Pending')}"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Не удалось добавить задачу")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при добавлении задачи: {str(e)}")

    async def habit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Быстрое добавление привычки"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите привычку: `/habit [название]`")
            return
        
        habit_name = " ".join(context.args)
        
        try:
            await update.message.reply_text(f"🔄 Добавление привычки...")
            
            habit_data = {
                'title': habit_name,
                'status': 'Active',
                'category': 'General',
                'frequency': 'Daily',
                'description': f"Привычка: {habit_name}",
                'tags': ['habit', 'quick'],
                'created_date': datetime.now(UTC),
                'target_frequency': 7,
                'current_frequency': 0
            }
            
            created_habit = await self.notion_repo.create_habit(habit_data)
            
            if created_habit:
                response = f"✅ Привычка добавлена:\n\n**{created_habit['title']}**\nID: `{created_habit['id']}`\nЧастота: {created_habit.get('frequency', 'Daily')}"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Не удалось добавить привычку")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при добавлении привычки: {str(e)}")

    async def reflection_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Быстрое добавление рефлексии"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите рефлексию: `/reflection [текст]`")
            return
        
        reflection_text = " ".join(context.args)
        
        try:
            await update.message.reply_text(f"💭 Добавление рефлексии...")
            
            reflection_data = {
                'title': f"Рефлексия {datetime.now().strftime('%d.%m.%Y')}",
                'type': 'Daily',
                'mood': 'Neutral',
                'content': reflection_text,
                'tags': ['reflection', 'quick'],
                'created_date': datetime.now(UTC)
            }
            
            created_reflection = await self.notion_repo.create_reflection(reflection_data)
            
            if created_reflection:
                response = f"✅ Рефлексия добавлена:\n\n**{created_reflection['title']}**\nID: `{created_reflection['id']}`\n\n{reflection_text}"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Не удалось добавить рефлексию")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при добавлении рефлексии: {str(e)}")

    async def idea_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Быстрое сохранение идеи"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите идею: `/idea [идея]`")
            return
        
        idea_text = " ".join(context.args)
        
        try:
            await update.message.reply_text(f"💡 Сохранение идеи...")
            
            # Сохраняем как материал
            idea_data = {
                'title': f"Идея: {idea_text[:50]}...",
                'type': 'Idea',
                'category': 'General',
                'description': idea_text,
                'tags': ['idea', 'quick'],
                'created_date': datetime.now(UTC),
                'status': 'Active'
            }
            
            created_idea = await self.notion_repo.create_material(idea_data)
            
            if created_idea:
                response = f"✅ Идея сохранена:\n\n**{created_idea['title']}**\nID: `{created_idea['id']}`\n\n{idea_text}"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Не удалось сохранить идею")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при сохранении идеи: {str(e)}")

    async def morning_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Утренний ритуал - шаблон"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            await update.message.reply_text("🌅 Создание утреннего ритуала...")
            
            # Создаем утренний ритуал
            ritual_data = {
                'title': f"Утренний ритуал {datetime.now().strftime('%d.%m.%Y')}",
                'status': 'Active',
                'category': 'Morning',
                'frequency': 'Daily',
                'description': 'Утренний ритуал для продуктивного дня',
                'tags': ['morning', 'ritual', 'daily'],
                'created_date': datetime.now(UTC),
                'priority': 'High'
            }
            
            created_ritual = await self.notion_repo.create_ritual(ritual_data)
            
            if created_ritual:
                response = f"🌅 **Утренний ритуал создан!**\n\n**{created_ritual['title']}**\nID: `{created_ritual['id']}`\n\n**Что включить в утренний ритуал:**\n• Медитация (5-10 мин)\n• Планирование дня\n• Легкая зарядка\n• Здоровый завтрак\n• Чтение/обучение"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Не удалось создать утренний ритуал")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при создании утреннего ритуала: {str(e)}")

    async def evening_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Вечерняя рефлексия - шаблон"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            await update.message.reply_text("🌙 Создание вечерней рефлексии...")
            
            # Создаем вечернюю рефлексию
            reflection_data = {
                'title': f"Вечерняя рефлексия {datetime.now().strftime('%d.%m.%Y')}",
                'type': 'Evening',
                'mood': 'Neutral',
                'content': 'Время для размышлений о прошедшем дне',
                'tags': ['evening', 'reflection', 'daily'],
                'created_date': datetime.now(UTC)
            }
            
            created_reflection = await self.notion_repo.create_reflection(reflection_data)
            
            if created_reflection:
                response = f"🌙 **Вечерняя рефлексия создана!**\n\n**{created_reflection['title']}**\nID: `{created_reflection['id']}`\n\n**Вопросы для рефлексии:**\n• Что сегодня получилось хорошо?\n• Что можно было сделать лучше?\n• За что я благодарен?\n• Что планирую на завтра?\n\nИспользуй `/reflection [текст]` для записи ответов"
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ Не удалось создать вечернюю рефлексию")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при создании вечерней рефлексии: {str(e)}")

    # Команды аналитики и отчетов
    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отчет о прогрессе"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            await update.message.reply_text("📊 Подготовка отчета о прогрессе...")
            
            # Получаем данные по всем таблицам
            rituals = await self.notion_repo.get_rituals()
            habits = await self.notion_repo.get_habits()
            reflections = await self.notion_repo.get_reflections()
            actions = await self.notion_repo.get_actions()
            
            # Базовая статистика
            active_rituals = len([r for r in rituals if r.get('status') == 'Active'])
            active_habits = len([h for h in habits if h.get('status') == 'Active'])
            pending_tasks = len([a for a in actions if a.get('status') == 'Pending'])
            completed_tasks = len([a for a in actions if a.get('status') == 'Done'])
            
            response = f"📊 **Отчет о прогрессе**\n\n"
            response += f"🎯 **Активные ритуалы:** {active_rituals}\n"
            response += f"🔄 **Активные привычки:** {active_habits}\n"
            response += f"📝 **Задачи в работе:** {pending_tasks}\n"
            response += f"✅ **Выполнено задач:** {completed_tasks}\n"
            response += f"💭 **Рефлексий:** {len(reflections)}\n\n"
            
            if active_habits > 0:
                response += f"**Рекомендации:**\n"
                response += f"• Отслеживай выполнение привычек\n"
                response += f"• Используй `/reflection` для анализа\n"
                response += f"• Планируй день с `/morning`\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при подготовке отчета: {str(e)}")

    async def mood_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Анализ настроения по рефлексиям"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            await update.message.reply_text("😊 Анализ настроения...")
            
            reflections = await self.notion_repo.get_reflections()
            
            if not reflections:
                await update.message.reply_text("📭 Нет данных для анализа настроения. Добавь рефлексии с помощью `/reflection`")
                return
            
            # Простой анализ настроения
            mood_counts = {}
            for reflection in reflections:
                mood = reflection.get('mood', 'Unknown')
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            response = f"😊 **Анализ настроения**\n\n"
            response += f"**Всего рефлексий:** {len(reflections)}\n\n"
            
            for mood, count in mood_counts.items():
                percentage = (count / len(reflections)) * 100
                response += f"**{mood}:** {count} ({percentage:.1f}%)\n"
            
            response += f"\n**Рекомендации:**\n"
            if mood_counts.get('Positive', 0) > mood_counts.get('Negative', 0):
                response += f"• Отличное настроение! Продолжай в том же духе\n"
            else:
                response += f"• Попробуй добавить больше позитивных активностей\n"
            
            response += f"• Используй `/reflection` для отслеживания\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при анализе настроения: {str(e)}")

    async def insights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Персональные инсайты"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            await update.message.reply_text("🧠 Анализ персональных инсайтов...")
            
            # Получаем данные
            reflections = await self.notion_repo.get_reflections()
            habits = await self.notion_repo.get_habits()
            actions = await self.notion_repo.get_actions()
            
            response = f"🧠 **Персональные инсайты**\n\n"
            
            # Инсайт 1: Активность
            if len(reflections) > 0:
                response += f"📈 **Активность рефлексии:**\n"
                response += f"• У тебя {len(reflections)} рефлексий\n"
                response += f"• Это показывает высокий уровень самосознания\n\n"
            
            # Инсайт 2: Привычки
            active_habits = [h for h in habits if h.get('status') == 'Active']
            if active_habits:
                response += f"🔄 **Работа с привычками:**\n"
                response += f"• Активных привычек: {len(active_habits)}\n"
                response += f"• Фокус на развитии: {', '.join([h.get('title', '')[:20] for h in active_habits[:3]])}\n\n"
            
            # Инсайт 3: Продуктивность
            completed_tasks = [a for a in actions if a.get('status') == 'Done']
            if completed_tasks:
                response += f"✅ **Продуктивность:**\n"
                response += f"• Выполнено задач: {len(completed_tasks)}\n"
                response += f"• Это показывает хорошую дисциплину\n\n"
            
            response += f"**Рекомендации:**\n"
            response += f"• Продолжай вести рефлексии\n"
            response += f"• Отслеживай прогресс привычек\n"
            response += f"• Используй `/stats` для детальной статистики\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при анализе инсайтов: {str(e)}")

    async def recommendations_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Персональные рекомендации"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            await update.message.reply_text("💡 Подготовка персональных рекомендаций...")
            
            # Получаем данные
            rituals = await self.notion_repo.get_rituals()
            habits = await self.notion_repo.get_habits()
            reflections = await self.notion_repo.get_reflections()
            actions = await self.notion_repo.get_actions()
            
            response = f"💡 **Персональные рекомендации**\n\n"
            
            # Рекомендация 1: На основе количества ритуалов
            if len(rituals) < 3:
                response += f"🎯 **Ритуалы:**\n"
                response += f"• У тебя мало ритуалов ({len(rituals)})\n"
                response += f"• Попробуй добавить утренний ритуал: `/morning`\n"
                response += f"• Или создай вечерний: `/evening`\n\n"
            
            # Рекомендация 2: На основе привычек
            active_habits = [h for h in habits if h.get('status') == 'Active']
            if len(active_habits) < 2:
                response += f"🔄 **Привычки:**\n"
                response += f"• Активных привычек: {len(active_habits)}\n"
                response += f"• Попробуй добавить новую: `/habit [название]`\n"
                response += f"• Например: `/habit медитация`\n\n"
            
            # Рекомендация 3: На основе рефлексий
            if len(reflections) < 5:
                response += f"💭 **Рефлексии:**\n"
                response += f"• Рефлексий: {len(reflections)}\n"
                response += f"• Регулярные рефлексии помогают развитию\n"
                response += f"• Используй: `/reflection [текст]`\n\n"
            
            # Рекомендация 4: На основе задач
            pending_tasks = [a for a in actions if a.get('status') == 'Pending']
            if len(pending_tasks) > 5:
                response += f"📝 **Задачи:**\n"
                response += f"• Много незавершенных задач: {len(pending_tasks)}\n"
                response += f"• Попробуй фокус на 3 главных задачах\n"
                response += f"• Используй приоритизацию\n\n"
            
            response += f"**Общие рекомендации:**\n"
            response += f"• Используй `/morning` для планирования дня\n"
            response += f"• `/evening` для рефлексии\n"
            response += f"• `/progress` для отслеживания\n"
            response += f"• `/stats` для детальной статистики\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при подготовке рекомендаций: {str(e)}")

    async def watch_sync_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Синхронизация с Xiaomi Watch S"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            from src.integrations.xiaomi_watch import xiaomi_integration
            
            await update.message.reply_text("🔄 Синхронизация с Xiaomi Watch S...")
            
            # Получаем биометрические данные
            biometrics = await xiaomi_integration.watch_api.get_current_biometrics()
            
            response_text = f"""
📱 **Синхронизация с Xiaomi Watch S**

✅ **Биометрические данные получены:**
• Пульс: {biometrics.heart_rate} уд/мин
• Качество сна: {biometrics.sleep_quality:.0f}%
• Продолжительность сна: {biometrics.sleep_duration:.1f} ч
• Уровень стресса: {biometrics.stress_level:.0f}%
• Шаги: {biometrics.steps}
• Калории: {biometrics.calories}

🔄 **Готов к голосовым командам!**
            """.strip()
            
            await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка синхронизации: {str(e)}")

    async def watch_biometrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр биометрических данных"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            from src.integrations.xiaomi_watch import xiaomi_integration
            
            await update.message.reply_text("📊 Получение биометрических данных...")
            
            biometrics = await xiaomi_integration.watch_api.get_current_biometrics()
            
            # Анализ данных
            stress_analysis = "Нормальный" if biometrics.stress_level < 50 else "Повышенный"
            sleep_analysis = "Отличный" if biometrics.sleep_quality > 80 else "Хороший" if biometrics.sleep_quality > 60 else "Требует улучшения"
            activity_analysis = "Активный" if biometrics.steps > 8000 else "Умеренный" if biometrics.steps > 5000 else "Низкий"
            
            response_text = f"""
📊 **Биометрические данные**

💓 **Сердечно-сосудистая система:**
• Пульс: {biometrics.heart_rate} уд/мин
• Уровень стресса: {biometrics.stress_level:.0f}% ({stress_analysis})

😴 **Сон:**
• Качество: {biometrics.sleep_quality:.0f}% ({sleep_analysis})
• Продолжительность: {biometrics.sleep_duration:.1f} ч

🏃‍♂️ **Активность:**
• Шаги: {biometrics.steps} ({activity_analysis})
• Калории: {biometrics.calories}
• Активные минуты: {biometrics.activity_level:.1f} ч

💡 **Рекомендации:**
{self._get_biometric_recommendations(biometrics)}
            """.strip()
            
            await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения данных: {str(e)}")

    async def watch_voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Тест голосового интерфейса"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            from src.integrations.xiaomi_watch import xiaomi_integration
            
            # Симулируем голосовую команду
            test_commands = [
                "добавь задачу купить продукты",
                "мой прогресс",
                "добавь привычку медитация",
                "мое настроение хорошее"
            ]
            
            response_text = "🎤 **Тест голосового интерфейса**\n\n"
            
            for command in test_commands:
                response = await xiaomi_integration.handle_voice_command(b"test_audio")
                response_text += f"**Команда:** `{command}`\n"
                response_text += f"**Ответ:** {response}\n\n"
            
            await update.message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка тестирования: {str(e)}")

    async def watch_settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Настройка уведомлений часов"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("🔔 Утренние уведомления", callback_data="watch_morning"),
                InlineKeyboardButton("🌅 Дневные уведомления", callback_data="watch_day")
            ],
            [
                InlineKeyboardButton("🌙 Вечерние уведомления", callback_data="watch_evening"),
                InlineKeyboardButton("🚨 Экстренные уведомления", callback_data="watch_emergency")
            ],
            [
                InlineKeyboardButton("📊 Биометрические уведомления", callback_data="watch_biometrics_notif"),
                InlineKeyboardButton("🎯 Целевые уведомления", callback_data="watch_goals")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ **Настройка уведомлений Xiaomi Watch S**\n\n"
            "Выберите тип уведомлений для настройки:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def watch_notification_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Генерация умного уведомления"""
        if not self.is_user_allowed(update.effective_user.id):
            await update.message.reply_text("❌ Доступ запрещён")
            return
        
        try:
            from src.integrations.xiaomi_watch import xiaomi_integration
            
            notification = await xiaomi_integration.get_smart_notification()
            
            await update.message.reply_text(
                f"📱 **Умное уведомление для часов:**\n\n{notification}",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка генерации уведомления: {str(e)}")

    def _get_biometric_recommendations(self, biometrics) -> str:
        """Генерация рекомендаций на основе биометрии"""
        recommendations = []
        
        if biometrics.stress_level and biometrics.stress_level > 60:
            recommendations.append("• Рекомендуется медитация или прогулка для снижения стресса")
        
        if biometrics.sleep_quality and biometrics.sleep_quality < 70:
            recommendations.append("• Улучшите качество сна: избегайте экранов перед сном")
        
        if biometrics.steps and biometrics.steps < 6000:
            recommendations.append("• Увеличьте физическую активность: цель 8000+ шагов в день")
        
        if biometrics.heart_rate and biometrics.heart_rate > 90:
            recommendations.append("• Пульс повышен, рекомендуется отдых")
        
        if not recommendations:
            recommendations.append("• Отличные показатели! Продолжайте в том же духе")
        
        return "\n".join(recommendations)

# Глобальный экземпляр
admin_bot = AdminBot()