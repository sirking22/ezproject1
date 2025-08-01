"""
🎯 FIGMA MATERIALS BOT - Революционный Telegram бот для создания материалов

ПРИНЦИП ПАРЕТО: 20% кода = 80% функциональности
- Figma URL → PNG превью → Notion материал с обложкой
- Автосвязывание с задачами, релизами, KPI, участниками
- Умные правки/чеклисты → подзадачи
- Автотегирование → гайды, идеи, концепты

WORKFLOW:
1. Отправляешь Figma ссылку
2. Бот создает материал с превью
3. Автоматически связывает с задачами
4. Генерирует чеклисты/правки
5. Распределяет по базам через теги
"""

import asyncio
import logging
import json
import re
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Локальные импорты
from shared_code.integrations.notion import NotionClient
from shared_code.integrations.yandex_cloud import YandexDiskManager
from shared_code.utils.logging_utils import setup_logging

# Загружаем окружение
load_dotenv()

# Настройка логирования
logger = setup_logging("figma_materials_bot")

@dataclass
class FigmaLink:
    """Структура Figma ссылки"""
    url: str
    file_id: str
    node_id: Optional[str] = None
    link_type: str = "file"  # file, proto, design
    title: str = ""

@dataclass
class MaterialRequest:
    """Запрос на создание материала"""
    figma_link: FigmaLink
    name: str
    description: str = ""
    tags: List[str] = None
    priority: str = "Средний"
    assigned_to: str = ""
    related_task: str = ""
    release_type: str = ""

class FigmaMaterialsBot:
    """🎯 Революционный бот для создания материалов из Figma"""
    
    def __init__(self):
        # Токены API
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.figma_token = os.getenv("FIGMA_TOKEN") or os.getenv("FIGMA_ACCESS_TOKEN")  # Поддержка обеих переменных
        self.yandex_token = os.getenv("YANDEX_DISK_TOKEN")
        self.notion = NotionClient()
        self.yandex_disk = YandexDiskManager()
        
        # ID баз данных из env
        self.materials_db = os.getenv("MATERIALS_DB")
        self.tasks_db = os.getenv("TASKS_TRACKER_DB")
        self.subtasks_db = os.getenv("NOTION_SUBTASKS_DB_ID")
        self.ideas_db = os.getenv("БАЗА_ИДЕЙ_СОВЕТОВ_DB")
        self.guides_db = os.getenv("ГАЙДЫ_DB")
        self.kpi_db = os.getenv("KPI_DB")
        
        # Кэш активных задач для быстрого поиска
        self.active_tasks_cache = {}
        self.cache_timestamp = None
        
        logger.info("🚀 FigmaMaterialsBot инициализирован")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        welcome_text = """
🎨 **FIGMA MATERIALS BOT** - Революционная автоматизация!

📋 **ЧТО УМЕЮ:**
• 🔗 Обрабатываю Figma ссылки → создаю материалы с превью
• 🔄 Автосвязываю с задачами, релизами, KPI
• ✅ Генерирую чеклисты/правки → подзадачи
• 🏷️ Автотегирую → распределяю по гайдам/идеям/концептам

📤 **КАК ИСПОЛЬЗОВАТЬ:**
Просто отправь мне Figma ссылку - я сделаю всё остальное!

🎯 **ПРИМЕРЫ ССЫЛОК:**
• `https://www.figma.com/file/ABC123/My-Design`
• `https://www.figma.com/proto/ABC123/Prototype`
• `https://www.figma.com/design/ABC123/Design`

⚡ **КОМАНДЫ:**
/refresh - обновить кэш задач
/stats - статистика созданных материалов
/help - справка
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    def parse_figma_url(self, url: str) -> Optional[FigmaLink]:
        """Парсинг Figma URL с извлечением ID и типа"""
        # Регулярки для разных типов Figma ссылок
        patterns = {
            'file': r'https://www\.figma\.com/file/([a-zA-Z0-9]+)/([^/?]+)',
            'proto': r'https://www\.figma\.com/proto/([a-zA-Z0-9]+)/([^/?]+)',
            'design': r'https://www\.figma\.com/design/([a-zA-Z0-9]+)/([^/?]+)'
        }
        
        for link_type, pattern in patterns.items():
            match = re.match(pattern, url)
            if match:
                file_id = match.group(1)
                title = match.group(2).replace('-', ' ')
                
                # Извлекаем node_id если есть
                node_id = None
                if 'node-id=' in url:
                    node_match = re.search(r'node-id=([^&]+)', url)
                    if node_match:
                        node_id = node_match.group(1)
                
                return FigmaLink(
                    url=url,
                    file_id=file_id,
                    node_id=node_id,
                    link_type=link_type,
                    title=title
                )
        
        return None

    async def get_figma_preview(self, figma_link: FigmaLink) -> Optional[str]:
        """Получение превью изображения из Figma"""
        try:
            # API URL для получения изображения
            api_url = f"https://api.figma.com/v1/images/{figma_link.file_id}"
            
            params = {
                'ids': figma_link.node_id or 'root',
                'format': 'png',
                'scale': 2
            }
            
            headers = {
                'X-Figma-Token': self.figma_token
            }
            
            response = requests.get(api_url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'images' in data and data['images']:
                    # Получаем первое доступное изображение
                    image_url = list(data['images'].values())[0]
                    return image_url
            else:
                logger.error(f"Ошибка Figma API: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Ошибка получения превью Figma: {e}")
        
        return None

    async def upload_to_yandex_disk(self, image_url: str, filename: str) -> Optional[str]:
        """Загрузка изображения на Яндекс.Диск"""
        try:
            # Скачиваем изображение
            response = requests.get(image_url)
            if response.status_code != 200:
                return None
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            try:
                # Загружаем на Яндекс.Диск
                disk_path = f"/figma_materials/{filename}.png"
                success = self.yandex_disk.upload_file(temp_path, disk_path)
                
                if success:
                    # Получаем публичную ссылку
                    public_url = self.yandex_disk.get_public_image_url(disk_path)
                    return public_url
                    
            finally:
                # Удаляем временный файл
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Ошибка загрузки на Яндекс.Диск: {e}")
        
        return None

    async def refresh_tasks_cache(self) -> Dict[str, Any]:
        """Обновление кэша активных задач"""
        try:
            # Получаем активные задачи (не Backlog, не Done, не Canceled)
            filter_data = {
                "and": [
                    {
                        "property": "Статус",
                        "status": {
                            "does_not_equal": "Backlog"
                        }
                    },
                    {
                        "property": "Статус", 
                        "status": {
                            "does_not_equal": "Done"
                        }
                    },
                    {
                        "property": "Статус",
                        "status": {
                            "does_not_equal": "Canceled"
                        }
                    }
                ]
            }
            
            tasks = self.notion.query_database(
                database_id=self.tasks_db,
                filter_data=filter_data
            )
            
            # Создаем индекс для быстрого поиска
            cache = {}
            for task in tasks.get('results', []):
                task_title = task['properties']['Задача']['title'][0]['text']['content'] if task['properties']['Задача']['title'] else ""
                cache[task['id']] = {
                    'title': task_title,
                    'status': task['properties']['Статус']['status']['name'] if task['properties']['Статус']['status'] else "",
                    'participants': [p['name'] for p in task['properties']['Участники']['people']] if task['properties']['Участники']['people'] else []
                }
            
            self.active_tasks_cache = cache
            self.cache_timestamp = datetime.now()
            
            logger.info(f"Кэш задач обновлен: {len(cache)} активных задач")
            return cache
            
        except Exception as e:
            logger.error(f"Ошибка обновления кэша задач: {e}")
            return {}

    def find_related_task(self, material_name: str, figma_link: FigmaLink) -> Optional[str]:
        """Поиск связанной задачи по названию материала/Figma"""
        if not self.active_tasks_cache:
            return None
        
        search_terms = [
            material_name.lower(),
            figma_link.title.lower(),
            # Ключевые слова из URL
            *figma_link.title.lower().split()
        ]
        
        best_match = None
        best_score = 0
        
        for task_id, task_data in self.active_tasks_cache.items():
            task_title = task_data['title'].lower()
            
            # Простой поиск совпадений
            score = 0
            for term in search_terms:
                if term in task_title:
                    score += len(term)
            
            if score > best_score:
                best_score = score
                best_match = task_id
        
        return best_match if best_score > 3 else None  # Минимальный порог

    def generate_smart_tags(self, material_name: str, figma_link: FigmaLink) -> List[str]:
        """Умное тегирование на основе названия и контекста"""
        tags = []
        
        content = f"{material_name} {figma_link.title}".lower()
        
        # Детерминированные правила тегирования (98% случаев)
        tag_rules = {
            'Дизайн': ['дизайн', 'макет', 'ui', 'ux', 'интерфейс', 'layout'],
            'Бренд': ['логотип', 'бренд', 'logo', 'brand', 'фирм', 'стиль'],
            'Веб': ['сайт', 'web', 'лендинг', 'landing', 'веб'],
            'SMM': ['пост', 'stories', 'сторис', 'инста', 'соцсет'],
            'Полиграфия': ['баннер', 'флаер', 'листовка', 'печать', 'полиграф'],
            'Видео': ['видео', 'анимация', 'motion', 'ролик'],
            'Фото': ['фото', 'photo', 'съемка', 'обработка']
        }
        
        for tag, keywords in tag_rules.items():
            if any(keyword in content for keyword in keywords):
                tags.append(tag)
        
        # Если нет тегов - ставим Дизайн по умолчанию
        if not tags:
            tags.append('Дизайн')
        
        return tags

    def generate_checklist_items(self, material_name: str, tags: List[str]) -> List[str]:
        """Генерация чеклиста/правок для подзадач"""
        checklist = []
        
        # Базовые проверки для всех материалов
        checklist.extend([
            "Проверить соответствие брендбуку",
            "Проверить качество изображения (min 300 DPI)",
            "Проверить читаемость текста"
        ])
        
        # Специфичные проверки по тегам
        tag_checklists = {
            'Бренд': [
                "Проверить корректность логотипа",
                "Проверить цветовую схему бренда",
                "Проверить типографику"
            ],
            'Веб': [
                "Проверить адаптивность дизайна",
                "Проверить UX/UI паттерны",
                "Проверить accessibility"
            ],
            'SMM': [
                "Проверить размеры под платформу",
                "Проверить Call-to-Action",
                "Проверить hashtags"
            ],
            'Полиграфия': [
                "Проверить вылеты и обрезку",
                "Проверить CMYK цвета",
                "Проверить размеры файла"
            ]
        }
        
        for tag in tags:
            if tag in tag_checklists:
                checklist.extend(tag_checklists[tag])
        
        return checklist[:6]  # Максимум 6 пунктов

    async def create_material_with_relations(self, material_request: MaterialRequest, preview_url: str) -> Optional[str]:
        """Создание материала с автосвязями"""
        try:
            # Подготовка данных для материала
            material_data = {
                "Name": {"title": [{"text": {"content": material_request.name}}]},
                "URL": {"url": material_request.figma_link.url},
                "Описание": {"rich_text": [{"text": {"content": material_request.description}}]},
                "Теги": {"multi_select": [{"name": tag} for tag in material_request.tags]},
                "Статус": {"status": {"name": "In progress"}},
                "Date": {"date": {"start": datetime.now().isoformat()}},
                "Вес": {"number": 5}  # Средняя важность
            }
            
            # Добавляем Files & media если есть превью
            if preview_url:
                material_data["Files & media"] = {
                    "files": [{"external": {"url": preview_url}}]
                }
            
            # Создаем материал
            material_page = self.notion.create_page(
                database_id=self.materials_db,
                properties=material_data
            )
            
            if not material_page:
                return None
            
            material_id = material_page['id']
            
            # Устанавливаем cover если есть превью
            if preview_url:
                try:
                    self.notion.update_page_cover(material_id, preview_url)
                except Exception as e:
                    logger.warning(f"Не удалось установить cover: {e}")
            
            # Создаем подзадачи из чеклиста
            checklist = self.generate_checklist_items(material_request.name, material_request.tags)
            await self.create_subtasks_from_checklist(material_request.related_task, checklist)
            
            # Автоматическое распределение по базам через теги
            await self.auto_distribute_by_tags(material_request, material_id)
            
            logger.info(f"Материал создан: {material_id}")
            return material_id
            
        except Exception as e:
            logger.error(f"Ошибка создания материала: {e}")
            return None

    async def create_subtasks_from_checklist(self, parent_task_id: str, checklist: List[str]):
        """Создание подзадач из чеклиста"""
        if not parent_task_id or not checklist:
            return
        
        try:
            for item in checklist:
                subtask_data = {
                    "Подзадачи": {"title": [{"text": {"content": item}}]},
                    "Задачи": {"relation": [{"id": parent_task_id}]},
                    " Статус": {"status": {"name": "To do"}},
                    "Направление": {"multi_select": [{"name": "Дизайн"}]},
                    "Приоритет": {"select": {"name": "Средний"}},
                    "Часы": {"number": 0.5}  # 30 минут на проверку
                }
                
                self.notion.create_page(
                    database_id=self.subtasks_db,
                    properties=subtask_data
                )
                
            logger.info(f"Создано {len(checklist)} подзадач для задачи {parent_task_id}")
            
        except Exception as e:
            logger.error(f"Ошибка создания подзадач: {e}")

    async def auto_distribute_by_tags(self, material_request: MaterialRequest, material_id: str):
        """Автоматическое распределение материала по базам через теги"""
        try:
            # Правила распределения по тегам
            distribution_rules = {
                'Бренд': {'db': self.guides_db, 'reason': 'брендинг'},
                'Стратегия': {'db': self.ideas_db, 'reason': 'стратегическая идея'},
                'Концепт': {'db': self.ideas_db, 'reason': 'концептуальная идея'}
            }
            
            for tag in material_request.tags:
                if tag in distribution_rules:
                    rule = distribution_rules[tag]
                    
                    # Создаем запись в соответствующей базе
                    target_data = {
                        "Name": {"title": [{"text": {"content": f"{material_request.name} ({rule['reason']})"}}]},
                        "Описание": {"rich_text": [{"text": {"content": f"Автоматически создано из материала: {material_request.figma_link.url}"}}]},
                        "Теги": {"multi_select": [{"name": tag}]},
                        "Статус": {"status": {"name": "To do"}},
                        "Вес": {"number": 3}
                    }
                    
                    self.notion.create_page(
                        database_id=rule['db'],
                        properties=target_data
                    )
                    
                    logger.info(f"Материал распределен в {rule['db']} по тегу {tag}")
                    
        except Exception as e:
            logger.error(f"Ошибка автораспределения: {e}")

    async def handle_figma_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка Figma URL"""
        message_text = update.message.text
        figma_link = self.parse_figma_url(message_text)
        
        if not figma_link:
            await update.message.reply_text(
                "❌ Не могу распознать Figma ссылку.\n"
                "Пример правильной ссылки: https://www.figma.com/file/ABC123/My-Design"
            )
            return
        
        # Показываем прогресс
        progress_msg = await update.message.reply_text("🔄 Обрабатываю Figma ссылку...")
        
        try:
            # 1. Получаем превью
            await progress_msg.edit_text("🖼️ Получаю превью изображения...")
            preview_url = await self.get_figma_preview(figma_link)
            
            # 2. Загружаем на Яндекс.Диск
            if preview_url:
                await progress_msg.edit_text("☁️ Загружаю на Яндекс.Диск...")
                disk_url = await self.upload_to_yandex_disk(preview_url, figma_link.title)
                preview_url = disk_url or preview_url
            
            # 3. Обновляем кэш задач
            if not self.active_tasks_cache:
                await progress_msg.edit_text("🔄 Обновляю кэш задач...")
                await self.refresh_tasks_cache()
            
            # 4. Ищем связанную задачу
            related_task = self.find_related_task(figma_link.title, figma_link)
            
            # 5. Генерируем теги
            tags = self.generate_smart_tags(figma_link.title, figma_link)
            
            # Создаем request
            material_request = MaterialRequest(
                figma_link=figma_link,
                name=figma_link.title,
                description=f"Материал из Figma: {figma_link.link_type}",
                tags=tags,
                related_task=related_task
            )
            
            # Показываем конфирмацию
            await self.show_confirmation(update, progress_msg, material_request, preview_url)
            
        except Exception as e:
            logger.error(f"Ошибка обработки Figma URL: {e}")
            await progress_msg.edit_text(f"❌ Ошибка обработки: {str(e)}")

    async def show_confirmation(self, update: Update, progress_msg, material_request: MaterialRequest, preview_url: str):
        """Показ конфирмации создания материала"""
        # Информация о найденной задаче
        task_info = ""
        if material_request.related_task and material_request.related_task in self.active_tasks_cache:
            task_data = self.active_tasks_cache[material_request.related_task]
            task_info = f"🔗 Связанная задача: {task_data['title']}\n"
        
        confirmation_text = f"""
🎨 **МАТЕРИАЛ ГОТОВ К СОЗДАНИЮ**

📝 **Название:** {material_request.name}
🏷️ **Теги:** {', '.join(material_request.tags)}
{task_info}
🖼️ **Превью:** {"✅ Да" if preview_url else "❌ Нет"}

✅ **ЧТО СОЗДАСТСЯ:**
• Материал в Notion с обложкой
• Автосвязь с задачей (если найдена)
• Чеклист правок → подзадачи
• Автораспределение по тегам

Создаем?
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Создать", callback_data=f"create_material_{update.message.message_id}"),
                InlineKeyboardButton("❌ Отмена", callback_data="cancel_material")
            ]
        ])
        
        # Сохраняем данные в context
        context = {
            'material_request': material_request,
            'preview_url': preview_url
        }
        
        # Используем глобальную переменную для простоты (в продакшене использовать Redis/DB)
        self.pending_materials = getattr(self, 'pending_materials', {})
        self.pending_materials[update.message.message_id] = context
        
        await progress_msg.edit_text(confirmation_text, reply_markup=keyboard, parse_mode='Markdown')

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("create_material_"):
            message_id = int(query.data.split("_")[-1])
            
            if hasattr(self, 'pending_materials') and message_id in self.pending_materials:
                material_context = self.pending_materials[message_id]
                material_request = material_context['material_request']
                preview_url = material_context['preview_url']
                
                await query.edit_message_text("🚀 Создаю материал...")
                
                # Создаем материал
                material_id = await self.create_material_with_relations(material_request, preview_url)
                
                if material_id:
                    notion_url = f"https://www.notion.so/{material_id.replace('-', '')}"
                    success_text = f"""
✅ **МАТЕРИАЛ СОЗДАН УСПЕШНО!**

🔗 [Открыть в Notion]({notion_url})

📊 **ЧТО СДЕЛАНО:**
• Материал с превью создан
• {"Связан с задачей" if material_request.related_task else "Задача не найдена"}
• Созданы подзадачи-проверки
• Распределен по тегам
                    """
                    await query.edit_message_text(success_text, parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Ошибка создания материала")
                
                # Очищаем кэш
                del self.pending_materials[message_id]
            else:
                await query.edit_message_text("❌ Данные запроса устарели")
                
        elif query.data == "cancel_material":
            await query.edit_message_text("❌ Создание материала отменено")

    async def refresh_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда обновления кэша"""
        msg = await update.message.reply_text("🔄 Обновляю кэш задач...")
        
        cache = await self.refresh_tasks_cache()
        
        await msg.edit_text(f"✅ Кэш обновлен\n📊 Активных задач: {len(cache)}")

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика бота"""
        stats_text = f"""
📊 **СТАТИСТИКА БОТА**

🗂️ **Базы данных:**
• Материалы: {self.materials_db[-8:]}...
• Задачи: {self.tasks_db[-8:]}...
• Подзадачи: {self.subtasks_db[-8:] if self.subtasks_db else 'Н/Д'}...

⚡ **Кэш:**
• Активных задач: {len(self.active_tasks_cache)}
• Последнее обновление: {self.cache_timestamp.strftime('%H:%M:%S') if self.cache_timestamp else 'Никогда'}

🎯 **Возможности:**
• Обработка Figma ссылок
• Автосвязывание с задачами  
• Генерация чеклистов
• Умное тегирование
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Справка по командам"""
        help_text = """
🆘 **СПРАВКА ПО БОТУ**

📋 **КОМАНДЫ:**
• `/start` - приветствие и инструкция
• `/refresh` - обновить кэш активных задач
• `/stats` - статистика и состояние бота
• `/help` - эта справка

🔗 **ИСПОЛЬЗОВАНИЕ:**
Просто отправьте Figma ссылку, бот автоматически:
1. Получит превью изображения
2. Загрузит на Яндекс.Диск
3. Создаст материал в Notion с обложкой
4. Свяжет с подходящей задачей
5. Создаст подзадачи-проверки
6. Распределит по базам через теги

🎯 **ПОДДЕРЖИВАЕМЫЕ ССЫЛКИ:**
• `figma.com/file/...`
• `figma.com/proto/...`
• `figma.com/design/...`
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

    def run(self):
        """Запуск бота"""
        if not self.telegram_token:
            logger.error("TELEGRAM_BOT_TOKEN не найден в .env")
            return
        
        # Создаем приложение
        app = Application.builder().token(self.telegram_token).build()
        
        # Регистрируем команды
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("refresh", self.refresh_command))
        app.add_handler(CommandHandler("stats", self.stats_command))
        app.add_handler(CommandHandler("help", self.help_command))
        
        # Обработчик Figma URL
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_figma_url))
        
        # Обработчик callback кнопок
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("🚀 Figma Materials Bot запущен!")
        print("🎨 FIGMA MATERIALS BOT - Революционная автоматизация!")
        print("📤 Отправьте Figma ссылку для обработки")
        
        # Запускаем бота
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = FigmaMaterialsBot()
    bot.run()