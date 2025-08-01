#!/usr/bin/env python3
"""
Создание материала из одной ссылки с Files & media
Использует правильную структуру из universal_materials_bot.py
"""

import asyncio
import aiohttp
import os
import re
import random
from datetime import datetime
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
MATERIALS_DB = os.getenv("MATERIALS_DB")

def log(message: str, level: str = "INFO"):
    """Логирование с временной меткой"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

async def get_image_from_url(url: str) -> Optional[str]:
    """Получает изображение из разных типов ссылок"""
    log(f"🔍 Анализирую URL: {url}")
    
    # Определяем тип URL
    if "figma.com" in url:
        return await get_figma_image(url)
    elif "prnt.sc" in url or "lightshot.cc" in url:
        return await get_lightshot_image(url)
    elif "yadi.sk" in url or "disk.yandex.ru" in url:
        return await get_yandex_disk_image(url)
    elif any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
        return url  # Прямая ссылка на изображение
    else:
        log(f"❌ Неизвестный тип URL: {url}", "ERROR")
        return None

async def get_figma_image(figma_url: str) -> Optional[str]:
    """Получает изображение из Figma"""
    try:
        log(f"🎨 Получаю Figma изображение: {figma_url}")
        
        # Извлекаем file key
        if "/design/" in figma_url:
            file_key = figma_url.split("/design/")[1].split("/")[0]
        elif "/file/" in figma_url:
            file_key = figma_url.split("/file/")[1].split("/")[0]
        else:
            log("❌ Не удалось извлечь file_key из Figma URL", "ERROR")
            return None
        
        # Извлекаем node id
        node_id = None
        if "node-id=" in figma_url:
            node_id = figma_url.split("node-id=")[1].split("&")[0]
        
        # Получаем изображение через Figma API
        figma_token = os.getenv("FIGMA_TOKEN")
        headers = {"X-Figma-Token": figma_token} if figma_token else {}
        
        if node_id:
            images_url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format=png&scale=2"
        else:
            images_url = f"https://api.figma.com/v1/images/{file_key}?format=png&scale=2"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(images_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    images = data.get("images", {})
                    
                    if node_id:
                        # Ищем изображение с правильным node_id
                        image_url = None
                        for key, url in images.items():
                            if key == node_id or key == node_id.replace("-", ":"):
                                image_url = url
                                break
                        if not image_url and images:
                            image_url = list(images.values())[0]
                    else:
                        image_url = list(images.values())[0] if images else None
                    
                    if image_url:
                        log(f"✅ Получено Figma изображение: {image_url[:60]}...")
                        return image_url
                else:
                    log(f"❌ Ошибка Figma API: {response.status}", "ERROR")
        
        return None
        
    except Exception as e:
        log(f"❌ Ошибка получения Figma изображения: {e}", "ERROR")
        return None

async def get_lightshot_image(lightshot_url: str) -> Optional[str]:
    """Получает изображение из LightShot"""
    try:
        log(f"📸 Получаю LightShot изображение: {lightshot_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(lightshot_url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Ищем изображение в HTML
                    patterns = [
                        r'https://image\.prntscr\.com/image/[^"\']+',
                        r'https://[^"\']*\.png',
                        r'https://[^"\']*\.jpg',
                        r'https://[^"\']*\.jpeg',
                        r'https://[^"\']*\.webp'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, html)
                        if matches:
                            image_url = matches[0]
                            log(f"✅ Найдено LightShot изображение: {image_url}")
                            return image_url
                    
                    log("❌ Не найдено изображение в LightShot HTML", "ERROR")
                else:
                    log(f"❌ Ошибка получения LightShot HTML: {response.status}", "ERROR")
        
        return None
        
    except Exception as e:
        log(f"❌ Ошибка получения LightShot изображения: {e}", "ERROR")
        return None

async def get_yandex_disk_image(yandex_url: str) -> Optional[str]:
    """Получает изображение из Яндекс.Диск"""
    try:
        log(f"☁️ Получаю Яндекс.Диск изображение: {yandex_url}")
        
        # Извлекаем file_id из URL
        if "/i/" in yandex_url:
            file_id = yandex_url.split("/i/")[1]
        elif "/d/" in yandex_url:
            file_id = yandex_url.split("/d/")[1].split("/")[0]
        else:
            log("❌ Не удалось извлечь file_id из Яндекс.Диск URL", "ERROR")
            return None
        
        # Создаем прямую ссылку на изображение
        direct_url = f"https://disk.yandex.ru/i/{file_id}"
        log(f"✅ Создана прямая ссылка: {direct_url}")
        
        return direct_url
        
    except Exception as e:
        log(f"❌ Ошибка получения Яндекс.Диск изображения: {e}", "ERROR")
        return None

async def upload_to_yandex_disk_and_get_permanent_url(image_url: str, filename: str) -> Tuple[str, str, str]:
    """Загружает изображение на Яндекс.Диск и получает постоянную ссылку для обложки и предпросмотр для Files & media"""
    log(f"📥 Скачиваю изображение: {image_url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
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
            
            async with session.get(upload_url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ошибка получения URL загрузки: {response.status} - {error_text}")
                
                upload_data = await response.json()
                href = upload_data.get("href")
                
                if not href:
                    raise Exception("Не получен href для загрузки")
                
                # Загружаем файл
                async with session.put(href, data=image_data) as put_response:
                    if put_response.status != 201:
                        error_text = await put_response.text()
                        raise Exception(f"Ошибка загрузки файла: {put_response.status} - {error_text}")
                
                log(f"✅ Файл загружен на Яндекс.Диск")
                
                # Получаем прямую ссылку для обложки (через download API)
                download_url = "https://cloud-api.yandex.net/v1/disk/resources/download"
                download_params = {"path": remote_path}
                
                async with session.get(download_url, headers=headers, params=download_params) as download_response:
                    if download_response.status != 200:
                        error_text = await download_response.text()
                        raise Exception(f"Ошибка получения download ссылки: {download_response.status} - {error_text}")
                    
                    download_data = await download_response.json()
                    cover_url = download_data.get("href")
                    
                    if not cover_url:
                        raise Exception("Не получена ссылка для обложки")
                    
                    log(f"✅ Получена ссылка для обложки: {cover_url[:80]}...")
                
                # Публикуем файл для получения ссылки с предпросмотром для Files & media
                publish_url = f"https://cloud-api.yandex.net/v1/disk/resources/publish?path={remote_path}"
                async with session.put(publish_url, headers=headers) as publish_response:
                    if publish_response.status == 200:
                        publish_data = await publish_response.json()
                        if 'href' in publish_data:
                            # Получаем информацию о файле для получения public_url
                            file_info_url = publish_data['href']
                            async with session.get(file_info_url, headers=headers) as file_response:
                                if file_response.status == 200:
                                    file_info = await file_response.json()
                                    if 'public_url' in file_info:
                                        files_media_url = file_info['public_url']
                                        log(f"✅ Получена ссылка с предпросмотром для Files & media: {files_media_url}")
                                        return cover_url, files_media_url, remote_path
                
                # Fallback: используем ту же ссылку для обоих случаев
                log(f"⚠️ Использую fallback - ту же ссылку для обложки и Files & media")
                return cover_url, cover_url, remote_path

async def create_notion_material(title: str, cover_url: str, files_media_url: str, original_url: str) -> str:
    """Создает материал в Notion с обложкой и Files & media"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Создаем материал с Files & media и обложкой (правильная структура из universal_materials_bot.py)
    material_data = {
        "parent": {"database_id": MATERIALS_DB},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "URL": {"url": original_url},
            "Files & media": {
                "files": [{
                    "external": {"url": files_media_url},
                    "name": "Material File"
                }]
            }
        },
        "cover": {
            "type": "external",
            "external": {"url": cover_url}
        }
    }
    
    async with aiohttp.ClientSession() as session:
        log(f"📄 Создаю материал в Notion...")
        async with session.post("https://api.notion.com/v1/pages", headers=headers, json=material_data) as response:
            if response.status == 200:
                data = await response.json()
                page_url = data.get("url")
                log(f"✅ Материал создан в Notion: {page_url}")
                return page_url
            else:
                error_text = await response.text()
                raise Exception(f"Ошибка создания материала: {response.status} - {error_text}")

async def main():
    """Главная функция"""
    # Тестовая ссылка (можешь заменить на любую)
    test_url = "https://prnt.sc/Gk-idc6SARl7"
    
    try:
        log("🚀 НАЧАЛО СОЗДАНИЯ МАТЕРИАЛА")
        log("=" * 60)
        
        # Получаем изображение из ссылки
        image_url = await get_image_from_url(test_url)
        if not image_url:
            log("❌ Не удалось получить изображение из ссылки", "ERROR")
            return
        
        log(f"✅ Получено изображение: {image_url[:60]}...")
        
        # Загружаем на Яндекс.Диск и получаем ссылки для обложки и Files & media
        cover_url, files_media_url, remote_path = await upload_to_yandex_disk_and_get_permanent_url(image_url, "test_material")
        
        # Создаем материал в Notion
        title = "Тестовый материал из ссылки"
        notion_url = await create_notion_material(
            title=title,
            cover_url=cover_url,  # Обложка (прямая ссылка для скачивания)
            files_media_url=files_media_url,  # Files & media (ссылка с предпросмотром)
            original_url=test_url
        )
        
        print(f"\n🎉 МАТЕРИАЛ УСПЕШНО СОЗДАН!")
        print(f"📄 Ссылка на материал в Notion: {notion_url}")
        print(f"🖼️ Обложка (прямая ссылка): {cover_url[:80]}...")
        print(f"📎 Files & media (с предпросмотром): {files_media_url[:80]}...")
        print(f"💾 Файл на Яндекс.Диске: {remote_path}")
        print(f"🔗 Оригинальная ссылка: {test_url}")
        
        # Проверяем типы ссылок
        if "downloader.disk.yandex.ru" in cover_url:
            print(f"✅ Обложка: ДОЛГОВЕЧНАЯ (через download API)")
        else:
            print(f"⚠️ Обложка: может быть временной")
            
        if "yadi.sk" in files_media_url:
            print(f"✅ Files & media: С ПРЕДПРОСМОТРОМ (публичная ссылка)")
        else:
            print(f"⚠️ Files & media: может быть прямым скачиванием")
            
    except Exception as e:
        log(f"❌ ОШИБКА: {e}", "ERROR")

if __name__ == "__main__":
    asyncio.run(main()) 