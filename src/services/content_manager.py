"""
Content Manager - Система управления контентом
Функции: черновики, планирование, медиа-библиотека, публикации
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

from notion_client import AsyncClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class ContentType(Enum):
    POST = "📝 Пост"
    STORY = "📸 История"
    VIDEO = "🎥 Видео"
    CAROUSEL = "🖼️ Карусель"
    REEL = "🎬 Reels"
    ARTICLE = "📄 Статья"

class ContentStatus(Enum):
    DRAFT = "📝 Черновик"
    REVIEW = "👀 На проверке"
    APPROVED = "✅ Утвержден"
    SCHEDULED = "⏰ Запланирован"
    PUBLISHED = "🌍 Опубликован"
    ARCHIVED = "📁 Архив"

class Platform(Enum):
    INSTAGRAM = "📷 Instagram"
    TELEGRAM = "💬 Telegram"
    VK = "🔵 VKontakte"
    FACEBOOK = "👤 Facebook"
    TIKTOK = "🎵 TikTok"
    YOUTUBE = "📺 YouTube"
    WEBSITE = "🌐 Сайт"

@dataclass
class MediaFile:
    id: str
    filename: str
    file_type: str  # image, video, document
    file_size: int
    url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    tags: List[str] = None
    uploaded_at: datetime = None

@dataclass
class ContentPiece:
    id: str
    title: str
    content_type: ContentType
    status: ContentStatus
    text_content: str
    media_files: List[MediaFile]
    platforms: List[Platform]
    hashtags: List[str]
    scheduled_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    author_id: str
    reviewer_id: Optional[str] = None
    notes: str = ""
    engagement_target: Optional[Dict[str, int]] = None  # likes, comments, views
    
class ContentCalendar:
    """Календарь контента с планированием"""
    
    def __init__(self):
        self.scheduled_content: Dict[str, List[ContentPiece]] = {}  # date -> content list
        
    def add_content(self, content: ContentPiece):
        """Добавление контента в календарь"""
        if content.scheduled_time:
            date_key = content.scheduled_time.strftime("%Y-%m-%d")
            if date_key not in self.scheduled_content:
                self.scheduled_content[date_key] = []
            self.scheduled_content[date_key].append(content)
    
    def get_content_for_date(self, date: datetime) -> List[ContentPiece]:
        """Получение контента на определенную дату"""
        date_key = date.strftime("%Y-%m-%d")
        return self.scheduled_content.get(date_key, [])
    
    def get_week_content(self, start_date: datetime) -> Dict[str, List[ContentPiece]]:
        """Получение контента на неделю"""
        week_content = {}
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            date_key = current_date.strftime("%Y-%m-%d")
            week_content[date_key] = self.get_content_for_date(current_date)
        return week_content

class ContentManager:
    """Менеджер контента с полным функционалом"""
    
    def __init__(self, notion_token: str, content_db_id: str, media_db_id: str):
        self.notion = AsyncClient(auth=notion_token)
        self.content_db_id = content_db_id
        self.media_db_id = media_db_id
        self.calendar = ContentCalendar()
        self.content_templates = {}
        
    async def create_content_draft(
        self,
        title: str,
        content_type: ContentType,
        text_content: str = "",
        platforms: List[Platform] = None,
        hashtags: List[str] = None,
        media_files: List[str] = None,  # file URLs or IDs
        author_telegram_id: str = None,
        scheduled_time: Optional[datetime] = None
    ) -> ContentPiece:
        """Создание черновика контента"""
        
        # Подготовка медиафайлов
        media_objects = []
        if media_files:
            for media_id in media_files:
                media = await self.get_media_file(media_id)
                if media:
                    media_objects.append(media)
        
        # Создание объекта контента
        content = ContentPiece(
            id=str(uuid.uuid4()),
            title=title,
            content_type=content_type,
            status=ContentStatus.DRAFT,
            text_content=text_content,
            media_files=media_objects,
            platforms=platforms or [],
            hashtags=hashtags or [],
            scheduled_time=scheduled_time,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            author_id=author_telegram_id or "unknown"
        )
        
        # Сохранение в Notion
        await self._save_content_to_notion(content)
        
        # Добавление в календарь если запланировано
        if scheduled_time:
            self.calendar.add_content(content)
            
        return content
    
    async def update_content(
        self,
        content_id: str,
        title: Optional[str] = None,
        text_content: Optional[str] = None,
        status: Optional[ContentStatus] = None,
        platforms: Optional[List[Platform]] = None,
        hashtags: Optional[List[str]] = None,
        scheduled_time: Optional[datetime] = None,
        notes: Optional[str] = None,
        updater_telegram_id: Optional[str] = None
    ) -> bool:
        """Обновление контента"""
        
        content = await self.get_content(content_id)
        if not content:
            return False
            
        # Обновление полей
        if title:
            content.title = title
        if text_content is not None:
            content.text_content = text_content
        if status:
            content.status = status
        if platforms is not None:
            content.platforms = platforms
        if hashtags is not None:
            content.hashtags = hashtags
        if scheduled_time:
            content.scheduled_time = scheduled_time
            self.calendar.add_content(content)
        if notes is not None:
            content.notes = notes
            
        content.updated_at = datetime.now()
        
        # Сохранение изменений
        await self._save_content_to_notion(content)
        
        # Уведомления о изменении статуса
        if status:
            await self._notify_content_status_change(content, updater_telegram_id)
            
        return True
    
    async def get_content(self, content_id: str) -> Optional[ContentPiece]:
        """Получение контента по ID"""
        try:
            # Поиск в базе Notion
            response = await self.notion.databases.query(
                database_id=self.content_db_id,
                filter={
                    "property": "ID",
                    "rich_text": {"equals": content_id}
                }
            )
            
            if response["results"]:
                return await self._parse_content_from_notion(response["results"][0])
                
        except Exception as e:
            logger.error(f"Error getting content {content_id}: {e}")
            
        return None
    
    async def get_content_by_status(self, status: ContentStatus) -> List[ContentPiece]:
        """Получение контента по статусу"""
        try:
            response = await self.notion.databases.query(
                database_id=self.content_db_id,
                filter={
                    "property": "Статус",
                    "select": {"equals": status.value}
                },
                sorts=[{"property": "Обновлено", "direction": "descending"}]
            )
            
            content_list = []
            for page in response["results"]:
                content = await self._parse_content_from_notion(page)
                if content:
                    content_list.append(content)
                    
            return content_list
            
        except Exception as e:
            logger.error(f"Error getting content by status {status}: {e}")
            return []
    
    async def get_scheduled_content(self, date: datetime) -> List[ContentPiece]:
        """Получение запланированного контента на дату"""
        try:
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            response = await self.notion.databases.query(
                database_id=self.content_db_id,
                filter={
                    "and": [
                        {
                            "property": "Дата публикации",
                            "date": {"on_or_after": start_date.isoformat()}
                        },
                        {
                            "property": "Дата публикации",  
                            "date": {"before": end_date.isoformat()}
                        },
                        {
                            "property": "Статус",
                            "select": {"equals": ContentStatus.SCHEDULED.value}
                        }
                    ]
                },
                sorts=[{"property": "Дата публикации", "direction": "ascending"}]
            )
            
            content_list = []
            for page in response["results"]:
                content = await self._parse_content_from_notion(page)
                if content:
                    content_list.append(content)
                    
            return content_list
            
        except Exception as e:
            logger.error(f"Error getting scheduled content: {e}")
            return []
    
    async def upload_media_file(
        self,
        file_data: bytes,
        filename: str,
        file_type: str,
        alt_text: Optional[str] = None,
        tags: List[str] = None,
        uploader_telegram_id: Optional[str] = None
    ) -> MediaFile:
        """Загрузка медиафайла в библиотеку"""
        
        # Сохранение файла (в реальной реализации - в облачное хранилище)
        file_id = str(uuid.uuid4())
        file_url = f"https://storage.example.com/{file_id}/{filename}"
        
        media_file = MediaFile(
            id=file_id,
            filename=filename,
            file_type=file_type,
            file_size=len(file_data),
            url=file_url,
            alt_text=alt_text,
            tags=tags or [],
            uploaded_at=datetime.now()
        )
        
        # Сохранение информации в Notion
        await self._save_media_to_notion(media_file, uploader_telegram_id)
        
        return media_file
    
    async def get_media_file(self, media_id: str) -> Optional[MediaFile]:
        """Получение медиафайла из библиотеки"""
        try:
            response = await self.notion.databases.query(
                database_id=self.media_db_id,
                filter={
                    "property": "ID",
                    "rich_text": {"equals": media_id}
                }
            )
            
            if response["results"]:
                return await self._parse_media_from_notion(response["results"][0])
                
        except Exception as e:
            logger.error(f"Error getting media file {media_id}: {e}")
            
        return None
    
    async def search_media(
        self,
        query: Optional[str] = None,
        file_type: Optional[str] = None,
        tags: List[str] = None
    ) -> List[MediaFile]:
        """Поиск медиафайлов в библиотеке"""
        
        filters = []
        
        if query:
            filters.append({
                "property": "Название",
                "rich_text": {"contains": query}
            })
            
        if file_type:
            filters.append({
                "property": "Тип",
                "select": {"equals": file_type}
            })
            
        if tags:
            for tag in tags:
                filters.append({
                    "property": "Теги",
                    "multi_select": {"contains": tag}
                })
        
        try:
            filter_condition = {"and": filters} if len(filters) > 1 else filters[0] if filters else {}
            
            response = await self.notion.databases.query(
                database_id=self.media_db_id,
                filter=filter_condition,
                sorts=[{"property": "Загружено", "direction": "descending"}]
            )
            
            media_list = []
            for page in response["results"]:
                media = await self._parse_media_from_notion(page)
                if media:
                    media_list.append(media)
                    
            return media_list
            
        except Exception as e:
            logger.error(f"Error searching media: {e}")
            return []
    
    async def create_content_template(
        self,
        name: str,
        content_type: ContentType,
        template_text: str,
        default_platforms: List[Platform],
        default_hashtags: List[str],
        creator_telegram_id: str
    ) -> str:
        """Создание шаблона контента"""
        
        template_id = str(uuid.uuid4())
        
        self.content_templates[template_id] = {
            "name": name,
            "content_type": content_type,
            "template_text": template_text,
            "default_platforms": default_platforms,
            "default_hashtags": default_hashtags,
            "creator_id": creator_telegram_id,
            "created_at": datetime.now()
        }
        
        # Сохранение в Notion (база шаблонов)
        await self._save_template_to_notion(template_id, self.content_templates[template_id])
        
        return template_id
    
    async def use_template(self, template_id: str, title: str, custom_text: str = "") -> ContentPiece:
        """Использование шаблона для создания контента"""
        
        template = self.content_templates.get(template_id)
        if not template:
            return None
            
        # Замена переменных в шаблоне
        final_text = template["template_text"]
        if custom_text:
            final_text = final_text.replace("{CUSTOM_TEXT}", custom_text)
        final_text = final_text.replace("{DATE}", datetime.now().strftime("%d.%m.%Y"))
        
        return await self.create_content_draft(
            title=title,
            content_type=template["content_type"],
            text_content=final_text,
            platforms=template["default_platforms"],
            hashtags=template["default_hashtags"],
            author_telegram_id=template["creator_id"]
        )
    
    def generate_content_keyboard(self, content: ContentPiece) -> InlineKeyboardMarkup:
        """Генерация клавиатуры для управления контентом"""
        
        keyboard = []
        
        # Первая строка - статусы
        status_row = []
        if content.status == ContentStatus.DRAFT:
            status_row.append(InlineKeyboardButton("👀 На проверку", callback_data=f"content_status_{content.id}_review"))
        elif content.status == ContentStatus.REVIEW:
            status_row.append(InlineKeyboardButton("✅ Утвердить", callback_data=f"content_status_{content.id}_approved"))
            status_row.append(InlineKeyboardButton("📝 В черновик", callback_data=f"content_status_{content.id}_draft"))
        elif content.status == ContentStatus.APPROVED:
            status_row.append(InlineKeyboardButton("⏰ Запланировать", callback_data=f"content_schedule_{content.id}"))
            
        if status_row:
            keyboard.append(status_row)
        
        # Вторая строка - управление
        keyboard.append([
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"content_edit_{content.id}"),
            InlineKeyboardButton("🖼️ Медиа", callback_data=f"content_media_{content.id}")
        ])
        
        # Третья строка - дополнительно
        keyboard.append([
            InlineKeyboardButton("📋 Детали", callback_data=f"content_details_{content.id}"),
            InlineKeyboardButton("🗂️ Дублировать", callback_data=f"content_duplicate_{content.id}")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def format_content_message(self, content: ContentPiece, detailed: bool = False) -> str:
        """Форматирование сообщения о контенте"""
        
        msg = f"**{content.title}**\n\n"
        msg += f"📝 Тип: {content.content_type.value}\n"
        msg += f"📊 Статус: {content.status.value}\n"
        
        if content.platforms:
            platform_names = [p.value for p in content.platforms]
            msg += f"🌐 Платформы: {', '.join(platform_names)}\n"
        
        if content.scheduled_time:
            msg += f"⏰ Запланировано: {content.scheduled_time.strftime('%d.%m.%Y %H:%M')}\n"
        
        if content.media_files:
            msg += f"🖼️ Медиафайлов: {len(content.media_files)}\n"
        
        if content.hashtags:
            msg += f"#️⃣ Хештеги: {' '.join(['#' + tag for tag in content.hashtags])}\n"
        
        if detailed and content.text_content:
            preview = content.text_content[:200] + "..." if len(content.text_content) > 200 else content.text_content
            msg += f"\n📄 Текст:\n{preview}\n"
        
        if detailed and content.notes:
            msg += f"\n📝 Заметки: {content.notes}\n"
        
        msg += f"\n🕐 Создано: {content.created_at.strftime('%d.%m.%Y %H:%M')}"
        
        return msg
    
    def format_calendar_week(self, week_content: Dict[str, List[ContentPiece]]) -> str:
        """Форматирование недельного календаря"""
        
        msg = "📅 **Календарь контента на неделю**\n\n"
        
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        
        for i, (date_key, content_list) in enumerate(week_content.items()):
            date_obj = datetime.strptime(date_key, "%Y-%m-%d")
            day_name = days[date_obj.weekday()]
            
            msg += f"**{day_name} {date_obj.strftime('%d.%m')}**\n"
            
            if content_list:
                for content in content_list:
                    time_str = content.scheduled_time.strftime("%H:%M") if content.scheduled_time else "?"
                    platforms = " ".join([p.value.split()[0] for p in content.platforms])
                    msg += f"  {time_str} - {content.title} {platforms}\n"
            else:
                msg += "  _Нет запланированного контента_\n"
                
            msg += "\n"
        
        return msg
    
    # Вспомогательные методы для работы с Notion
    async def _save_content_to_notion(self, content: ContentPiece):
        """Сохранение контента в Notion"""
        
        properties = {
            "ID": {"rich_text": [{"text": {"content": content.id}}]},
            "Название": {"title": [{"text": {"content": content.title}}]},
            "Тип": {"select": {"name": content.content_type.value}},
            "Статус": {"select": {"name": content.status.value}},
            "Текст": {"rich_text": [{"text": {"content": content.text_content}}]},
            "Создано": {"date": {"start": content.created_at.isoformat()}},
            "Обновлено": {"date": {"start": content.updated_at.isoformat()}}
        }
        
        if content.scheduled_time:
            properties["Дата публикации"] = {"date": {"start": content.scheduled_time.isoformat()}}
            
        if content.platforms:
            properties["Платформы"] = {"multi_select": [{"name": p.value} for p in content.platforms]}
            
        if content.hashtags:
            properties["Хештеги"] = {"rich_text": [{"text": {"content": " ".join(["#" + tag for tag in content.hashtags])}}]}
        
        try:
            # Проверяем, существует ли уже страница
            existing = await self.notion.databases.query(
                database_id=self.content_db_id,
                filter={
                    "property": "ID",
                    "rich_text": {"equals": content.id}
                }
            )
            
            if existing["results"]:
                # Обновляем существующую
                await self.notion.pages.update(
                    page_id=existing["results"][0]["id"],
                    properties=properties
                )
            else:
                # Создаем новую
                await self.notion.pages.create(
                    parent={"database_id": self.content_db_id},
                    properties=properties
                )
                
        except Exception as e:
            logger.error(f"Error saving content to Notion: {e}")
    
    async def _save_media_to_notion(self, media: MediaFile, uploader_id: str):
        """Сохранение медиафайла в Notion"""
        
        properties = {
            "ID": {"rich_text": [{"text": {"content": media.id}}]},
            "Название": {"title": [{"text": {"content": media.filename}}]},
            "Тип": {"select": {"name": media.file_type}}, 
            "Размер": {"number": media.file_size},
            "URL": {"url": media.url},
            "Загружено": {"date": {"start": media.uploaded_at.isoformat()}}
        }
        
        if media.alt_text:
            properties["Alt текст"] = {"rich_text": [{"text": {"content": media.alt_text}}]}
            
        if media.tags:
            properties["Теги"] = {"multi_select": [{"name": tag} for tag in media.tags]}
        
        try:
            await self.notion.pages.create(
                parent={"database_id": self.media_db_id},
                properties=properties
            )
        except Exception as e:
            logger.error(f"Error saving media to Notion: {e}")
    
    async def _parse_content_from_notion(self, page: Dict) -> Optional[ContentPiece]:
        """Парсинг контента из страницы Notion"""
        # Реализация парсинга свойств Notion в объект ContentPiece
        return None
    
    async def _parse_media_from_notion(self, page: Dict) -> Optional[MediaFile]:
        """Парсинг медиафайла из страницы Notion"""
        # Реализация парсинга свойств Notion в объект MediaFile
        return None
    
    async def _notify_content_status_change(self, content: ContentPiece, updater_id: str):
        """Уведомление об изменении статуса контента"""
        # Реализация уведомлений через Telegram
        pass
    
    async def _save_template_to_notion(self, template_id: str, template_data: Dict):
        """Сохранение шаблона в Notion"""
        # Реализация сохранения шаблона
        pass 