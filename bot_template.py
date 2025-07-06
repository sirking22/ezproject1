#!/usr/bin/env python3
"""
Шаблон для Telegram ботов с базовой инфраструктурой
"""
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
)
from notion_client import AsyncClient
import aiohttp

# --- Загрузка переменных окружения ---
load_dotenv()

# --- Настройка логирования ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Конфигурация ---
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_MATERIALS_DB_ID = os.getenv('NOTION_MATERIALS_DB_ID')
NOTION_IDEAS_DB_ID = os.getenv('NOTION_IDEAS_DB_ID')
YA_TOKEN = os.getenv('YA_ACCESS_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# --- Проверка переменных окружения ---
def check_environment():
    """Проверка всех необходимых переменных"""
    required_vars = {
        'TELEGRAM_BOT_TOKEN': TELEGRAM_TOKEN,
        'NOTION_TOKEN': NOTION_TOKEN,
        'YA_ACCESS_TOKEN': YA_TOKEN,
        'NOTION_MATERIALS_DB_ID': NOTION_MATERIALS_DB_ID,
        'NOTION_IDEAS_DB_ID': NOTION_IDEAS_DB_ID
    }
    
    missing = [var for var, value in required_vars.items() if not value]
    
    if missing:
        logger.error(f"Missing required environment variables: {missing}")
        return False
    
    logger.info("✅ All environment variables loaded successfully")
    return True

# --- Основные функции ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot")
    
    await update.message.reply_text(
        "🤖 Бот запущен!\n"
        "Отправьте файл для загрузки в Yandex Disk и создания записи в Notion."
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик файлов"""
    user_id = update.effective_user.id
    logger.info(f"Received file from user {user_id}")
    
    # TODO: Реализовать обработку файлов
    await update.message.reply_text("📁 Файл получен. Обработка...")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    text = update.message.text
    logger.info(f"Received text from user {user_id}: {text}")
    
    # TODO: Реализовать обработку текста
    await update.message.reply_text("💬 Текст получен.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback запросов"""
    query = update.callback_query
    user_id = query.from_user.id
    logger.info(f"Received callback from user {user_id}: {query.data}")
    
    # TODO: Реализовать обработку callback
    await query.answer("✅ Обработано")

async def main():
    """Основная функция"""
    logger.info("Starting bot...")
    
    # Проверяем переменные окружения
    if not check_environment():
        logger.error("Environment check failed!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("✅ Bot started successfully!")
    
    # Запускаем бота
    await application.run_polling()

if __name__ == "__main__":
    # Устанавливаем event loop policy для Windows
    import sys
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}") 