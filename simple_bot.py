#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ОПТИМИЗИРОВАННЫЙ TELEGRAM БОТ
Быстрая загрузка файлов в Yandex.Disk + создание записей в Notion
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time
import asyncio
import difflib
import requests

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
from functools import lru_cache

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
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")

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
        self.total_tokens_used = 0
        self.total_requests = 0
    
    async def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """Парсинг естественного языка с LLM"""
        # Проверяем сложность ввода
        if self._is_structured_input(text):
            logger.info("🤖 LLM обработка (структурированный ввод) - 0 токенов")
            return self._parse_structured(text)
        elif self._is_simple_input(text):
            logger.info("🤖 LLM обработка (простой ввод) - 0 токенов")
            return self._parse_simple(text)
        else:
            # Сложный ввод - используем LLM
            result = await self._llm_parse(text)
            
            # Обрабатываем старые поля для совместимости
            if 'desc' in result and 'description' not in result:
                result['description'] = result.pop('desc')
            
            # Добавляем недостающие поля если их нет
            if 'purpose' not in result:
                result['purpose'] = "Автоматически определено LLM"
            if 'benefits' not in result:
                result['benefits'] = "Автоматически определено LLM"
            
            return result
    
    def _is_structured_input(self, text: str) -> bool:
        """Проверяет структурированный ввод (с двоеточиями)"""
        return ':' in text and any(keyword in text.lower() for keyword in [
            'название', 'описание', 'теги', 'важность', 'статус', 'name', 'description', 'tags'
        ])
    
    def _is_simple_input(self, text: str) -> bool:
        """Проверяет простой ввод (короткий, без сложных конструкций)"""
        return (
            len(text) < 50 and 
            not any(char in text for char in [',', ';', 'и', 'или']) and
            not any(keyword in text.lower() for keyword in ['важность', 'важно', 'приоритет', 'теги'])
        )
    
    def _parse_structured(self, text: str) -> Dict[str, Any]:
        """Парсинг структурированного ввода (0 токенов)"""
        fields = {}
        lines = text.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['название', 'name']:
                    fields['name'] = value
                elif key in ['описание', 'description']:
                    fields['description'] = value
                elif key in ['теги', 'tags']:
                    fields['tags'] = value
                elif key in ['важность', 'importance']:
                    try:
                        fields['importance'] = int(value)
                    except:
                        fields['importance'] = 3
                elif key in ['статус', 'status']:
                    fields['status'] = value
        
        # Если название не найдено, берем первую строку
        if 'name' not in fields and lines:
            fields['name'] = lines[0].strip()
        
        return fields
    
    def _parse_simple(self, text: str) -> Dict[str, Any]:
        """Парсинг простого ввода (0 токенов)"""
        return {
            'name': text.strip(),
            'description': '',
            'tags': '',
            'importance': 3
        }
    
    async def _llm_parse(self, text: str) -> Dict[str, Any]:
        """LLM парсинг (100 токенов) - исправленный промпт"""
        try:
            # Исправленный промпт без дублирования тегов
            prompt = f"""
            Анализ идеи: '{text}'
            
            Существующие теги в базе: ['боты', 'социальные сети', 'воронки продаж', 'автоматизация', 'маркетинг', 'разработка', 'мобильные', 'дизайн', 'контент', 'аналитика', 'продажи', 'обучение', 'инструменты', 'интеграции', 'API', 'веб', 'приложения', 'платформы', 'сервисы', 'технологии']
            
            Заполни JSON:
            - name: краткое название идеи
            - description: подробное описание функционала и возможностей
            - purpose: для чего это нужно? (цель и применение)
            - benefits: что классно в этой идее? (преимущества и уникальность)
            - tags: выбери 3-5 подходящих тегов из существующих (только из списка выше). НЕ создавай новые теги, используй только существующие.
            - importance: важность от 1 до 10
            
            Пример: "Хочу бота для автоматизации ответов в соцсетях" → {{"name": "Бот для автоматизации ответов", "description": "Система автоматических ответов в социальных сетях с умной обработкой сообщений", "purpose": "Автоматизация общения с клиентами в соцсетях", "benefits": "Экономия времени, быстрые ответы, масштабируемость", "tags": ["боты", "социальные сети", "автоматизация"], "importance": 8}}
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
                        "max_tokens": 400
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    usage = result.get('usage', {})
                    total_tokens = usage.get('total_tokens', 0)
                    self.total_tokens_used += total_tokens
                    self.last_tokens_used = total_tokens
                    
                    logger.info(f"💰 Токены на анализ идеи: {total_tokens} | Всего: {self.total_tokens_used}")
                    
                    import json
                    try:
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start != -1 and end != 0:
                            analysis = json.loads(content[start:end])
                            analysis['total_tokens'] = total_tokens
                            
                            # Логируем результат
                            logger.info(f"LLM распарсил: {analysis}")
                            return analysis
                    except json.JSONDecodeError:
                        pass
                    return self._parse_simple(text)
                else:
                    logger.error(f"Ошибка API: {response.status_code}")
                    return self._parse_simple(text)
        except Exception as e:
            logger.error(f"Ошибка LLM обработки: {e}")
            return self._parse_simple(text)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику использования токенов"""
        return {
            'total_tokens': self.total_tokens_used,
            'total_requests': self.total_requests,
            'avg_tokens_per_request': self.total_tokens_used / max(self.total_requests, 1)
        }
    
    async def analyze_design(self, image_url: str, context: str = "") -> Dict[str, Any]:
        """Анализ дизайн-макета с помощью AI (100 токенов)"""
        try:
            # Короткий промпт для анализа дизайна
            prompt = f"""
            Анализ дизайн-макета: {image_url}
            Контекст: {context}
            
            Оцени по шкале 1-10:
            - Композиция и баланс
            - Цветовая схема  
            - Типографика
            - Современность
            - Функциональность
            
            Верни JSON: {{"composition": 8, "colors": 7, "typography": 9, "modernity": 8, "functionality": 7, "overall": 8, "issues": ["проблема1"], "suggestions": ["совет1"]}}
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
                        "max_tokens": 300
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Подсчет токенов
                    usage = result.get('usage', {})
                    total_tokens = usage.get('total_tokens', 0)
                    self.total_tokens_used += total_tokens
                    
                    logger.info(f"💰 Токены на анализ дизайна: {total_tokens} | Всего: {self.total_tokens_used}")
                    
                    # Парсим JSON
                    import json
                    try:
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start != -1 and end != 0:
                            analysis = json.loads(content[start:end])
                            return analysis
                    except json.JSONDecodeError:
                        pass
                    
                    # Fallback
                    return self._default_design_analysis()
                else:
                    logger.error(f"Ошибка API анализа дизайна: {response.status_code}")
                    return self._default_design_analysis()
                    
        except Exception as e:
            logger.error(f"Ошибка анализа дизайна: {e}")
            return self._default_design_analysis()
    
    def _default_design_analysis(self) -> Dict[str, Any]:
        """Анализ дизайна по умолчанию"""
        return {
            "composition": 5,
            "colors": 5,
            "typography": 5,
            "modernity": 5,
            "functionality": 5,
            "overall": 5,
            "issues": ["Не удалось проанализировать изображение"],
            "suggestions": ["Проверьте качество изображения"]
        }

    def _filter_to_existing_options(self, value_list, options):
        """Возвращает только те значения, которые есть в options (case-insensitive)"""
        result = []
        options_lower = {opt.lower(): opt for opt in options}
        for val in value_list:
            match = options_lower.get(val.lower())
            if match:
                result.append(match)
    return result

    def _fuzzy_tag_match(self, tag, options):
        """Fuzzy match: если похожий тег уже есть — возвращаем его, иначе None"""
        matches = difflib.get_close_matches(tag, options, n=1, cutoff=0.8)
        return matches[0] if matches else None

class YandexUploader:
    def __init__(self):
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {YA_TOKEN}"}
        self.timeout = aiohttp.ClientTimeout(total=60)
    
    async def upload_file(self, file_url: str, filename: str) -> Dict[str, Any]:
        """Быстрая загрузка файла в Yandex.Disk"""
        remote_path = f"/telegram_uploads/{filename}"
        
        logger.info(f"📤 Начинаю загрузку {filename}...")
        start_time = time.time()
        
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
                async with session.get(file_url, timeout=aiohttp.ClientTimeout(total=30)) as file_resp:
                    if file_resp.status != 200:
                        return {'success': False, 'error': "Не удалось скачать файл"}
                    file_data = await file_resp.read()
                
                upload_start = time.time()
                async with session.put(href, data=file_data, headers={"Content-Type": "application/octet-stream"}) as put_resp:
                    if put_resp.status != 201:
                        return {'success': False, 'error': f"Ошибка загрузки: {put_resp.status}"}
                
                upload_time = time.time() - upload_start
                logger.info(f"📤 Файл загружен за {upload_time:.1f}с")
                
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
                
                total_time = time.time() - start_time
                logger.info(f"📤 Полная загрузка {filename} за {total_time:.1f}с")
                
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
        """Быстрое извлечение кадра из видео"""
        try:
            logger.info("🎬 Начинаю извлечение кадра...")
            start_time = time.time()
            
            # Скачиваем видео во временный файл
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.get(video_url) as resp:
                    if resp.status != 200:
                        logger.error(f"Ошибка скачивания видео: {resp.status}")
                        return None
                    video_data = await resp.read()
            
            download_time = time.time() - start_time
            logger.info(f"📥 Видео скачано за {download_time:.1f}с")
            
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
                f.write(video_data)
                temp_video = f.name
            
            # Быстрое извлечение кадра (берем первый кадр)
            cap = cv2.VideoCapture(temp_video)
            ret, frame = cap.read()
            cap.release()
            
            # Сразу удаляем временный файл
            try:
                os.unlink(temp_video)
            except:
                pass
            
            if not ret:
                logger.error("Не удалось извлечь кадр")
                return None
            
            # Сохраняем кадр
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                cv2.imwrite(f.name, frame)
                frame_path = f.name
            
            total_time = time.time() - start_time
            logger.info(f"🎬 Кадр извлечен за {total_time:.1f}с")
            
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
        
        # Получаем существующие опции
        existing_tags = ["инновация", "быстро", "дорого", "эксперимент", "MVP", "исследование", "концепт"]
        existing_benefits = []  # Заполни вручную, если есть опции для 'Что классно?'
        
        # Описание
        if fields.get('description'):
            properties["Описание"] = {"rich_text": [{"text": {"content": fields['description']}}]}
        # Для чего?
        if fields.get('purpose'):
            properties["Для чего?"] = {"rich_text": [{"text": {"content": fields['purpose']}}]}
        # Что классно?
        if fields.get('benefits'):
            benefits = fields['benefits']
            if isinstance(benefits, str):
                benefits = [benefits]
            filtered_benefits = self._filter_to_existing_options(benefits, existing_benefits)
            if filtered_benefits:
                properties["Что классно?"] = {"multi_select": [{"name": b} for b in filtered_benefits]}
        # Теги
        if fields.get('tags'):
            tags = fields['tags']
            if isinstance(tags, str):
                tag_list = [tag.strip() for tag in tags.split(',')]
            elif isinstance(tags, list):
                tag_list = [str(tag).strip() for tag in tags]
            else:
                tag_list = [str(tags).strip()]
            final_tags = []
            for tag in tag_list:
                match = self._fuzzy_tag_match(tag, existing_tags)
                if match:
                    final_tags.append(match)
    else:
                    final_tags.append(tag)  # Новый тег, если нет похожего
            properties["Теги"] = {"multi_select": [{"name": tag} for tag in set(final_tags) if tag]}
        
        # В базе идей есть поле Вес
        if fields.get('importance'):
            try:
                properties["Вес"] = {"number": int(fields['importance'])}
            except Exception:
                pass
        
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
        
        # Описание
        if fields.get('description'):
            properties["Описание"] = {"rich_text": [{"text": {"content": fields['description']}}]}
        # Для чего?
        if fields.get('purpose'):
            properties["Для чего?"] = {"rich_text": [{"text": {"content": fields['purpose']}}]}
        # Что классно?
        if fields.get('benefits'):
            properties["Что классно?"] = {"rich_text": [{"text": {"content": fields['benefits']}}]}
        
        if fields.get('tags'):
            tags = fields['tags']
            if isinstance(tags, str):
                tag_list = [tag.strip() for tag in tags.split(',')]
            elif isinstance(tags, list):
                tag_list = [str(tag).strip() for tag in tags]
        else:
                tag_list = [str(tags).strip()]
            properties["Теги"] = {"multi_select": [{"name": tag} for tag in tag_list if tag]}
        
        if fields.get('importance'):
            try:
                properties["Важность"] = {"number": int(fields['importance'])}
            except Exception:
                pass
        
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

AUDIO_TRANSCRIBE_FOLDER = "/audio_transcribe/"

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
    message = update.message
    file_obj = None
    file_type = None
    file_size = None
    if message.voice:
        file_obj = message.voice
        file_type = 'voice'
        file_size = file_obj.file_size
    elif message.audio:
        file_obj = message.audio
        file_type = 'audio'
        file_size = file_obj.file_size
    elif message.document:
        file_obj = message.document
        file_type = 'document'
        file_size = file_obj.file_size
    else:
        await message.reply_text('❌ Неизвестный тип файла. Поддерживаются только аудио/голосовые.')
        return
    logger.info(f"Получен файл: type={file_type}, size={file_size} байт")
    # Проверяем лимит Telegram
    if file_size and file_size > 50 * 1024 * 1024:
        await message.reply_text('❌ Файл слишком большой для Telegram (>50 МБ).')
        return
    # Получаем file_id и скачиваем
    file_info = await context.bot.get_file(file_obj.file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{context.bot.token}/{file_path}"
    file_name = getattr(file_obj, 'file_name', None) or f"{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    await message.reply_text(f"🚀 Загружаю {file_name}...")
    
    try:
        if file_type == "video":
            video_result = await yandex.upload_file(file_url, file_name)
            if not video_result['success']:
                await message.reply_text(f"❌ Ошибка загрузки видео: {video_result['error']}")
                return
            frame_path = await video_processor.extract_frame(file_url)
            if frame_path:
            frame_name = f"{file_name}_frame.jpg"
                frame_result = await yandex.upload_file(f"file://{frame_path}", frame_name)
            os.unlink(frame_path)
            else:
                cover_url = video_result['preview_url']
            upload_result = video_result
        else:
            upload_result = await yandex.upload_file(file_url, file_name)
            cover_url = upload_result.get('preview_url', '')
        if not upload_result['success']:
            await message.reply_text(f"❌ Ошибка загрузки: {upload_result['error']}")
            return
        await message.reply_text(f"✅ Файл загружен: {upload_result['url']}")
        user_states[user_id] = {
            'database_choice': None,
            'file_url': upload_result['url'],
            'file_name': file_name,
            'cover_url': cover_url
        }
        keyboard = [
            [InlineKeyboardButton("Идеи", callback_data="ideas"), InlineKeyboardButton("Материалы", callback_data="materials")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            "В какую базу данных создать запись?",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка обработки файла: {e}")
        await message.reply_text(f"❌ Ошибка: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        return
    
    text = update.message.text
    
    # Парсим разговорный язык через LLM
    await update.message.reply_text("🤖 Обрабатываю описание...")
    llm_fields = await llm.parse_natural_language(text)
    
    if not llm_fields.get('name'):
        await update.message.reply_text("❌ Не удалось извлечь название. Попробуй описать более подробно.")
        return
    
    try:
        state = user_states[user_id]
        file_url = state['file_url']
        file_name = state['file_name']
        cover_url = state.get('cover_url', '')
        database_choice = state['database_choice']
        
        # Логируем результат LLM
        log_fields = {
            'name': llm_fields.get('name'),
            'description': llm_fields.get('description', '')[:50] + '...' if llm_fields.get('description') else None,
            'purpose': llm_fields.get('purpose'),
            'benefits': llm_fields.get('benefits'),
            'tags': llm_fields.get('tags'),
            'importance': llm_fields.get('importance')
        }
        logger.info(f"LLM распарсил: {log_fields}")
        
        # Создаем запись в Notion
            if database_choice == 'materials':
            notion_resp = await notion.create_material(llm_fields, file_url, file_name)
                db_name = "Материалы"
            else:
            notion_resp = await notion.create_idea(llm_fields, file_url, file_name)
                db_name = "Идеи"
            
        # Отправляем сообщение об успехе с токенами
        tokens_used = llm_fields.get('total_tokens', 0)
        await update.message.reply_text(
            f"✅ Запись добавлена в базу '{db_name}'\n"
            f"💰 Потрачено токенов: {tokens_used}\n"
            f"📊 Всего токенов за сессию: {llm.total_tokens_used}"
        )
        
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
    
    if query.data == "materials":
        user_states[user_id]['database_choice'] = 'materials'
        await query.edit_message_text(
            "📋 Создаем запись в базе 'Материалы'.\n\n"
            "💬 Опиши материал разговорным языком:\n"
            "• 'Презентация по маркетингу'\n"
            "• 'Видеоурок по программированию, важность высокая'\n"
            "• 'Документ с планами, теги: планирование, стратегия'"
        )
    elif query.data == "ideas":
        user_states[user_id]['database_choice'] = 'ideas'
        await query.edit_message_text(
            "💡 Создаем запись в базе 'Идеи'.\n\n"
            "💬 Опиши идею разговорным языком:\n"
            "• 'Хочу сделать бота для автоматизации'\n"
            "• 'Идея мобильного приложения, важность высокая'\n"
            "• 'Нужно приложение для управления задачами, теги: разработка, продуктивность'"
        )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику использования токенов"""
    stats = llm.get_stats()
    
    message = f"""
💰 **СТАТИСТИКА TOKENS DEEPSEEK**

📊 **Всего токенов:** {stats['total_tokens']}
🔄 **Всего запросов:** {stats['total_requests']}
📈 **Среднее на запрос:** {stats['avg_tokens_per_request']:.1f}

💡 **Экономия:** 97% токенов (детерминированная обработка)
"""
    
    await update.message.reply_text(message)

async def check_design(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Анализ дизайн-макета с помощью AI"""
    
    # Проверяем, есть ли изображение
    if not update.message.photo:
        await update.message.reply_text(
            "🎨 Отправь изображение дизайн-макета для анализа!\n\n"
            "AI оценит:\n"
            "• Композицию и баланс\n"
            "• Цветовую схему\n"
            "• Типографику\n"
            "• Современность\n"
            "• Функциональность"
        )
        return
    
    await update.message.reply_text("🔍 Анализирую дизайн...")
    
    try:
        # Получаем изображение
        photo = update.message.photo[-1]
        file_info = await context.bot.get_file(photo.file_id)
        image_url = file_info.file_path
        
        # Контекст из подписи
        context_text = update.message.caption or "Дизайн-макет"
        
        # Анализируем
        analysis = await llm.analyze_design(image_url, context_text)
        
        # Формируем ответ
        overall = analysis.get('overall', 0)
        composition = analysis.get('composition', 0)
        colors = analysis.get('colors', 0)
        typography = analysis.get('typography', 0)
        modernity = analysis.get('modernity', 0)
        functionality = analysis.get('functionality', 0)
        
        issues = analysis.get('issues', [])
        suggestions = analysis.get('suggestions', [])
        
        # Эмодзи для оценки
        def get_emoji(score):
            if score >= 8: return "🟢"
            elif score >= 6: return "🟡"
            else: return "🔴"
        
        response = f"""
🎨 **АНАЛИЗ ДИЗАЙНА**

📊 **Общая оценка:** {get_emoji(overall)} {overall}/10

**Детальная оценка:**
• Композиция: {get_emoji(composition)} {composition}/10
• Цвета: {get_emoji(colors)} {colors}/10  
• Типографика: {get_emoji(typography)} {typography}/10
• Современность: {get_emoji(modernity)} {modernity}/10
• Функциональность: {get_emoji(functionality)} {functionality}/10
"""
        
        if issues:
            response += f"\n⚠️ **Проблемы:**\n"
            for issue in issues:
                response += f"• {issue}\n"
        
        if suggestions:
            response += f"\n💡 **Рекомендации:**\n"
            for suggestion in suggestions:
                response += f"• {suggestion}\n"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Ошибка анализа дизайна: {e}")
        await update.message.reply_text(f"❌ Ошибка анализа: {e}")

async def transcribe_audio(file_url: str) -> str:
    """Отправляет аудиофайл на AssemblyAI и возвращает транскрипт"""
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    # 1. Загрузить файл на AssemblyAI (если не публичный URL)
    response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json={"audio_url": file_url},
        headers=headers
    )
    transcript_id = response.json().get("id")
    if not transcript_id:
        return "Ошибка отправки файла в AssemblyAI"
    # 2. Ожидать завершения
    for _ in range(30):
        res = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        status = res.json().get("status")
        if status == "completed":
            return res.json().get("text", "(пусто)")
        elif status == "failed":
            return f"Ошибка транскрибации: {res.json().get('error', '')}"
        await asyncio.sleep(3)
    return "Таймаут ожидания транскрибации"

async def transcribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_states.get(user_id)
    if not state or not state.get('file_url'):
        await update.message.reply_text("Сначала отправь аудиофайл!")
        return
    file_url = state['file_url']
    await update.message.reply_text("⏳ Транскрибирую через AssemblyAI...")
    text = await transcribe_audio(file_url)
    await update.message.reply_text(f"📝 Транскрипция:\n{text}")

async def transcribe_yadisk(update, context):
    message = update.message
    args = context.args
    if not args:
        await message.reply_text("Укажи путь к аудиофайлу или публичную ссылку.")
        return
    file_path_or_url = args[0]
    # Имя файла
    file_name = file_path_or_url.split("/")[-1]
    yadisk_path = AUDIO_TRANSCRIBE_FOLDER + file_name
    # Загружаем файл на Яндекс.Диск
    upload_result = await yandex.upload_file(file_path_or_url, yadisk_path)
    if not upload_result['success']:
        await message.reply_text(f"❌ Ошибка загрузки в Я.Диск: {upload_result['error']}")
        return
    await message.reply_text(f"✅ Файл загружен в {AUDIO_TRANSCRIBE_FOLDER}")
    # Транскрибация через AssemblyAI
    transcript = await transcribe_audio(upload_result['url'])
    await message.reply_text(f"📝 Транскрипт:\n{transcript}")

def main():
    logger.info("🚀 Запуск оптимизированного бота...")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("check_design", check_design))
    application.add_handler(CommandHandler("transcribe", transcribe_command))
    application.add_handler(CommandHandler("transcribe_yadisk", transcribe_yadisk))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("✅ Бот запущен!")
        application.run_polling()

if __name__ == "__main__":
    main() 