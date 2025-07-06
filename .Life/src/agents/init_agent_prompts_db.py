import os
from dotenv import load_dotenv
import asyncio
from notion_client import AsyncClient

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
AGENT_PROMPTS_DB = os.getenv("NOTION_DATABASE_ID_AGENT_PROMPTS")

async def init_agent_prompts_db():
    """Инициализирует базу agent_prompts с правильной структурой"""
    client = AsyncClient(auth=NOTION_TOKEN)
    
    try:
        print("Инициализация базы agent_prompts...")
        
        # Создаём тестовую запись для проверки структуры
        test_page = await client.pages.create(
            parent={"database_id": AGENT_PROMPTS_DB},
            properties={
                "Название": {"title": [{"text": {"content": "Тестовый промпт"}}]},
                "Роль": {"select": {"name": "Test"}},
                "Промпт": {"rich_text": [{"text": {"content": "Тестовый промпт для проверки структуры"}}]},
                "Миссия": {"rich_text": [{"text": {"content": "Тестовая миссия"}}]},
                "Статус": {"select": {"name": "Активный"}},
                "Версия": {"number": 1}
            }
        )
        
        print("✓ Тестовая запись создана")
        
        # Получаем структуру базы
        db = await client.databases.retrieve(database_id=AGENT_PROMPTS_DB)
        print(f"\nСтруктура базы '{db['title'][0]['plain_text']}':")
        
        for prop_name, prop_data in db['properties'].items():
            print(f"  - {prop_name}: {prop_data['type']}")
            if prop_data['type'] == 'select' and 'options' in prop_data:
                print(f"    Варианты: {[opt['name'] for opt in prop_data['options']]}")
        
        # Удаляем тестовую запись
        await client.pages.update(page_id=test_page["id"], archived=True)
        print("\n✓ Тестовая запись удалена")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await init_agent_prompts_db()

if __name__ == "__main__":
    asyncio.run(main()) 