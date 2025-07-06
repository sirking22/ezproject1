#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 УЛУЧШЕННЫЙ TELEGRAM БОТ С НОВЫМ МЕНЕДЖЕРОМ NOTION
Использует новую систему для четкой работы с базами данных
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
)
from notion_client import AsyncClient
from dotenv import load_dotenv

# Импортируем наши модули
from src.services.notion_manager_simple import SimpleNotionManager, NotionResult
from notion_database_schemas import DATABASE_SCHEMAS
from simple_bot import YandexUploader, VideoProcessor, LLMProcessor

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
YA_TOKEN = os.getenv('YA_ACCESS_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not all([NOTION_TOKEN, YA_TOKEN, TELEGRAM_TOKEN]):
    logger.error("❌ Отсутствуют необходимые токены!")
    exit(1)

logger.info("✅ Токены загружены")

# Глобальные объекты
notion_client = None
notion_manager = None
ya_uploader = None
llm_processor = None

# Состояния пользователей
user_states = {}

class EnhancedBotManager:
    """🎯 Улучшенный менеджер бота"""
    
    def __init__(self):
        self.notion_client = AsyncClient(auth=NOTION_TOKEN)
        self.notion_manager = SimpleNotionManager(self.notion_client, DATABASE_SCHEMAS)
        self.ya_uploader = YandexUploader()
        self.llm_processor = LLMProcessor()
        
    async def process_file_upload(self, file_url: str, filename: str, user_input: str = "") -> Dict[str, Any]:
        """
        🔄 Обработка загрузки файла
        
        Args:
            file_url: URL файла от Telegram
            filename: Имя файла
            user_input: Дополнительная информация от пользователя
            
        Returns:
            Результат обработки
        """
        try:
            logger.info(f"📤 Обрабатываем файл: {filename}")
            
            # 1. Загружаем файл в Yandex.Disk
            upload_result = await self.ya_uploader.upload_file(file_url, filename)
            
            if not upload_result['success']:
                return {
                    'success': False,
                    'error': f"Ошибка загрузки файла: {upload_result['error']}"
                }
            
            file_public_url = upload_result['url']
            preview_url = upload_result.get('preview_url', '')
            
            logger.info(f"✅ Файл загружен: {file_public_url}")
            
            # 2. Анализируем пользовательский ввод с LLM (если есть)
            analysis_data = {}
            if user_input:
                logger.info("🧠 Анализируем пользовательский ввод...")
                analysis_data = await self.llm_processor.parse_natural_language(user_input)
            
            # 3. Определяем тип контента и базу данных
            content_type = self._determine_content_type(filename, user_input)
            
            # 4. Создаем запись в соответствующей базе
            if content_type == 'idea':
                result = await self._create_idea_record(filename, file_public_url, analysis_data)
            elif content_type == 'material':
                result = await self._create_material_record(filename, file_public_url, analysis_data)
            else:
                # По умолчанию создаем материал
                result = await self._create_material_record(filename, file_public_url, analysis_data)
            
            if not result.success:
                return {
                    'success': False,
                    'error': f"Ошибка создания записи: {result.error}"
                }
            
            # 5. Устанавливаем обложку если это изображение/видео
            if preview_url and content_type in ['idea', 'material']:
                cover_result = await self.notion_manager.set_cover_image(
                    result.data['id'], 
                    preview_url
                )
                if cover_result.success:
                    logger.info("🖼️ Обложка установлена")
            
            return {
                'success': True,
                'notion_record': result.data,
                'file_url': file_public_url,
                'content_type': content_type
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки файла: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _determine_content_type(self, filename: str, user_input: str) -> str:
        """Определяем тип контента"""
        # Простая логика определения типа
        if any(keyword in user_input.lower() for keyword in ['идея', 'концепт', 'задумка']):
            return 'idea'
        
        # По расширению файла
        if filename.lower().endswith(('.jpg', '.png', '.mp4', '.mov', '.avi')):
            return 'idea'  # Медиа-файлы обычно идеи
        else:
            return 'material'  # Документы и прочее - материалы
    
    async def _create_idea_record(self, filename: str, file_url: str, analysis_data: Dict) -> NotionResult:
        """Создание записи в базе идей"""
        idea_data = {
            'name': analysis_data.get('name', filename),
            'description': analysis_data.get('description', ''),
            'url': file_url,
            'tags': analysis_data.get('tags', []),
            'importance': analysis_data.get('importance', 5)
        }
        
        return await self.notion_manager.create_idea(idea_data)
    
    async def _create_material_record(self, filename: str, file_url: str, analysis_data: Dict) -> NotionResult:
        """Создание записи в базе материалов"""
        material_data = {
            'name': analysis_data.get('name', filename),
            'description': analysis_data.get('description', ''),
            'url': file_url,
            'tags': analysis_data.get('tags', [])
        }
        
        return await self.notion_manager.create_material(material_data)

# Инициализируем менеджер
bot_manager = EnhancedBotManager()

# ===== ОБРАБОТЧИКИ КОМАНД =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    keyboard = [
        [InlineKeyboardButton("📋 Создать задачу", callback_data="create_task")],
        [InlineKeyboardButton("💡 Создать идею", callback_data="create_idea")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("📋 Мои задачи", callback_data="my_tasks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *Улучшенный бот для работы с Notion*\n\n"
        "Выберите действие или просто отправьте файл:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка загруженных файлов"""
    try:
        message = update.message
        user_id = message.from_user.id
        
        # Получаем файл
        if message.document:
            file_obj = message.document
            filename = file_obj.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        elif message.photo:
            file_obj = message.photo[-1]  # Берем фото наивысшего качества
            filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        elif message.video:
            file_obj = message.video
            filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        elif message.audio:
            file_obj = message.audio
            filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        else:
            await message.reply_text("❌ Неподдерживаемый тип файла")
            return
        
        # Получаем URL файла
        file = await context.bot.get_file(file_obj.file_id)
        file_url = file.file_path
        
        # Получаем описание от пользователя
        user_input = message.caption or ""
        
        # Отправляем уведомление о начале обработки
        processing_msg = await message.reply_text(
            f"⏳ Обрабатываю файл `{filename}`...",
            parse_mode='Markdown'
        )
        
        # Обрабатываем файл
        result = await bot_manager.process_file_upload(file_url, filename, user_input)
        
        if result['success']:
            notion_record = result['notion_record']
            content_type = result['content_type']
            
            # Определяем иконку по типу
            icon = "💡" if content_type == 'idea' else "📁"
            type_name = "идея" if content_type == 'idea' else "материал"
            
            success_text = (
                f"{icon} *{type_name.title()} успешно создана!*\n\n"
                f"📝 Название: {notion_record['properties'].get('Name', filename)}\n"
                f"🔗 [Открыть в Notion]({notion_record['url']})\n"
                f"☁️ [Файл на Яндекс.Диске]({result['file_url']})"
            )
            
            await processing_msg.edit_text(
                success_text,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
        else:
            await processing_msg.edit_text(
                f"❌ Ошибка обработки файла:\n`{result['error']}`",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки файла: {e}")
        await update.message.reply_text(
            f"💥 Произошла ошибка: {str(e)}"
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "create_task":
        await query.edit_message_text(
            "✏️ Отправьте описание задачи в формате:\n\n"
            "`Название: Моя задача`\n"
            "`Описание: Подробное описание`\n"
            "`Статус: To do`\n"
            "`Приоритет: !!!`",
            parse_mode='Markdown'
        )
        user_states[query.from_user.id] = 'creating_task'
        
    elif data == "create_idea":
        await query.edit_message_text(
            "💡 Отправьте описание идеи в формате:\n\n"
            "`Название: Моя идея`\n"
            "`Описание: Подробное описание`\n"
            "`Теги: разработка, автоматизация`\n"
            "`Важность: 8`",
            parse_mode='Markdown'
        )
        user_states[query.from_user.id] = 'creating_idea'
        
    elif data == "stats":
        stats = bot_manager.notion_manager.get_stats()
        stats_text = (
            f"📊 *Статистика работы бота:*\n\n"
            f"📈 Всего запросов: {stats['total_requests']}\n"
            f"✅ Успешных: {stats['successful_requests']}\n"
            f"❌ Неудачных: {stats['failed_requests']}\n"
            f"🎯 Процент успеха: {stats['success_rate']:.1f}%"
        )
        await query.edit_message_text(stats_text, parse_mode='Markdown')
        
    elif data == "my_tasks":
        # Получаем задачи пользователя
        tasks_result = await bot_manager.notion_manager.get_tasks(limit=5)
        
        if tasks_result.success:
            tasks = tasks_result.data
            if tasks:
                tasks_text = "📋 *Последние задачи:*\n\n"
                for i, task in enumerate(tasks[:5], 1):
                    title = task['properties'].get('Задача', 'Без названия')
                    status = task['properties'].get('Статус', 'Без статуса')
                    tasks_text += f"{i}. {title} [{status}]\n"
            else:
                tasks_text = "📋 Задач пока нет"
        else:
            tasks_text = f"❌ Ошибка получения задач: {tasks_result.error}"
        
        await query.edit_message_text(tasks_text, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.message.from_user.id
    text = update.message.text
    
    # Проверяем состояние пользователя
    state = user_states.get(user_id)
    
    if state == 'creating_task':
        # Парсим данные задачи
        task_data = await parse_task_data(text)
        if task_data:
            result = await bot_manager.notion_manager.create_task(task_data)
            
            if result.success:
                await update.message.reply_text(
                    f"✅ Задача создана!\n"
                    f"🔗 [Открыть в Notion]({result.data['url']})",
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
            else:
                await update.message.reply_text(
                    f"❌ Ошибка создания задачи: {result.error}"
                )
        else:
            await update.message.reply_text(
                "❌ Не удалось распарсить данные задачи. Проверьте формат."
            )
        
        # Сбрасываем состояние
        user_states.pop(user_id, None)
        
    elif state == 'creating_idea':
        # Парсим данные идеи
        idea_data = await parse_idea_data(text)
        if idea_data:
            result = await bot_manager.notion_manager.create_idea(idea_data)
            
            if result.success:
                await update.message.reply_text(
                    f"💡 Идея создана!\n"
                    f"🔗 [Открыть в Notion]({result.data['url']})",
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
            else:
                await update.message.reply_text(
                    f"❌ Ошибка создания идеи: {result.error}"
                )
        else:
            await update.message.reply_text(
                "❌ Не удалось распарсить данные идеи. Проверьте формат."
            )
        
        # Сбрасываем состояние
        user_states.pop(user_id, None)
        
    else:
        # Обычное сообщение - пытаемся создать идею автоматически
        try:
            analysis = await bot_manager.llm_processor.parse_natural_language(text)
            
            if analysis.get('name'):
                result = await bot_manager.notion_manager.create_idea(analysis)
                
                if result.success:
                    await update.message.reply_text(
                        f"💡 Автоматически создана идея!\n"
                        f"📝 {analysis['name']}\n"
                        f"🔗 [Открыть в Notion]({result.data['url']})",
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                else:
                    await update.message.reply_text(
                        "❌ Не удалось создать идею автоматически"
                    )
            else:
                await update.message.reply_text(
                    "💭 Получил ваше сообщение, но не смог определить что с ним делать"
                )
                
        except Exception as e:
            logger.error(f"Ошибка обработки текста: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке сообщения"
            )

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

async def parse_task_data(text: str) -> Optional[Dict[str, Any]]:
    """Парсинг данных задачи из текста"""
    try:
        lines = text.strip().split('\n')
        task_data = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['название', 'name', 'title']:
                    task_data['title'] = value
                elif key in ['описание', 'description']:
                    task_data['description'] = value
                elif key in ['статус', 'status']:
                    task_data['status'] = value
                elif key in ['приоритет', 'priority']:
                    task_data['priority'] = value
        
        # Проверяем обязательные поля
        if 'title' not in task_data:
            return None
            
        return task_data
        
    except Exception as e:
        logger.error(f"Ошибка парсинга задачи: {e}")
        return None

async def parse_idea_data(text: str) -> Optional[Dict[str, Any]]:
    """Парсинг данных идеи из текста"""
    try:
        lines = text.strip().split('\n')
        idea_data = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['название', 'name']:
                    idea_data['name'] = value
                elif key in ['описание', 'description']:
                    idea_data['description'] = value
                elif key in ['теги', 'tags']:
                    idea_data['tags'] = [tag.strip() for tag in value.split(',')]
                elif key in ['важность', 'importance']:
                    try:
                        idea_data['importance'] = int(value)
                    except:
                        idea_data['importance'] = 5
        
        # Проверяем обязательные поля
        if 'name' not in idea_data:
            return None
            
        return idea_data
        
    except Exception as e:
        logger.error(f"Ошибка парсинга идеи: {e}")
        return None

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling update: {context.error}")
    
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Произошла ошибка. Попробуйте позже."
        )

def main():
    """Запуск бота"""
    print("🚀 Запуск улучшенного бота...")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(MessageHandler(filters.PHOTO, handle_file))
    application.add_handler(MessageHandler(filters.VIDEO, handle_file))
    application.add_handler(MessageHandler(filters.AUDIO, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    print("✅ Улучшенный бот запущен!")
    print("📋 Доступные команды:")
    print("   /start - Главное меню")
    print("   Отправка файлов - Автоматическая обработка")
    print("   Текстовые сообщения - Создание идей")
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()