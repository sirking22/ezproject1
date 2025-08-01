#!/usr/bin/env python3
"""
Создание материала из LightShot с обложкой (РАБОЧАЯ ВЕРСИЯ)
Использует проверенный код из test_covers_working_final.py
"""
import asyncio
import aiohttp
import os
import re
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
MATERIALS_DB = os.getenv("MATERIALS_DB")

LIGHTSHOT_URL = "https://prnt.sc/Gk-idc6SARl7"

def log(message: str, level: str = "INFO"):
    """Логирование с временной меткой"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

async def get_lightshot_image(lightshot_url: str) -> str:
    """Получает изображение из LightShot (РАБОЧАЯ ВЕРСИЯ)"""
    log(f"🔍 Получаю LightShot страницу: {lightshot_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(lightshot_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            log(f"📊 Статус LightShot: {response.status}")
            
            if response.status == 200:
                html = await response.text()
                log(f"📄 Размер HTML: {len(html)} символов")
                
                # Ищем прямую ссылку на изображение
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
                        log(f"✅ Найдено изображение LightShot: {image_url}")
                        return image_url
                
                # Если не нашли, попробуем извлечь из мета-тегов
                meta_pattern = r'<meta property="og:image" content="([^"]+)"'
                meta_matches = re.findall(meta_pattern, html)
                if meta_matches:
                    image_url = meta_matches[0]
                    log(f"✅ Найдено изображение в meta: {image_url}")
                    return image_url
                
                raise Exception("Не найдена прямая ссылка на изображение в LightShot")
            else:
                raise Exception(f"Ошибка получения LightShot страницы: {response.status}")

async def upload_to_yadisk_and_get_permanent_url(image_url: str, filename: str) -> tuple:
    """Загружает изображение на Яндекс.Диск и получает постоянную ссылку"""
    log(f"📥 Скачиваю изображение: {image_url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                raise Exception(f"Ошибка скачивания изображения: {response.status}")
            
            image_data = await response.read()
            log(f"✅ Изображение скачано: {len(image_data)} байт")
            
            # Загружаем на Яндекс.Диск
            headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
            
            # Создаем уникальное имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_suffix = random.randint(1000, 9999)
            safe_filename = f"{filename}_{timestamp}_{random_suffix}.jpg"
            remote_path = f"/notion_covers/{safe_filename}"
            
            log(f"📤 Загружаю на Яндекс.Диск: {remote_path}")
            
            # Получаем URL для загрузки
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            params = {
                "path": remote_path,
                "overwrite": "true"
            }
            
            async with session.get(upload_url, headers=headers, params=params) as upload_response:
                if upload_response.status != 200:
                    error_text = await upload_response.text()
                    raise Exception(f"Ошибка получения URL загрузки: {upload_response.status} - {error_text}")
                
                upload_data = await upload_response.json()
                href = upload_data.get("href")
                
                if not href:
                    raise Exception("Не получен href для загрузки")
                
                # Загружаем файл
                async with session.put(href, data=image_data) as put_response:
                    if put_response.status not in [201, 202, 200]:
                        error_text = await put_response.text()
                        raise Exception(f"Ошибка загрузки файла: {put_response.status} - {error_text}")
                
                log(f"✅ Файл загружен на Яндекс.Диск")
                
                # Получаем постоянную ссылку через download API
                download_url = "https://cloud-api.yandex.net/v1/disk/resources/download"
                download_params = {"path": remote_path}
                
                async with session.get(download_url, headers=headers, params=download_params) as download_response:
                    if download_response.status != 200:
                        error_text = await download_response.text()
                        raise Exception(f"Ошибка получения download ссылки: {download_response.status} - {error_text}")
                    
                    download_data = await download_response.json()
                    permanent_url = download_data.get("href")
                    
                    if not permanent_url:
                        raise Exception("Не получена постоянная ссылка")
                    
                    log(f"✅ Получена постоянная ссылка: {permanent_url[:80]}...")
                    return permanent_url, remote_path

async def create_notion_material(title: str, cover_url: str, original_url: str) -> tuple:
    """Создает материал в Notion с обложкой"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Создаем материал БЕЗ обложки сначала
    material_data = {
        "parent": {"database_id": MATERIALS_DB},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "URL": {"url": original_url}
        }
    }
    
    async with aiohttp.ClientSession() as session:
        log(f"📄 Создаю материал в Notion...")
        async with session.post("https://api.notion.com/v1/pages", headers=headers, json=material_data) as resp:
            data = await resp.json()
            page_id = data.get("id")
            if not page_id:
                raise Exception(f"Ошибка создания материала: {data}")
        
        # Добавляем обложку отдельным запросом
        log(f"🖼️ Добавляю обложку в Notion...")
        cover_data = {
            "cover": {
                "type": "external",
                "external": {"url": cover_url}
            }
        }
        
        async with session.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=cover_data) as resp:
            patch_data = await resp.json()
            if resp.status != 200:
                raise Exception(f"Ошибка добавления обложки: {patch_data}")
            
            return data.get("url"), cover_url

async def main():
    try:
        # Получаем изображение из LightShot
        lightshot_image_url = await get_lightshot_image(LIGHTSHOT_URL)
        
        # Загружаем на Яндекс.Диск и получаем постоянную ссылку
        download_url, remote_path = await upload_to_yadisk_and_get_permanent_url(lightshot_image_url, "lightshot_screenshot")
        
        # Создаем материал в Notion с обложкой
        notion_url, used_cover_url = await create_notion_material(
            title="LightShot Screenshot Test",
            cover_url=download_url,
            original_url=LIGHTSHOT_URL
        )
        
        print(f"\n✅ ГОТОВО!")
        print(f"📄 Ссылка на материал в Notion: {notion_url}")
        print(f"🖼️ Ссылка, добавленная в обложку: {used_cover_url}")
        print(f"💾 Файл на Яндекс.Диске: {remote_path}")
        print(f"🔗 Оригинальная LightShot ссылка: {LIGHTSHOT_URL}")
        
        # Проверяем, что ссылка долговечная
        if "downloader.disk.yandex.ru" in used_cover_url:
            print(f"✅ Ссылка ДОЛГОВЕЧНАЯ (через download API)")
        else:
            print(f"⚠️ Ссылка может быть временной")
            
    except Exception as e:
        log(f"❌ ОШИБКА: {e}", "ERROR")
        if 'download_url' in locals():
            print(f"🔗 Ссылка, которую пытались добавить: {download_url}")
        if 'remote_path' in locals():
            print(f"💾 Файл на Яндекс.Диске: {remote_path}")

if __name__ == "__main__":
    asyncio.run(main()) 