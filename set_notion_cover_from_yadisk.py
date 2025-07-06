import asyncio
from services.media_cover_manager import MediaCoverManager
from app.core.notion_client import NotionManager
import os

# Реальный путь к jpg-файлу на Яндекс.Диске
YADISK_PATH = '/TelegramImport_20250621_025209/group_20240125_031952/photo_1192@25-01-2024_03-19-52.jpg'

async def main():
    # 1. Создаем новую идею
    notion = NotionManager()
    page = await notion.create_page({
        "database_id": os.getenv("NOTION_IDEAS_DB_ID"),
        "title": "Тестовая идея с обложкой из Яндекс.Диска",
        "description": "Проверка установки cover через raw-картинку Яндекс.Диска",
        "tags": ["cover-test"],
        "importance": 3,
        "status": "To do"
    })
    print(f'Создана страница: {page.id}')

    # 2. Ставим обложку из Яндекс.Диска
    manager = MediaCoverManager()
    await manager.apply_cover_from_yadisk_path(page.id, YADISK_PATH)
    print(f'https://www.notion.so/{page.id.replace("-","")}')

if __name__ == "__main__":
    asyncio.run(main()) 