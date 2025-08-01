"""
🎯 UNIVERSAL MATERIALS BOT - МЕГА-АГРЕГАТОР ВСЕХ ВОЗМОЖНОСТЕЙ

ПРИНЦИП ПАРЕТО: 20% кода = 80% всех функций
- Figma ссылки → материалы с превью
- Скриншоты → автоматические задачи
- Файлы → структурированные материалы
- Умное связывание: задачи ↔ материалы ↔ KPI ↔ релизы ↔ участники
- Детерминированные правила (98%) + LLM (2%)
- Автогенерация правок/чеклистов → подзадачи
- Тегирование → автораспределение по гайдам/идеям/концептам
"""

import asyncio
import logging
import json
import re
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from urllib.parse import urlparse
import base64
import io
from PIL import Image

import requests
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, File
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Наследуем от готовых ботов
from services.figma_materials_bot import FigmaMaterialsBot, FigmaLink, MaterialRequest
from shared_code.integrations.notion import NotionManager
from shared_code.integrations.yandex_cloud import YandexDiskManager
from shared_code.utils.logging_utils import setup_logging

# Загружаем окружение
load_dotenv()

# Настройка логирования
logger = setup_logging("universal_materials_bot")

@dataclass
class UniversalRequest:
    """Универсальный запрос на создание материала"""
    content_type: str  # "figma", "screenshot", "file", "text"
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    content: Optional[str] = None
    
    # Извлечённые данные
    title: str = ""
    description: str = ""
    tags: List[str] = None
    
    # Связи
    related_task_id: Optional[str] = None
    related_project_id: Optional[str] = None
    assigned_users: List[str] = None
    release_type: str = ""
    
    # Правки и чеклисты
    checklist_items: List[str] = None
    needs_review: bool = True

class UniversalMaterialsBot(FigmaMaterialsBot):
    """🎯 УНИВЕРСАЛЬНЫЙ бот - агрегатор всех возможностей"""
    
    def __init__(self):
        super().__init__()
        
        # Дополнительные базы
        self.projects_db = os.getenv("ПРОЕКТЫ_DB")
        self.concepts_db = os.getenv("КОНЦЕПТЫ_СЦЕНАРИИ_DB")
        self.releases_db = os.getenv("ЛИНЕЙКИ_ПРОДУКТОВ_DB")
        
        # Кэш проектов и релизов
        self.projects_cache = {}
        self.releases_cache = {}
        
        logger.info("🚀 UniversalMaterialsBot инициализирован - ВСЕ ВОЗМОЖНОСТИ!")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start - показ всех возможностей"""
        welcome_text = """
🎯 **UNIVERSAL MATERIALS BOT** - ВСЕ В ОДНОМ МЕСТЕ!

🎨 **ЧТО УМЕЮ:**
• 🔗 **Figma ссылки** → материалы с превью + автосвязи
• 🖼️ **Скриншоты** → автозадачи с аннотациями
• 📁 **Файлы** → структурированные материалы
• ✍️ **Текст** → идеи, концепты, гайды

🔄 **УМНОЕ СВЯЗЫВАНИЕ:**
• Материалы ↔ Задачи ↔ Подзадачи
• Задачи ↔ KPI ↔ Участники  
• Материалы ↔ Релизы ↔ Проекты
• Правки → Чеклисты → Подзадачи

🏷️ **АВТОТЕГИРОВАНИЕ:**
• Бренд → Гайды
• Стратегия → Идеи
• Концепт → Концепты
• 15+ детерминированных правил

📤 **КАК ИСПОЛЬЗОВАТЬ:**
Просто отправь:
• Figma ссылку
• Скриншот с аннотациями
• Любой файл
• Текстовое сообщение

⚡ **КОМАНДЫ:**
/refresh - обновить кэш
/stats - статистика
/tasks - активные задачи
/help - справка
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    def detect_content_type(self, update: Update) -> str:
        """Определение типа контента"""
        message = update.message
        
        # Figma ссылка
        if message.text and 'figma.com' in message.text:
            return "figma"
        

        
        # Скриншот/изображение
        if message.photo or message.document:
            if message.document and message.document.mime_type and message.document.mime_type.startswith('image/'):
                return "screenshot"
            elif message.photo:
                return "screenshot"
            else:
                return "file"
        
        # Текстовое сообщение
        if message.text:
            return "text"
        
        return "unknown"

    async def extract_universal_request(self, update: Update) -> UniversalRequest:
        """Извлечение универсального запроса из сообщения"""
        content_type = self.detect_content_type(update)
        message = update.message
        
        request = UniversalRequest(content_type=content_type)
        
        if content_type == "figma":
            # Используем готовую логику от FigmaMaterialsBot
            figma_link = self.parse_figma_url(message.text)
            if figma_link:
                request.source_url = figma_link.url
                request.title = figma_link.title
                request.description = f"Материал из Figma: {figma_link.link_type}"
                request.tags = self.generate_smart_tags(figma_link.title, figma_link)
        

        
        elif content_type == "screenshot":
            # Обработка скриншота
            request.file_name = "screenshot.png"
            request.title = "Скриншот " + datetime.now().strftime("%d.%m %H:%M")
            request.description = message.caption or "Скриншот для обработки"
            request.tags = self.extract_tags_from_screenshot(message.caption or "")
            
        elif content_type == "file":
            # Обработка файла
            if message.document:
                request.file_name = message.document.file_name
                request.title = message.document.file_name.split('.')[0]
                request.description = message.caption or f"Файл: {message.document.file_name}"
                request.tags = self.extract_tags_from_filename(message.document.file_name)
        
        elif content_type == "text":
            # Обработка текста
            request.content = message.text
            request.title = message.text[:50] + "..." if len(message.text) > 50 else message.text
            request.description = "Текстовая идея/концепт"
            request.tags = self.extract_tags_from_text(message.text)
        
        # Поиск связанных задач
        if request.title:
            request.related_task_id = self.find_related_task(request.title, None)
        
        # Генерация чеклиста
        request.checklist_items = self.generate_universal_checklist(request)
        
        return request

    def extract_tags_from_screenshot(self, caption: str) -> List[str]:
        """Извлечение тегов из подписи к скриншоту"""
        tags = []
        caption_lower = caption.lower()
        
        # Детерминированные правила
        screenshot_rules = {
            'UI/UX': ['интерфейс', 'ui', 'ux', 'дизайн', 'макет'],
            'Бренд': ['логотип', 'бренд', 'фирм', 'стиль'],
            'Ошибка': ['ошибка', 'баг', 'проблема', 'не работает'],
            'Задача': ['задача', 'todo', 'сделать', 'исправить'],
            'Идея': ['идея', 'предложение', 'улучшение'],
            'Процесс': ['процесс', 'workflow', 'алгоритм']
        }
        
        for tag, keywords in screenshot_rules.items():
            if any(keyword in caption_lower for keyword in keywords):
                tags.append(tag)
        
        # Если нет тегов - ставим Скриншот
        if not tags:
            tags.append('Скриншот')
        
        return tags

    def extract_tags_from_filename(self, filename: str) -> List[str]:
        """Извлечение тегов из имени файла"""
        tags = []
        filename_lower = filename.lower()
        
        # Детерминированные правила для файлов
        file_rules = {
            'Документ': ['.doc', '.pdf', '.txt'],
            'Презентация': ['.ppt', '.pptx'],
            'Таблица': ['.xls', '.xlsx', '.csv'],
            'Изображение': ['.jpg', '.png', '.gif', '.svg'],
            'Видео': ['.mp4', '.mov', '.avi'],
            'Архив': ['.zip', '.rar', '.7z'],
            'Код': ['.py', '.js', '.html', '.css']
        }
        
        for tag, extensions in file_rules.items():
            if any(ext in filename_lower for ext in extensions):
                tags.append(tag)
        
        # Анализ названия файла
        name_rules = {
            'Бренд': ['logo', 'brand', 'логотип', 'бренд'],
            'Макет': ['mockup', 'layout', 'макет', 'дизайн'],
            'Техзадание': ['тз', 'техзадание', 'spec', 'requirements']
        }
        
        for tag, keywords in name_rules.items():
            if any(keyword in filename_lower for keyword in keywords):
                tags.append(tag)
        
        return tags or ['Файл']

    def extract_tags_from_text(self, text: str) -> List[str]:
        """Извлечение тегов из текста"""
        tags = []
        text_lower = text.lower()
        
        # Детерминированные правила для текста
        text_rules = {
            'Идея': ['идея', 'предложение', 'концепция', 'думаю'],
            'Задача': ['нужно', 'сделать', 'todo', 'задача'],
            'Проблема': ['проблема', 'ошибка', 'не работает', 'баг'],
            'Стратегия': ['стратегия', 'план', 'развитие', 'цель'],
            'Процесс': ['процесс', 'алгоритм', 'последовательность'],
            'Бренд': ['бренд', 'логотип', 'фирменный', 'айдентика'],
            'Маркетинг': ['реклама', 'продвижение', 'маркетинг', 'smm'],
            'Продукт': ['продукт', 'товар', 'функция', 'фича']
        }
        
        for tag, keywords in text_rules.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        
        return tags or ['Заметка']



    def generate_universal_checklist(self, request: UniversalRequest) -> List[str]:
        """Генерация универсального чеклиста"""
        checklist = []
        
        # Базовые проверки
        checklist.append("Проверить соответствие техзаданию")
        checklist.append("Проверить качество материала")
        
        # Специфичные проверки по типу контента
        if request.content_type == "figma":
            checklist.extend([
                "Проверить соответствие брендбуку",
                "Проверить адаптивность дизайна"
            ])
        elif request.content_type == "screenshot":
            checklist.extend([
                "Воспроизвести проблему/ситуацию",
                "Создать план исправления"
            ])
        elif request.content_type == "file":
            checklist.extend([
                "Проверить формат файла",
                "Проверить полноту информации"
            ])
        elif request.content_type == "text":
            checklist.extend([
                "Детализировать идею",
                "Оценить реализуемость"
            ])
        
        # Проверки по тегам
        if 'Бренд' in (request.tags or []):
            checklist.append("Проверить фирменный стиль")
        if 'UI/UX' in (request.tags or []):
            checklist.append("Проверить пользовательский опыт")
        
        return checklist[:6]  # Максимум 6 пунктов

    async def determine_target_databases(self, request: UniversalRequest) -> Dict[str, str]:
        """Определение целевых баз данных"""
        targets = {
            'primary': self.materials_db  # Основная база - всегда материалы
        }
        
        # Дополнительные базы по тегам
        if request.tags:
            for tag in request.tags:
                if tag in ['Бренд', 'Стиль', 'Гайды']:
                    targets['guides'] = self.guides_db
                elif tag in ['Идея', 'Концепция', 'Стратегия']:
                    targets['ideas'] = self.ideas_db
                elif tag in ['Концепт', 'Сценарий']:
                    targets['concepts'] = self.concepts_db
        
        return targets

    async def create_universal_material(self, request: UniversalRequest, file_url: Optional[str] = None) -> Optional[str]:
        """Создание универсального материала с всеми связями"""
        try:
            # Подготовка базовых данных
            material_data = {
                "Name": {"title": [{"text": {"content": request.title}}]},
                "Описание": {"rich_text": [{"text": {"content": request.description}}]},
                "Теги": {"multi_select": [{"name": tag} for tag in (request.tags or [])]},
                "Статус": {"status": {"name": "In progress"}},
                "Date": {"date": {"start": datetime.now().isoformat()}},
                "Вес": {"number": 5}
            }
            
            # Добавляем URL если есть
            if request.source_url:
                material_data["URL"] = {"url": request.source_url}
            elif file_url:
                material_data["URL"] = {"url": file_url}
            
            # Добавляем файл если есть
            if file_url:
                material_data["Files & media"] = {
                    "files": [{"external": {"url": file_url}}]
                }
            
            # Создаем основной материал
            material_page = self.notion.create_page(
                database_id=self.materials_db,
                properties=material_data
            )
            
            if not material_page:
                return None
            
            material_id = material_page['id']
            
            # Устанавливаем cover для изображений
            if file_url and request.content_type in ["screenshot", "figma"]:
                try:
                    self.notion.update_page_cover(material_id, file_url)
                except Exception as e:
                    logger.warning(f"Не удалось установить cover: {e}")
            
            # Создаем подзадачи из чеклиста
            if request.checklist_items and request.related_task_id:
                await self.create_universal_subtasks(request.related_task_id, request.checklist_items)
            
            # Создаем связанные записи в других базах
            await self.create_related_records(request, material_id)
            
            # Связываем с задачей если найдена
            if request.related_task_id:
                await self.link_material_to_task(material_id, request.related_task_id)
            
            logger.info(f"✅ Универсальный материал создан: {material_id}")
            return material_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания универсального материала: {e}")
            return None

    async def create_universal_subtasks(self, parent_task_id: str, checklist_items: List[str]):
        """Создание универсальных подзадач"""
        try:
            for item in checklist_items:
                subtask_data = {
                    "Подзадачи": {"title": [{"text": {"content": item}}]},
                    "Задачи": {"relation": [{"id": parent_task_id}]},
                    " Статус": {"status": {"name": "To do"}},
                    "Направление": {"multi_select": [{"name": "Дизайн"}]},
                    "Приоритет": {"select": {"name": "Средний"}},
                    "Часы": {"number": 0.5}
                }
                
                self.notion.create_page(
                    database_id=self.subtasks_db,
                    properties=subtask_data
                )
            
            logger.info(f"✅ Создано {len(checklist_items)} универсальных подзадач")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания универсальных подзадач: {e}")

    async def create_related_records(self, request: UniversalRequest, material_id: str):
        """Создание связанных записей в других базах"""
        try:
            targets = await self.determine_target_databases(request)
            
            for db_type, db_id in targets.items():
                if db_type == 'primary':
                    continue  # Основная запись уже создана
                
                # Создаем связанную запись
                related_data = {
                    "Name": {"title": [{"text": {"content": f"{request.title} ({db_type})"}}]},
                    "Описание": {"rich_text": [{"text": {"content": f"Автоматически создано из материала. {request.description}"}}]},
                    "Теги": {"multi_select": [{"name": tag} for tag in (request.tags or [])]},
                    "Статус": {"status": {"name": "To do"}},
                    "Вес": {"number": 3}
                }
                
                # Добавляем дату
                related_data["Date"] = {"date": {"start": datetime.now().isoformat()}}
                
                # Создаем запись
                self.notion.create_page(
                    database_id=db_id,
                    properties=related_data
                )
                
                logger.info(f"✅ Создана связанная запись в {db_type}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания связанных записей: {e}")

    async def link_material_to_task(self, material_id: str, task_id: str):
        """Связывание материала с задачей"""
        try:
            # Получаем текущие связи задачи
            task_page = self.notion.get_page(task_id)
            if not task_page:
                return
            
            # Обновляем поле "Материалы" в задаче
            current_materials = task_page.get('properties', {}).get('Материалы', {}).get('relation', [])
            new_materials = current_materials + [{"id": material_id}]
            
            self.notion.update_page(
                page_id=task_id,
                properties={
                    "Материалы": {
                        "relation": new_materials
                    }
                }
            )
            
            logger.info(f"✅ Материал {material_id} связан с задачей {task_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка связывания материала с задачей: {e}")

    async def handle_universal_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Универсальный обработчик сообщений"""
        # Показываем прогресс
        progress_msg = await update.message.reply_text("🔄 Обрабатываю сообщение...")
        
        try:
            # Извлекаем универсальный запрос
            await progress_msg.edit_text("🔍 Анализирую контент...")
            request = await self.extract_universal_request(update)
            
            # Обрабатываем файл если есть
            file_url = None
            if request.content_type in ["screenshot", "file"]:
                await progress_msg.edit_text("📤 Загружаю файл...")
                file_url = await self.process_file(update.message)
            elif request.content_type == "figma":
                await progress_msg.edit_text("🎨 Получаю превью из Figma...")
                # Используем готовую логику Figma
                figma_link = self.parse_figma_url(update.message.text)
                if figma_link:
                    preview_url = await self.get_figma_preview(figma_link)
                    if preview_url:
                        file_url = await self.upload_to_yandex_disk(preview_url, figma_link.title)
            

            
            # Обновляем кэш задач если нужно
            if not self.active_tasks_cache:
                await progress_msg.edit_text("🔄 Обновляю кэш задач...")
                await self.refresh_tasks_cache()
            
            # Показываем конфирмацию
            await self.show_universal_confirmation(update, progress_msg, request, file_url)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки универсального сообщения: {e}")
            await progress_msg.edit_text(f"❌ Ошибка обработки: {str(e)}")

    async def process_file(self, message) -> Optional[str]:
        """Обработка файла/изображения"""
        try:
            file_obj = None
            file_name = "file"
            
            if message.photo:
                # Берем фото наибольшего размера
                file_obj = message.photo[-1]
                file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            elif message.document:
                file_obj = message.document
                file_name = message.document.file_name or "document"
            
            if not file_obj:
                return None
            
            # Получаем файл
            file = await file_obj.get_file()
            
            # Скачиваем во временный файл
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                await file.download_to_drive(temp_file.name)
                
                # Загружаем на Яндекс.Диск
                disk_path = f"/universal_materials/{file_name}"
                success = self.yandex_disk.upload_file(temp_file.name, disk_path)
                
                if success:
                    public_url = self.yandex_disk.get_public_image_url(disk_path)
                    return public_url
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки файла: {e}")
            return None

    async def show_universal_confirmation(self, update: Update, progress_msg, request: UniversalRequest, file_url: Optional[str]):
        """Показ универсальной конфирмации"""
        # Информация о найденной задаче
        task_info = ""
        if request.related_task_id and request.related_task_id in self.active_tasks_cache:
            task_data = self.active_tasks_cache[request.related_task_id]
            task_info = f"🔗 **Связанная задача:** {task_data['title']}\n"
        
        # Информация о чеклисте
        checklist_info = ""
        if request.checklist_items:
            checklist_info = f"✅ **Чеклист:** {len(request.checklist_items)} пунктов\n"
        
        # Иконка по типу контента
        type_icons = {
            "figma": "🎨",
            "screenshot": "🖼️", 
            "file": "📁",
            "text": "✍️"
        }
        
        confirmation_text = f"""
{type_icons.get(request.content_type, "📄")} **УНИВЕРСАЛЬНЫЙ МАТЕРИАЛ ГОТОВ!**

📝 **Название:** {request.title}
📋 **Тип:** {request.content_type.upper()}
🏷️ **Теги:** {', '.join(request.tags or [])}
{task_info}{checklist_info}📎 **Файл:** {"✅ Да" if file_url else "❌ Нет"}

🚀 **ЧТО СОЗДАСТСЯ:**
• Материал в Notion {f"с обложкой" if file_url else ""}
• {"Автосвязь с задачей" if request.related_task_id else "Поиск связанной задачи"}
• {"Чеклист → подзадачи" if request.checklist_items else "Базовые проверки"}
• Автораспределение по базам

Создаём универсальный материал?
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚀 Создать", callback_data=f"create_universal_{update.message.message_id}"),
                InlineKeyboardButton("❌ Отмена", callback_data="cancel_universal")
            ]
        ])
        
        # Сохраняем данные
        self.pending_materials = getattr(self, 'pending_materials', {})
        self.pending_materials[update.message.message_id] = {
            'request': request,
            'file_url': file_url
        }
        
        await progress_msg.edit_text(confirmation_text, reply_markup=keyboard, parse_mode='Markdown')

    async def handle_universal_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка универсальных callback"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("create_universal_"):
            message_id = int(query.data.split("_")[-1])
            
            if hasattr(self, 'pending_materials') and message_id in self.pending_materials:
                data = self.pending_materials[message_id]
                request = data['request']
                file_url = data['file_url']
                
                await query.edit_message_text("🚀 Создаю универсальный материал...")
                
                # Создаем материал
                material_id = await self.create_universal_material(request, file_url)
                
                if material_id:
                    notion_url = f"https://www.notion.so/{material_id.replace('-', '')}"
                    
                    # Подсчитываем что создали
                    created_items = ["Материал создан"]
                    if request.related_task_id:
                        created_items.append("Связан с задачей")
                    if request.checklist_items:
                        created_items.append(f"{len(request.checklist_items)} подзадач")
                    if len(request.tags or []) > 1:
                        created_items.append("Распределен по базам")
                    
                    success_text = f"""
🎉 **УНИВЕРСАЛЬНЫЙ МАТЕРИАЛ СОЗДАН!**

🔗 [Открыть в Notion]({notion_url})

✅ **РЕЗУЛЬТАТ:**
{chr(10).join(f"• {item}" for item in created_items)}

🏷️ **Теги:** {', '.join(request.tags or [])}
📊 **Тип:** {request.content_type.upper()}
                    """
                    await query.edit_message_text(success_text, parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Ошибка создания универсального материала")
                
                # Очищаем кэш
                del self.pending_materials[message_id]
            else:
                await query.edit_message_text("❌ Данные запроса устарели")
                
        elif query.data == "cancel_universal":
            await query.edit_message_text("❌ Создание универсального материала отменено")

    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда показа активных задач"""
        if not self.active_tasks_cache:
            await self.refresh_tasks_cache()
        
        if not self.active_tasks_cache:
            await update.message.reply_text("❌ Нет активных задач")
            return
        
        tasks_text = "📋 **АКТИВНЫЕ ЗАДАЧИ:**\n\n"
        
        for i, (task_id, task_data) in enumerate(list(self.active_tasks_cache.items())[:10], 1):
            status_emoji = {"To do": "⏳", "In Progress": "🔄", "Review": "👀"}.get(task_data['status'], "📋")
            tasks_text += f"{i}. {status_emoji} **{task_data['title'][:40]}**\n"
            if task_data['participants']:
                tasks_text += f"   👥 {', '.join(task_data['participants'][:2])}\n"
            tasks_text += "\n"
        
        if len(self.active_tasks_cache) > 10:
            tasks_text += f"... и ещё {len(self.active_tasks_cache) - 10} задач"
        
        await update.message.reply_text(tasks_text, parse_mode='Markdown')

    def run(self):
        """Запуск универсального бота"""
        if not self.telegram_token:
            logger.error("TELEGRAM_BOT_TOKEN не найден в .env")
            return
        
        # Создаем приложение
        app = Application.builder().token(self.telegram_token).build()
        
        # Регистрируем команды
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("refresh", self.refresh_command))
        app.add_handler(CommandHandler("stats", self.stats_command))
        app.add_handler(CommandHandler("tasks", self.tasks_command))
        app.add_handler(CommandHandler("help", self.help_command))
        
        # Универсальный обработчик сообщений
        app.add_handler(MessageHandler(filters.ALL, self.handle_universal_message))
        
        # Обработчик callback кнопок (расширяем родительский)
        app.add_handler(CallbackQueryHandler(self.handle_universal_callback))
        
        logger.info("🚀 Universal Materials Bot запущен!")
        print("🎯 UNIVERSAL MATERIALS BOT - ВСЕ ВОЗМОЖНОСТИ В ОДНОМ МЕСТЕ!")
        print("📤 Отправьте Figma ссылку, скриншот, файл или текст")
        
        # Запускаем бота
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = UniversalMaterialsBot()
    bot.run() 