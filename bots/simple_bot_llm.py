#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ОПТИМИЗИРОВАННЫЙ TELEGRAM БОТ С LLM
Быстрая загрузка файлов + понимание разговорного языка
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
)
from notion_client import AsyncClient
import aiohttp
import httpx
from dotenv import load_dotenv
import tempfile
import cv2
import json

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_MATERIALS_DB_ID = os.getenv('NOTION_MATERIALS_DB_ID', '1d9ace03d9ff804191a4d35aeedcbbd4')
NOTION_IDEAS_DB_ID = os.getenv('NOTION_IDEAS_DB_ID', 'ad92a6e21485428c84de8587706b3be1')
YA_TOKEN = os.getenv('YA_ACCESS_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-DzPhbaSCgP7_YPxOuPvMOA')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://hubai.loe.gg/v1')

if not all([NOTION_TOKEN, YA_TOKEN, TELEGRAM_TOKEN]):
    logger.error("Отсутствуют необходимые токены!")
    exit(1)

logger.info("✅ Токены загружены")

# Состояния пользователей
user_states = {}

class LLMProcessor:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
    
    async def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """Парсит разговорный текст в структурированные поля"""
        try:
            prompt = f"""
            Пользователь описал идею в разговорном стиле. Извлеки структурированную информацию:
            
            Текст: "{text}"
            
            Верни JSON с полями:
            - name: название идеи (обязательно)
            - description: описание (если есть)
            - tags: теги через запятую (если есть)
            - importance: важность от 1 до 5 (если упоминается)
            - status: статус (если упоминается)
            
            Примеры:
            - "Хочу сделать бота для автоматизации" → {{"name": "Бот для автоматизации", "description": "Автоматизация процессов", "tags": "автоматизация, бот", "importance": 4}}
            - "Нужно приложение для управления задачами" → {{"name": "Приложение для управления задачами", "description": "Система управления задачами", "tags": "задачи, управление", "importance": 3}}
            
            Верни только JSON без дополнительного текста.
            """
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Пытаемся извлечь JSON
                    try:
                        # Ищем JSON в ответе
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start != -1 and end != 0:
                            json_str = content[start:end]
                            parsed = json.loads(json_str)
                            logger.info(f"LLM распарсил: {parsed}")
                            return parsed
                    except json.JSONDecodeError:
                        pass
                    
                    # Fallback: простой парсинг
                    return self.simple_parse(text)
                else:
                    logger.error(f"Ошибка LLM API: {response.status_code}")
                    return self.simple_parse(text)
                    
        except Exception as e:
            logger.error(f"Ошибка LLM обработки: {e}")
            return self.simple_parse(text)
    
    def simple_parse(self, text: str) -> Dict[str, Any]:
        """Простой парсинг без LLM"""
        fields = {}
        
        # Ищем название (первая фраза до запятой или точка)
        parts = text.split(',')
        if parts:
            name_part = parts[0].strip()
            if ':' in name_part:
                name_part = name_part.split(':', 1)[1].strip()
            fields['name'] = name_part
        
        # Ищем описание
        if len(parts) > 1:
            desc_parts = []
            for part in parts[1:]:
                part = part.strip()
                if ':' in part:
                    key, value = part.split(':', 1)
                    key = key.strip().lower()
                    if key in ['описание', 'description']:
                        fields['description'] = value.strip()
                    elif key in ['теги', 'tags']:
                        fields['tags'] = value.strip()
                    elif key in ['важность', 'importance']:
                        try:
                            fields['importance'] = int(value.strip())
                        except:
                            pass
                else:
                    desc_parts.append(part)
            
            if desc_parts and 'description' not in fields:
                fields['description'] = ', '.join(desc_parts)
        
        return fields

class YandexUploader:
    def __init__(self):
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {YA_TOKEN}"}
        self.timeout = aiohttp.ClientTimeout(total=120)
    
    async def upload_file(self, file_url: str, filename: str) -> Dict[str, Any]:
        """Быстрая загрузка файла в Yandex.Disk"""
        remote_path = f"/telegram_uploads/{filename}"
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            # 1. Получаем ссылку для загрузки
            upload_url = f"{self.base_url}/resources/upload"
            params = {"path": remote_path, "overwrite": "true"}
            
            async with session.get(upload_url, params=params, headers=self.headers) as resp:
                if resp.status != 200:
                    return {'success': False, 'error': f"Ошибка получения ссылки: {resp.status}"}
                upload_data = await resp.json()
                href = upload_data["href"]
            
            # 2. Скачиваем и загружаем файл
            try:
                async with session.get(file_url) as file_resp:
                    if file_resp.status != 200:
                        return {'success': False, 'error': "Не удалось скачать файл"}
                    file_data = await file_resp.read()
                
                async with session.put(href, data=file_data, headers={"Content-Type": "application/octet-stream"}) as put_resp:
                    if put_resp.status != 201:
                        return {'success': False, 'error': f"Ошибка загрузки: {put_resp.status}"}
            except Exception as e:
                return {'success': False, 'error': f"Ошибка загрузки: {e}"}
            
            # 3. Публикуем файл
            pub_url = f"{self.base_url}/resources/publish"
            async with session.put(pub_url, params={"path": remote_path}, headers=self.headers):
                pass
            
            # 4. Получаем публичную ссылку
            meta_url = f"{self.base_url}/resources"
            async with session.get(meta_url, params={"path": remote_path}, headers=self.headers) as meta_resp:
                meta_data = await meta_resp.json()
                public_url = meta_data.get("public_url")
                
                if not public_url:
                    return {'success': False, 'error': 'Не удалось получить публичную ссылку'}
                
                # 5. Получаем preview для cover
                preview_url = await self.get_preview_url(public_url)
                
                return {
                    'success': True, 
                    'url': public_url, 
                    'preview_url': preview_url,
                    'filename': filename
                }
    
    async def get_preview_url(self, public_url: str) -> str:
        """Получить preview или public_url для cover"""
        try:
            api_url = 'https://cloud-api.yandex.net/v1/disk/public/resources'
            params = {'public_key': public_url}
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(api_url, params=params)
                if resp.status_code == 200:
                    meta = resp.json()
                    return meta.get('preview') or meta.get('public_url', '')
        except Exception as e:
            logger.error(f"Ошибка получения preview: {e}")
        return ''

class VideoProcessor:
    @staticmethod
    async def extract_frame(video_url: str) -> Optional[str]:
        """Извлечь кадр из видео"""
        try:
            # Скачиваем видео во временный файл
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as resp:
                    if resp.status != 200:
                        return None
                    video_data = await resp.read()
            
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
                f.write(video_data)
                temp_video = f.name
            
            # Извлекаем кадр
            cap = cv2.VideoCapture(temp_video)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                os.unlink(temp_video)
                return None
            
            # Сохраняем кадр
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                cv2.imwrite(f.name, frame)
                frame_path = f.name
            
            os.unlink(temp_video)
            return frame_path
            
        except Exception as e:
            logger.error(f"Ошибка извлечения кадра: {e}")
            return None

class NotionManager:
    def __init__(self):
        self.client = AsyncClient(auth=NOTION_TOKEN)
    
    async def create_idea(self, fields: Dict[str, Any], file_url: str, file_name: str):
        """Создать запись в базе идей"""
        properties = {
            "Name": {"title": [{"text": {"content": fields.get('name', file_name)}}]},
            "URL": {"url": file_url},
            "Статус": {"status": {"name": fields.get('status', 'To do')}},
        }
        
        if fields.get('description'):
            properties["Описание"] = {"rich_text": [{"text": {"content": fields['description']}}]}
        
        if fields.get('tags'):
            properties["Теги"] = {"multi_select": [{"name": tag.strip()} for tag in fields['tags'].split(',')]}
        
        if fields.get('importance'):
            properties["Важность"] = {"number": int(fields['importance'])}
        
        return await self.client.pages.create(
            parent={"database_id": NOTION_IDEAS_DB_ID},
            properties=properties
        )
    
    async def create_material(self, fields: Dict[str, Any], file_url: str, file_name: str):
        """Создать запись в базе материалов"""
        properties = {
            "Name": {"title": [{"text": {"content": fields.get('name', file_name)}}]},
            "URL": {"url": file_url},
            "Статус": {"status": {"name": fields.get('status', 'To do')}},
        }
        
        if fields.get('description'):
            properties["Описание"] = {"rich_text": [{"text": {"content": fields['description']}}]}
        
        if fields.get('tags'):
            properties["Теги"] = {"multi_select": [{"name": tag.strip()} for tag in fields['tags'].split(',')]}
        
        if fields.get('importance'):
            properties["Важность"] = {"number": int(fields['importance'])}
        
        return await self.client.pages.create(
            parent={"database_id": NOTION_MATERIALS_DB_ID},
            properties=properties
        )
    
    async def set_cover(self, page_id: str, cover_url: str):
        """Установить cover для страницы"""
        try:
            await self.client.pages.update(
                page_id=page_id,
                cover={
                    "type": "external",
                    "external": {"url": cover_url}
                }
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка установки cover: {e}")
            return False

# Глобальные экземпляры
yandex = YandexUploader()
notion = NotionManager()
video_processor = VideoProcessor()
llm = LLMProcessor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Отправь файл, и я загружу его в Яндекс.Диск и создам карточку в Notion!\n\n"
        "💡 Можешь описать идею разговорным языком, например:\n"
        "• 'Хочу сделать бота для автоматизации задач'\n"
        "• 'Нужно приложение для управления проектами, важность высокая'\n"
        "• 'Идея для мобильного приложения, теги: разработка, мобильные'"
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Определяем тип файла
    if update.message.document:
        file_obj = update.message.document
        file_type = "document"
        file_name = file_obj.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    elif update.message.photo:
        file_obj = update.message.photo[-1]
        file_type = "photo"
        file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    elif update.message.video:
        file_obj = update.message.video
        file_type = "video"
        file_name = file_obj.file_name or f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    elif update.message.audio:
        file_obj = update.message.audio
        file_type = "audio"
        file_name = file_obj.file_name or f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    else:
        await update.message.reply_text("❌ Не удалось определить тип файла")
        return
    
    # Получаем ссылку на файл
    file_info = await context.bot.get_file(file_obj.file_id)
    if str(file_info.file_path).startswith("http"):
        file_url = file_info.file_path
    else:
        file_url = f"https://api.telegram.org/file/bot{context.bot.token}/{file_info.file_path}"
    
    await update.message.reply_text(f"🚀 Загружаю {file_name}...")
    
    try:
        start_time = time.time()
        
        if file_type == "video":
            # Загружаем видео
            video_result = await yandex.upload_file(file_url, file_name)
            if not video_result['success']:
                await update.message.reply_text(f"❌ Ошибка загрузки видео: {video_result['error']}")
                return
            
            # Извлекаем кадр
            frame_path = await video_processor.extract_frame(file_url)
            if frame_path:
                frame_name = f"{file_name}_frame.jpg"
                frame_result = await yandex.upload_file(f"file://{frame_path}", frame_name)
                os.unlink(frame_path)
                
                if frame_result['success']:
                    cover_url = frame_result['preview_url']
                else:
                    cover_url = video_result['preview_url']
            else:
                cover_url = video_result['preview_url']
            
            upload_result = video_result
            elapsed = time.time() - start_time
            logger.info(f"Видео обработано за {elapsed:.1f}с")
            
        else:
            # Обычный файл
            upload_result = await yandex.upload_file(file_url, file_name)
            cover_url = upload_result.get('preview_url', '')
        
        if not upload_result['success']:
            await update.message.reply_text(f"❌ Ошибка загрузки: {upload_result['error']}")
            return
        
        await update.message.reply_text(f"✅ Файл загружен: {upload_result['url']}")
        
        # Сохраняем состояние
        user_states[user_id] = {
            'database_choice': None,
            'file_url': upload_result['url'],
            'file_name': file_name,
            'cover_url': cover_url
        }
        
        # Показываем выбор базы
        keyboard = [
            [InlineKeyboardButton("📋 Материалы", callback_data="db_materials")],
            [InlineKeyboardButton("💡 Идеи", callback_data="db_ideas")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "В какую базу данных создать запись?",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки файла: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        return
    
    text = update.message.text
    
    # Парсим разговорный язык через LLM
    await update.message.reply_text("🤖 Обрабатываю описание...")
    fields = await llm.parse_natural_language(text)
    
    if not fields.get('name'):
        await update.message.reply_text("❌ Не удалось извлечь название. Попробуй описать более подробно.")
        return
    
    try:
        state = user_states[user_id]
        file_url = state['file_url']
        file_name = state['file_name']
        cover_url = state.get('cover_url', '')
        database_choice = state['database_choice']
        
        # Создаем запись в Notion
        if database_choice == 'materials':
            notion_resp = await notion.create_material(fields, file_url, file_name)
            db_name = "Материалы"
        else:
            notion_resp = await notion.create_idea(fields, file_url, file_name)
            db_name = "Идеи"
        
        notion_id = notion_resp.get('id', '')
        notion_url = f"https://notion.so/{notion_id.replace('-', '')}"
        
        await update.message.reply_text(f"📋 Карточка создана в '{db_name}': {notion_url}")
        
        # Устанавливаем cover (без сообщения в Telegram)
        if cover_url and notion_id:
            success = await notion.set_cover(notion_id, cover_url)
            if success:
                logger.info(f"Cover установлен для {notion_id}: {cover_url}")
            else:
                logger.error(f"Ошибка установки cover для {notion_id}")
        
        # Очищаем состояние
        user_states.pop(user_id, None)
        
    except Exception as e:
        logger.error(f"Ошибка создания записи: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in user_states:
        return
    
    if query.data == "db_materials":
        user_states[user_id]['database_choice'] = 'materials'
        await query.edit_message_text(
            "📋 Создаем запись в базе 'Материалы'.\n\n"
            "💬 Опиши материал разговорным языком:\n"
            "• 'Презентация по маркетингу'\n"
            "• 'Видеоурок по программированию, важность высокая'\n"
            "• 'Документ с планами, теги: планирование, стратегия'"
        )
    elif query.data == "db_ideas":
        user_states[user_id]['database_choice'] = 'ideas'
        await query.edit_message_text(
            "💡 Создаем запись в базе 'Идеи'.\n\n"
            "💬 Опиши идею разговорным языком:\n"
            "• 'Хочу сделать бота для автоматизации'\n"
            "• 'Идея мобильного приложения, важность высокая'\n"
            "• 'Нужно приложение для управления задачами, теги: разработка, продуктивность'"
        )

def main():
    logger.info("🚀 Запуск оптимизированного бота с LLM...")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("✅ Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main() 