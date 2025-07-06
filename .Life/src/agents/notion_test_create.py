import os
from dotenv import load_dotenv
import asyncio
from notion_client import AsyncClient

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DBS = {
    "rituals": os.getenv("NOTION_DATABASE_ID_RITUALS"),
    "habits": os.getenv("NOTION_DATABASE_ID_HABITS"),
    "materials": os.getenv("NOTION_DATABASE_ID_MATERIALS"),
    "guides": os.getenv("NOTION_DATABASE_ID_GUIDES"),
    "actions": os.getenv("NOTION_DATABASE_ID_ACTIONS"),
}

async def test_create():
    client = AsyncClient(auth=NOTION_TOKEN)
    for name, dbid in DBS.items():
        print(f"\nТестируем базу: {name} (id: {dbid})")
        try:
            page = await client.pages.create(
                parent={"database_id": dbid},
                properties={
                    "Name": {"title": [{"text": {"content": f"Тестовая страница для {name}"}}]},
                    "Category": {"select": {"name": "Тест"}},
                }
            )
            print(f"Успешно создано: {page['id']}")
        except Exception as e:
            print(f"Ошибка при создании в базе {name}: {e}")

if __name__ == "__main__":
    print("NOTION_TOKEN:", NOTION_TOKEN[:12] if NOTION_TOKEN else None)
    for k, v in DBS.items():
        print(f"{k}: {v}")
    asyncio.run(test_create()) 