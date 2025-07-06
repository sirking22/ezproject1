#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any, List, Optional
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
)
from notion_client import AsyncClient
import aiohttp

# Импортируем LLM сервис
from llm_service import OpenRouterLLM

# --- Настройка логирования ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_bot_v3.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Конфиг ---
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_IDEAS_DB_ID = os.getenv('NOTION_IDEAS_DB_ID', 'ad92a6e21485428c84de8587706b3be1')
YA_TOKEN = os.getenv('YA_ACCESS_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logger.info(f"Токены загружены: Notion={bool(NOTION_TOKEN)}, Yandex={bool(YA_TOKEN)}, Telegram={bool(TELEGRAM_TOKEN)}")

# Инициализируем LLM сервис
try:
    llm_service = OpenRouterLLM()
    logger.info("✅ LLM сервис инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации LLM: {e}")
    llm_service = None

YANDEX_BASE_URL = "https://cloud-api.yandex.net/v1/disk"

# --- Состояния пользователей ---
user_states = {}
file_queues = {}
processing_users = set()
file_timestamps = {}

# --- Вспомогательные функции ---

def is_url(text: str) -> bool:
    """Проверяет, содержит ли текст URL"""
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    return bool(re.search(url_pattern, text))

def extract_urls(text: str) -> List[str]:
    """Извлекает все URL из текста"""
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    return re.findall(url_pattern, text)

def clean_text_from_urls(text: str) -> str:
    """Удаляет URL из текста, оставляя только описание"""
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    return re.sub(url_pattern, '', text).strip()

async def create_yandex_folder(folder_name: str) -> Dict[str, Any]:
    """Создает папку в Яндекс.Диске"""
    headers = {"Authorization": f"OAuth {YA_TOKEN}"}
    folder_path = f"/telegram_uploads/{folder_name}"
    
    async with aiohttp.ClientSession() as session:
        url = f"{YANDEX_BASE_URL}/resources"
        params = {"path": folder_path}
        async with session.put(url, params=params, headers=headers) as resp:
            if resp.status in [201, 409]:
                logger.info(f"Папка {folder_name} создана/существует")
                return {'success': True, 'path': folder_path}
            else:
                error_text = await resp.text()
                logger.error(f"Ошибка создания папки: {resp.status} - {error_text}")
                return {'success': False, 'error': f"Ошибка создания папки: {resp.status}"}

async def upload_to_yandex_folder(telegram_file_url: str, filename: str, folder_name: str) -> Dict[str, Any]:
    """Загружает файл в папку на Яндекс.Диске"""
    logger.info(f"Загружаю {filename} в папку {folder_name}")
    
    remote_path = f"/telegram_uploads/{folder_name}/{filename}"
    headers = {"Authorization": f"OAuth {YA_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        # Получаем ссылку для загрузки
        url = f"{YANDEX_BASE_URL}/resources/upload"
        params = {"path": remote_path, "overwrite": "true"}
        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                logger.error(f"Ошибка получения ссылки Yandex: {resp.status} - {error_text}")
                return {'success': False, 'error': f"Ошибка получения ссылки: {resp.status}", 'url': None}
            upload_data = await resp.json()
            upload_url = upload_data["href"]
        
        # Скачиваем файл из Telegram
        async with session.get(telegram_file_url) as tg_resp:
            if tg_resp.status != 200:
                logger.error(f"Ошибка получения файла из Telegram: {tg_resp.status}")
                return {'success': False, 'error': f"Ошибка получения файла из Telegram: {tg_resp.status}", 'url': None}
            file_data = await tg_resp.read()
        
        # Загружаем в Yandex Disk
        async with session.put(upload_url, data=file_data, headers={"Content-Type": "application/octet-stream"}) as put_resp:
            if put_resp.status != 201:
                error_text = await put_resp.text()
                logger.error(f"Ошибка загрузки в Yandex Disk: {put_resp.status} - {error_text}")
                return {'success': False, 'error': f"Ошибка загрузки в Yandex Disk: {put_resp.status}", 'url': None}
        
        # Делаем папку публичной
        pub_url = f"{YANDEX_BASE_URL}/resources/publish"
        folder_path = f"/telegram_uploads/{folder_name}"
        params = {"path": folder_path}
        async with session.put(pub_url, params=params, headers=headers) as resp:
            pass
        
        # Получаем публичную ссылку на папку
        meta_url = f"{YANDEX_BASE_URL}/resources"
        async with session.get(meta_url, params={"path": folder_path}, headers=headers) as meta_resp:
            meta_data = await meta_resp.json()
            public_url = meta_data.get("public_url")
        
        return {'success': True, 'url': public_url, 'filename': filename, 'folder': folder_name}

async def create_notion_idea(fields: Dict[str, Any], file_url: str, folder_name: str):
    """Создает новую идею в Notion"""
    client = AsyncClient(auth=NOTION_TOKEN)
    
    try:
        properties = {
            "Name": {"title": [{"text": {"content": fields.get('name', 'Без названия')}}]},
            "Описание": {"rich_text": [{"text": {"content": fields.get('description', '')}}]},
            "Теги": {"rich_text": [{"text": {"content": fields.get('tags', '')}}]},
            "Статус": {"select": {"name": "Новое"}},
            "Приоритет": {"select": {"name": "Средний"}},
            "Тип": {"select": {"name": "Идея"}},
        }
        
        if file_url:
            properties["Файлы"] = {"url": file_url}
        
        # Добавляем URL если есть
        urls = fields.get('urls', [])
        if urls:
            properties["URL"] = {"url": urls[0]}
        
        response = await client.pages.create(
            parent={"database_id": NOTION_IDEAS_DB_ID},
            properties=properties
        )
        
        return {'success': True, 'id': response['id'], 'url': response['url']}
    except Exception as e:
        logger.error(f"Ошибка создания идеи в Notion: {e}")
        return {'success': False, 'error': str(e)}

# Остальные функции остаются без изменений...
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **Улучшенный бот v3** запущен!\n\n"
        "📁 Отправь файлы или опиши идею\n"
        "🤖 Команды: /llm, /queue, /mass_import"
    )

def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск улучшенного бота v3...")
    
    if not all([NOTION_TOKEN, YA_TOKEN, TELEGRAM_TOKEN]):
        logger.error("❌ Отсутствуют необходимые токены!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    
    logger.info("✅ Улучшенный бот v3 готов к работе!")
    
    # Запускаем бота
    try:
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")

if __name__ == "__main__":
    # Исправляем event loop для Windows
    import sys
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    main() 