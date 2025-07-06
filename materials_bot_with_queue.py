import os
import asyncio
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
)
from notion_client import AsyncClient
import aiohttp

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

# --- Конфиг ---
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_MATERIALS_DB_ID = os.getenv('NOTION_MATERIALS_DB_ID', '1d9ace03d9ff804191a4d35aeedcbbd4')
NOTION_IDEAS_DB_ID = os.getenv('NOTION_IDEAS_DB_ID', 'ad92a6e21485428c84de8587706b3be1')
YA_TOKEN = os.getenv('YA_ACCESS_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logger.info(f"Токены загружены: Notion={bool(NOTION_TOKEN)}, Yandex={bool(YA_TOKEN)}, Telegram={bool(TELEGRAM_TOKEN)}")

YANDEX_BASE_URL = "https://cloud-api.yandex.net/v1/disk"

# --- Очередь и состояния ---
user_states = {}  # user_id -> {'current': {...}, 'pending_fields': {...}, 'database_choice': 'materials'|'ideas', 'file_url': str, 'file_name': str}
file_queues = {}  # user_id -> [{'file_url': str, 'file_name': str, 'file_type': str}]

# --- Вспомогательные функции ---
async def upload_to_yandex(telegram_file_url: str, filename: str) -> Dict[str, Any]:
    logger.info(f"Начинаю загрузку файла {filename} в Yandex Disk")
    remote_path = f"/telegram_uploads/{filename}"
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
            logger.info(f"Получена ссылка для загрузки: {upload_url}")
        
        # Скачиваем файл из Telegram
        async with session.get(telegram_file_url) as tg_resp:
            if tg_resp.status != 200:
                logger.error(f"Ошибка получения файла из Telegram: {tg_resp.status}")
                return {'success': False, 'error': f"Ошибка получения файла из Telegram: {tg_resp.status}", 'url': None}
            file_data = await tg_resp.read()
            logger.info(f"Файл скачан из Telegram, размер: {len(file_data)} байт")
        
        # Загружаем в Yandex Disk
        async with session.put(upload_url, data=file_data, headers={"Content-Type": "application/octet-stream"}) as put_resp:
            if put_resp.status != 201:
                error_text = await put_resp.text()
                logger.error(f"Ошибка загрузки в Yandex Disk: {put_resp.status} - {error_text}")
                return {'success': False, 'error': f"Ошибка загрузки в Yandex Disk: {put_resp.status}", 'url': None}
            logger.info(f"Файл успешно загружен в Yandex Disk")
        
        # Делаем файл публичным
        pub_url = f"{YANDEX_BASE_URL}/resources/publish"
        params = {"path": remote_path}
        async with session.put(pub_url, params=params, headers=headers) as resp:
            pass  # ignore errors (already published)
        
        # Получаем публичную ссылку
        meta_url = f"{YANDEX_BASE_URL}/resources"
        async with session.get(meta_url, params={"path": remote_path}, headers=headers) as meta_resp:
            meta_data = await meta_resp.json()
            public_url = meta_data.get("public_url")
            logger.info(f"Получена публичная ссылка: {public_url}")
        
        return {'success': True, 'url': public_url, 'filename': filename}

async def create_notion_material(fields: Dict[str, Any], file_url: str, file_name: str):
    logger.info(f"Создаю запись в базе Materials: {fields.get('name', file_name)}")
    client = AsyncClient(auth=NOTION_TOKEN)
    props = {
        "Name": {"title": [{"text": {"content": fields.get('name', file_name)}}]},
        "Описание": {"rich_text": [{"text": {"content": fields.get('description', '')}}]},
        "Date": {"date": {"start": datetime.now().isoformat()}},
        "Статус": {"status": {"name": "To do"}},
        "Теги": {"multi_select": [{"name": t.strip()} for t in fields.get('tags', '').split(',') if t.strip()]},
        "URL": {"url": file_url}
    }
    result = await client.pages.create(parent={"database_id": NOTION_MATERIALS_DB_ID}, properties=props)
    logger.info(f"Запись создана в Materials: {result.get('id')}")
    return result

async def create_notion_idea(fields: Dict[str, Any], file_url: str, file_name: str):
    logger.info(f"Создаю запись в базе Ideas: {fields.get('name', file_name)}")
    client = AsyncClient(auth=NOTION_TOKEN)
    props = {
        "Name": {"title": [{"text": {"content": fields.get('name', file_name)}}]},
        "Описание": {"rich_text": [{"text": {"content": fields.get('description', '')}}]},
        "Date": {"date": {"start": datetime.now().isoformat()}},
        "Статус": {"status": {"name": "To do"}},
        "Теги": {"multi_select": [{"name": t.strip()} for t in fields.get('tags', '').split(',') if t.strip()]},
        "URL": {"url": file_url}
    }
    result = await client.pages.create(parent={"database_id": NOTION_IDEAS_DB_ID}, properties=props)
    logger.info(f"Запись создана в Ideas: {result.get('id')}")
    return result

async def add_to_queue(user_id: int, file_url: str, file_name: str, file_type: str):
    """Добавляет файл в очередь пользователя"""
    if user_id not in file_queues:
        file_queues[user_id] = []
    
    file_queues[user_id].append({
        'file_url': file_url,
        'file_name': file_name,
        'file_type': file_type
    })
    
    logger.info(f"Файл {file_name} добавлен в очередь пользователя {user_id}. Размер очереди: {len(file_queues[user_id])}")

async def get_next_file_from_queue(user_id: int):
    """Получает следующий файл из очереди пользователя"""
    if user_id not in file_queues or not file_queues[user_id]:
        return None
    
    return file_queues[user_id].pop(0)

async def get_queue_status(user_id: int):
    """Возвращает статус очереди пользователя"""
    if user_id not in file_queues:
        return 0
    return len(file_queues[user_id])

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} запустил бота")
    await update.message.reply_text(
        "Привет! Просто отправь файл, и я помогу загрузить его в Яндекс.Диск и оформить карточку в Notion.\n\n"
        "После загрузки файла я спрошу, в какую базу создать запись (Материалы или Идеи), "
        "а затем попрошу заполнить поля для карточки.\n\n"
        "Можно отправлять несколько файлов подряд — они попадут в очередь!\n\n"
        "Команды:\n"
        "/queue - показать статус очереди\n"
        "/clear - очистить очередь"
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Получен файл от пользователя {user_id}")
    
    # Правильно определяем тип файла и получаем имя
    if update.message.document:
        file_obj = update.message.document
        file_type = "document"
        file_name = file_obj.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    elif update.message.photo:
        file_obj = update.message.photo[-1]  # Берем самое большое фото
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
        await update.message.reply_text("Не удалось определить тип файла.")
        return
    
    file_id = file_obj.file_id
    logger.info(f"Файл: {file_name}, тип: {file_type}, ID: {file_id}")
    
    # Получаем ссылку на файл
    file_info = await context.bot.get_file(file_id)
    telegram_file_url = file_info.file_path
    
    # Сразу обрабатываем файл
    await update.message.reply_text(f"🚀 Начинаю загрузку файла {file_name} в Яндекс.Диск...")
    
    try:
        upload_result = await upload_to_yandex(telegram_file_url, file_name)
        if not upload_result['success']:
            await update.message.reply_text(f"❌ Ошибка загрузки: {upload_result['error']}")
            return
        
        await update.message.reply_text(f"✅ Файл загружен! Ссылка: {upload_result['url']}")
        
        # Проверяем, есть ли уже активная обработка
        if user_id in user_states and user_states[user_id].get('file_url'):
            # Добавляем в очередь
            await add_to_queue(user_id, upload_result['url'], file_name, file_type)
            queue_size = await get_queue_status(user_id)
            await update.message.reply_text(
                f"📋 Файл добавлен в очередь! Позиция: {queue_size}\n"
                f"Сначала завершим обработку текущего файла."
            )
        else:
            # Начинаем обработку сразу
            keyboard = [
                [InlineKeyboardButton("📋 Материалы", callback_data="db_materials")],
                [InlineKeyboardButton("💡 Идеи", callback_data="db_ideas")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "В какую базу данных создать запись?",
                reply_markup=reply_markup
            )
            
            # Сохраняем информацию о файле для последующей обработки
            user_states[user_id] = {
                'current': None, 
                'pending_fields': {}, 
                'database_choice': None,
                'file_url': upload_result['url'],
                'file_name': file_name
            }
        
    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_name}: {e}")
        await update.message.reply_text(f"❌ Ошибка при обработке файла: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        return
    
    # Парсим поля
    text = update.message.text
    fields = {}
    for part in text.split(','):
        if ':' in part:
            key, value = part.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key in ['название', 'name']:
                fields['name'] = value
            elif key in ['описание', 'description']:
                fields['description'] = value
            elif key in ['теги', 'tags']:
                fields['tags'] = value
            elif key in ['категория', 'category']:
                fields['category'] = value
    
    # Если есть название, создаем запись в Notion
    if fields.get('name'):
        try:
            file_url = user_states[user_id].get('file_url')
            file_name = user_states[user_id].get('file_name')
            database_choice = user_states[user_id]['database_choice']
            
            if database_choice == 'materials':
                notion_resp = await create_notion_material(fields, file_url, file_name)
                db_name = "Материалы"
            else:
                notion_resp = await create_notion_idea(fields, file_url, file_name)
                db_name = "Идеи"
            
            notion_id = notion_resp.get('id', '')
            notion_url = f"https://notion.so/{notion_id.replace('-', '')}"
            await update.message.reply_text(
                f"📋 Карточка создана в базе '{db_name}': {notion_url}"
            )
            
            # Проверяем очередь на следующий файл
            next_file = await get_next_file_from_queue(user_id)
            if next_file:
                # Обрабатываем следующий файл
                keyboard = [
                    [InlineKeyboardButton("📋 Материалы", callback_data="db_materials")],
                    [InlineKeyboardButton("💡 Идеи", callback_data="db_ideas")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"🔄 Обрабатываем следующий файл: {next_file['file_name']}\n"
                    "В какую базу данных создать запись?",
                    reply_markup=reply_markup
                )
                
                # Обновляем состояние для следующего файла
                user_states[user_id] = {
                    'current': None, 
                    'pending_fields': {}, 
                    'database_choice': None,
                    'file_url': next_file['file_url'],
                    'file_name': next_file['file_name']
                }
                
                queue_size = await get_queue_status(user_id)
                if queue_size > 0:
                    await update.message.reply_text(f"📋 В очереди еще {queue_size} файлов")
            else:
                # Очищаем состояние пользователя
                user_states.pop(user_id, None)
                await update.message.reply_text("✅ Все файлы обработаны!")
            
        except Exception as e:
            logger.error(f"Ошибка при создании записи в Notion: {e}")
            await update.message.reply_text(f"❌ Ошибка при создании записи в Notion: {e}")
    else:
        await update.message.reply_text("Пожалуйста, укажите название для карточки.")

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
            "Теперь заполни поля для карточки:\n"
            "*Название* (обязательно)\n*Описание* (опционально)\n*Теги* (через запятую, опционально)\n\n"
            "Пример: Название: Презентация, Описание: Вебинар, Теги: обучение, презентация",
            parse_mode='Markdown'
        )
    elif query.data == "db_ideas":
        user_states[user_id]['database_choice'] = 'ideas'
        await query.edit_message_text(
            "💡 Создаем запись в базе 'Идеи'.\n\n"
            "Теперь заполни поля для карточки:\n"
            "*Название* (обязательно)\n*Описание* (опционально)\n*Теги* (через запятую, опционально)\n\n"
            "Пример: Название: Новая функция, Описание: Автоматизация, Теги: разработка, инновации",
            parse_mode='Markdown'
        )

async def on_new_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Просто отправь файл для загрузки.")

async def queue_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус очереди файлов пользователя"""
    user_id = update.effective_user.id
    queue_size = await get_queue_status(user_id)
    
    if queue_size == 0:
        await update.message.reply_text("📋 Очередь пуста")
    else:
        await update.message.reply_text(f"📋 В очереди {queue_size} файлов")
        
        # Показываем список файлов в очереди
        if user_id in file_queues:
            file_list = "\n".join([f"• {file['file_name']}" for file in file_queues[user_id]])
            await update.message.reply_text(f"Файлы в очереди:\n{file_list}")

async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очищает очередь файлов пользователя"""
    user_id = update.effective_user.id
    
    if user_id in file_queues:
        queue_size = len(file_queues[user_id])
        file_queues[user_id].clear()
        await update.message.reply_text(f"🗑️ Очередь очищена! Удалено {queue_size} файлов")
    else:
        await update.message.reply_text("📋 Очередь уже пуста")

async def main():
    logger.info("Запуск бота...")
    
    # Проверяем токены
    if not all([NOTION_TOKEN, YA_TOKEN, TELEGRAM_TOKEN]):
        logger.error("Отсутствуют необходимые токены!")
        return
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, on_new_chat_member))
    application.add_handler(CommandHandler("queue", queue_status))
    application.add_handler(CommandHandler("clear", clear_queue))
    
    logger.info("✅ Бот с очередью и выбором базы данных запущен!")
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            loop.create_task(application.run_polling())
        else:
            loop.run_until_complete(application.run_polling())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    import sys
    import asyncio
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}") 