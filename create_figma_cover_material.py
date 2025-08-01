#!/usr/bin/env python3
"""
Создание материала в Notion с обложкой из Figma (download API Яндекс.Диск)
"""
import asyncio
import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")
MATERIALS_DB = os.getenv("MATERIALS_DB")

FIGMA_URL = "https://www.figma.com/design/4zI8UT7UATdc0jSPiuI86d/%D0%91%D1%80%D0%B5%D0%BD%D0%B4-%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B8?node-id=6902-924&t=HqZj4HKdVBJY6Sx5-1"

async def get_figma_preview(figma_url: str, session: aiohttp.ClientSession) -> str:
    # Извлекаем file_key и node_id
    if "/design/" in figma_url:
        file_key = figma_url.split("/design/")[1].split("/")[0]
    elif "/file/" in figma_url:
        file_key = figma_url.split("/file/")[1].split("/")[0]
    else:
        raise Exception("Не удалось извлечь file_key из Figma URL")
    node_id = None
    if "node-id=" in figma_url:
        node_id = figma_url.split("node-id=")[1].split("&")[0]
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    if node_id:
        images_url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&format=png&scale=2"
    else:
        images_url = f"https://api.figma.com/v1/images/{file_key}?format=png&scale=2"
    async with session.get(images_url, headers=headers) as response:
        data = await response.json()
        images = data.get("images", {})
        # node_id в API может быть с ":" вместо "-"
        key = node_id.replace("-", ":") if node_id else None
        image_url = images.get(key) or (list(images.values())[0] if images else None)
        if not image_url:
            raise Exception(f"Figma не вернула превью: {data}")
        return image_url

async def upload_to_yadisk_and_get_download_url(image_url: str, filename: str) -> str:
    async with aiohttp.ClientSession() as session:
        # Скачиваем изображение
        async with session.get(image_url) as response:
            image_data = await response.read()
        # Загружаем на Яндекс.Диск
        headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_path = f"/notion_covers/{timestamp}_{filename}.png"
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": remote_path, "overwrite": "true"}
        async with session.get(upload_url, headers=headers, params=params) as resp:
            href = (await resp.json())["href"]
        async with session.put(href, data=image_data) as resp:
            assert resp.status in (201, 202, 200)
        # Получаем download-ссылку
        download_url = "https://cloud-api.yandex.net/v1/disk/resources/download"
        params = {"path": remote_path}
        async with session.get(download_url, headers=headers, params=params) as resp:
            download_data = await resp.json()
            url = download_data.get("href")
            if not url:
                raise Exception(f"Не удалось получить download-ссылку: {download_data}")
            return url, remote_path

async def create_notion_material(title: str, cover_url: str, original_url: str) -> str:
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    material_data = {
        "parent": {"database_id": MATERIALS_DB},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "URL": {"url": original_url}
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.notion.com/v1/pages", headers=headers, json=material_data) as resp:
            data = await resp.json()
            page_id = data.get("id")
            if not page_id:
                raise Exception(f"Ошибка создания материала: {data}")
        # Добавляем обложку
        cover_data = {"cover": {"type": "external", "external": {"url": cover_url}}}
        async with session.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=cover_data) as resp:
            patch_data = await resp.json()
            if resp.status != 200:
                raise Exception(f"Ошибка добавления обложки: {patch_data}")
            return data.get("url"), cover_url

async def main():
    async with aiohttp.ClientSession() as session:
        print("[1] Получаю превью Figma...")
        figma_image_url = await get_figma_preview(FIGMA_URL, session)
        print(f"[2] Загружаю на Яндекс.Диск: {figma_image_url}")
        download_url, remote_path = await upload_to_yadisk_and_get_download_url(figma_image_url, "figma_preview")
        print(f"[3] Download-ссылка: {download_url}")
        print(f"[4] Создаю материал в Notion...")
        try:
            notion_url, used_cover_url = await create_notion_material(
                title="Figma Cover Test",
                cover_url=download_url,
                original_url=FIGMA_URL
            )
            print(f"[5] ГОТОВО! Ссылка на материал: {notion_url}")
            print(f"[6] Ссылка, добавленная в обложку: {used_cover_url}")
            print(f"[7] Файл на Яндекс.Диске: {remote_path}")
        except Exception as e:
            print(f"[ERROR] {e}")
            print(f"[6] Ссылка, которую пытались добавить в обложку: {download_url}")
            print(f"[7] Файл на Яндекс.Диске: {remote_path}")

if __name__ == "__main__":
    asyncio.run(main())