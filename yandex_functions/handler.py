#!/usr/bin/env python3
"""
🔗 Webhook обработчик для Notion с обработкой обложек и Files & media
ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ - собрана на основе предыдущего опыта.
"""

import json
import os
import re
from urllib.parse import quote
import aiohttp
import asyncio
import traceback

# --- CONFIGURATION ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")

# --- CONSTANTS ---
CLOUDFLARE_WORKER_URL = "https://delicate-hat-c01b.e1vice.workers.dev"
NOTION_API_VERSION = "2022-06-28"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Базы данных для обработки
DATABASES = {
    "materials": "1d9ace03-d9ff-8041-91a4-d35aeedcbbd4",
    "design_tasks": "d09df250-ce7e-4e0d-9fbe-4e036d320def", 
    "subtasks": "9c5f4269-d614-49b6-a748-5579a3c21da3",
    "projects": "342f18c6-7a5e-41fe-ad73-dcec00770f4e",
    "ideas": "ad92a6e2-1485-428c-84de-8587706b3be1"
}

def log(message):
    """Централизованная функция логирования."""
    print(f"[HANDLER] {message}")

def get_base_headers():
    """Возвращает базовые заголовки для всех запросов к Notion через прокси."""
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_API_VERSION,
        "User-Agent": USER_AGENT,
    }

def get_base_headers_with_content_type():
    """Возвращает базовые заголовки с Content-Type для POST/PATCH запросов."""
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
        "User-Agent": USER_AGENT,
    }

async def get_notion_page(session, page_id):
    """Получает данные страницы Notion через Cloudflare Worker."""
    url = f"{CLOUDFLARE_WORKER_URL}/v1/pages/{page_id}"
    headers = get_base_headers()
    
    log(f"🔍 [get_notion_page] Запрос страницы: {page_id}")
    log(f"🔑 Токен: {NOTION_TOKEN[:10] if NOTION_TOKEN else 'None'}...")
    log(f"🔑 Полный токен: {NOTION_TOKEN}")
    log(f"🔑 Длина токена: {len(NOTION_TOKEN) if NOTION_TOKEN else 0}")
    log(f"🎯 URL через прокси: {url}")
    
    async with session.get(url, headers=headers) as response:
        log(f"✅ [get_notion_page] Ответ от прокси: {response.status}")
        if response.status == 200:
            return await response.json()
        
        error_text = await response.text()
        log(f"❌ [get_notion_page] Ошибка: {response.status} - {error_text}")
        return None

async def update_notion_cover(session, page_id, cover_url):
    """Обновляет обложку страницы Notion."""
    url = f"{CLOUDFLARE_WORKER_URL}/v1/pages/{page_id}"
    data = {"cover": {"type": "external", "external": {"url": cover_url}}}
    headers = get_base_headers_with_content_type()
    
    log(f"🖼️ [update_notion_cover] Обновление обложки для {page_id}...")
    async with session.patch(url, json=data, headers=headers) as response:
        success = response.status == 200
        log(f"🖼️ [update_notion_cover] Результат: {'✅' if success else '❌'}")
        if not success:
            log(f"❌ [update_notion_cover] Ошибка: {await response.text()}")
        return success

async def update_notion_files_media(session, page_id, file_url):
    """Обновляет свойство 'Files & media' страницы Notion."""
    url = f"{CLOUDFLARE_WORKER_URL}/v1/pages/{page_id}"
    data = {
        "properties": {
            "Files & media": {
                "files": [{"name": "Material File", "type": "external", "external": {"url": file_url}}]
            }
        }
    }
    headers = get_base_headers_with_content_type()

    log(f"📎 [update_notion_files_media] Обновление Files & media для {page_id}...")
    async with session.patch(url, json=data, headers=headers) as response:
        success = response.status == 200
        log(f"📎 [update_notion_files_media] Результат: {'✅' if success else '❌'}")
        if not success:
            log(f"❌ [update_notion_files_media] Ошибка: {await response.text()}")
        return success

async def get_figma_cover(session, figma_url):
    """Извлекает URL превью из ссылки Figma."""
    # Универсальный поиск file_key
    file_key_match = re.search(r"(?:file|design)/([a-zA-Z0-9]+)", figma_url)
    if not file_key_match: return None
    file_key = file_key_match.group(1)

    # Универсальный поиск node_id
    node_id_match = re.search(r"node-id=([a-zA-Z0-9%:-]+)", figma_url)
    if not node_id_match: return None
    node_id = quote(node_id_match.group(1).replace(':', '-')) # Figma API предпочитает '-'

    api_url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format=png&scale=2"
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    
    async with session.get(api_url, headers=headers) as response:
        if response.status != 200:
             log(f"❌ [get_figma_cover] Ошибка API Figma: {response.status} - {await response.text()}")
             return None
        data = await response.json()
        if data.get('err'):
            log(f"❌ [get_figma_cover] Ошибка в ответе Figma: {data['err']}")
            return None
        
        image_url = data.get('images', {}).get(node_id.replace('%3A', ':')) # API возвращает ':' в ID
        if not image_url:
             image_url = data.get('images', {}).get(node_id)
        
        return image_url

async def get_lightshot_image(session, lightshot_url):
    """Извлекает URL изображения из ссылки LightShot (РАБОЧАЯ ВЕРСИЯ)."""
    try:
        log(f"🔍 [get_lightshot_image] Запрашиваю LightShot: {lightshot_url}")
        
        # Используем правильные заголовки для обхода блокировки
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        async with session.get(lightshot_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            log(f"📊 [get_lightshot_image] Статус ответа: {response.status}")
            if response.status != 200:
                log(f"❌ [get_lightshot_image] Ошибка HTTP: {response.status}")
                return None
            
            html = await response.text()
            log(f"📄 [get_lightshot_image] Размер HTML: {len(html)} символов")
            
            # Ищем прямую ссылку на изображение (как в рабочей версии)
            image_patterns = [
                r'https://image\.prntscr\.com/image/[^"\']+',
                r'https://[^"\']*\.png',
                r'https://[^"\']*\.jpg',
                r'https://[^"\']*\.jpeg',
                r'https://[^"\']*\.webp'
            ]
            
            for pattern in image_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    image_url = matches[0]
                    log(f"✅ [get_lightshot_image] Найдено изображение LightShot: {image_url}")
                    return image_url
            
            # Если не нашли, попробуем извлечь из мета-тегов
            meta_pattern = r'<meta property="og:image" content="([^"]+)"'
            meta_matches = re.findall(meta_pattern, html)
            if meta_matches:
                image_url = meta_matches[0]
                log(f"✅ [get_lightshot_image] Найдено изображение в meta: {image_url}")
                return image_url
            
            log(f"⚠️ [get_lightshot_image] Изображение не найдено в HTML")
            return None
            
    except Exception as e:
        log(f"❌ [get_lightshot_image] Ошибка: {e}")
        return None

async def get_yandex_disk_image(session, yandex_url):
    """Формирует прямую ссылку на скачивание из Яндекс.Диска."""
    # Прямая ссылка для превью не требует API токена
    public_key = quote(yandex_url)
    api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}"
    async with session.get(api_url) as response:
        if response.status != 200:
            log(f"❌ [get_yandex_disk_image] Ошибка API Яндекс.Диска: {response.status}")
            return None
        data = await response.json()
        return data.get("preview") # Возвращаем URL превью

async def get_cover_url_from_link(session, link):
    """Определяет тип ссылки и вызывает соответствующий обработчик."""
    if "figma.com" in link:
        log(f"🎨 Обрабатываю Figma: {link}")
        return await get_figma_cover(session, link)
    if "prnt.sc" in link or "lightshot.cc" in link:
        log(f"📸 Обрабатываю LightShot: {link}")
        return await get_lightshot_image(session, link)
    if "disk.yandex.ru" in link:
        log(f"☁️ Обрабатываю Яндекс.Диск: {link}")
        return await get_yandex_disk_image(session, link)
    if any(ext in link.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']):
        log(f"🖼️ Прямое изображение: {link}")
        return link
    log(f"⚠️ Неизвестный тип ссылки: {link}")
    return None

async def process_page_update(session, page_id, page_data):
    """Основная логика обработки обновления страницы."""
    log(f"🔄 [process_page_update] Начинаю обработку страницы {page_id}")
    properties = page_data.get("properties", {})
    
    url_property = None
    for prop_name in ["URL", "Link", "Ссылка", "url", "link"]:
        if prop_name in properties:
            prop = properties[prop_name]
            if prop.get("type") == "url" and prop.get("url"):
                url_property = prop["url"]
                log(f"🔗 [process_page_update] Найден URL: {url_property}")
                break
    
    if not url_property:
        log("⚠️ [process_page_update] URL не найден в свойствах.")
        return

    cover_url = await get_cover_url_from_link(session, url_property)
    if not cover_url:
        log("⚠️ [process_page_update] Не удалось получить URL обложки.")
        return

    log(f"✅ [process_page_update] Обложка получена: {cover_url[:100]}...")
    await update_notion_cover(session, page_id, cover_url)
    
    parent_db_id = page_data.get("parent", {}).get("database_id", "").replace("-", "")
    if parent_db_id == DATABASES["materials"].replace("-", ""):
        log("📎 [process_page_update] Обновляю Files & media для материалов...")
        await update_notion_files_media(session, page_id, cover_url)

async def handler_async(event, context):
    """Асинхронный обработчик входящих запросов."""
    log("🚀 ПОЛУЧЕН ЗАПРОС")
    log(f"🔍 Переменные окружения: NOTION_TOKEN={'✅' if NOTION_TOKEN else '❌'}, FIGMA_TOKEN={'✅' if FIGMA_TOKEN else '❌'}, YANDEX_DISK_TOKEN={'✅' if YANDEX_DISK_TOKEN else '❌'}")

    try:
        webhook_data = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        if not webhook_data:
            webhook_data = event # Если body пуст, но сам event - это JSON
    except (json.JSONDecodeError, TypeError):
        log("⚠️ Не удалось декодировать JSON из body, используем event как есть.")
        webhook_data = event

    # Для Notion webhooks, которые приходят без 'body'
    if 'event' in webhook_data and 'page' in webhook_data:
         log("Обнаружен формат Notion webhook v2")

    # Обработка challenge для верификации URL вебхука
    if 'challenge' in webhook_data:
        challenge = webhook_data['challenge']
        log(f"✅ URL verification challenge: {challenge}")
        return {"statusCode": 200, "body": json.dumps({"challenge": challenge})}
    
    # Извлечение page_id из разных возможных структур
    page_id = None
    if 'page' in webhook_data and isinstance(webhook_data['page'], dict) and 'id' in webhook_data['page']:
        page_id = webhook_data['page']['id']
    elif 'entity' in webhook_data and 'id' in webhook_data['entity']: # Fallback
        page_id = webhook_data['entity']['id']

    if not page_id:
        log(f"❌ ID страницы не найден в webhook. Структура: {list(webhook_data.keys())}")
        return {'statusCode': 200, 'body': 'OK (page_id not found)'}

    # Форматируем page_id в правильный UUID формат (добавляем дефисы)
    log(f"🔧 [handler_async] Исходный page_id: {page_id} (длина: {len(page_id) if page_id else 0})")
    if page_id and len(page_id) == 32 and '-' not in page_id:  # UUID без дефисов
        page_id = f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:32]}"
        log(f"🔧 [handler_async] Форматирован page_id: {page_id}")
    elif page_id and len(page_id) == 36 and page_id.count('-') == 4:  # UUID с дефисами
        log(f"🔧 [handler_async] page_id уже в правильном формате: {page_id}")
    else:
        log(f"⚠️ [handler_async] Неизвестный формат page_id: {page_id}")
        # Попробуем использовать как есть, возможно это другой формат ID

    log(f"📄 Обрабатываю страницу: {page_id}")
    
    async with aiohttp.ClientSession() as session:
        page_data = await get_notion_page(session, page_id)
        if not page_data:
            log("❌ Не удалось получить данные страницы. Завершаю.")
            return {'statusCode': 200, 'body': 'OK (page data fetch failed)'}
        
        await process_page_update(session, page_id, page_data)
            
    return {'statusCode': 200, 'body': 'OK'}

def handler(event, context):
    """Синхронная точка входа для Yandex Cloud Function."""
    try:
        return asyncio.run(handler_async(event, context))
    except Exception as e:
        log(f"💥 КРИТИЧЕСКАЯ ОШИБКА в handler: {e}")
        log(traceback.format_exc())
        # Возвращаем 200, чтобы Notion не отключил вебхук
        return {'statusCode': 200, 'body': f'Critical error: {e}'}
