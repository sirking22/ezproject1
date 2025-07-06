import os
from dotenv import load_dotenv
import asyncio
from notion_client import AsyncClient

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
AGENT_PROMPTS_DB = os.getenv("NOTION_DATABASE_ID_AGENT_PROMPTS")

async def add_fields_to_agent_prompts_db():
    client = AsyncClient(auth=NOTION_TOKEN)
    try:
        print("Добавляю поля в базу agent_prompts...")
        await client.databases.update(
            database_id=AGENT_PROMPTS_DB,
            properties={
                "Роль": {
                    "select": {
                        "options": [
                            {"name": "Product Manager", "color": "blue"},
                            {"name": "Developer", "color": "green"},
                            {"name": "LLM Researcher", "color": "purple"},
                            {"name": "DevOps", "color": "orange"},
                            {"name": "QA", "color": "red"},
                            {"name": "Support", "color": "yellow"},
                            {"name": "Growth/Marketing", "color": "pink"},
                            {"name": "Meta-Agent", "color": "gray"}
                        ]
                    }
                },
                "Промпт": {"rich_text": {}},
                "Миссия": {"rich_text": {}},
                "Статус": {
                    "select": {
                        "options": [
                            {"name": "Активный", "color": "green"},
                            {"name": "Черновик", "color": "yellow"},
                            {"name": "Архив", "color": "gray"}
                        ]
                    }
                },
                "Версия": {"number": {"format": "number"}},
                "Дата создания": {"date": {}},
                "Последнее обновление": {"date": {}}
            }
        )
        print("✓ Все поля добавлены!")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await add_fields_to_agent_prompts_db()

if __name__ == "__main__":
    asyncio.run(main()) 