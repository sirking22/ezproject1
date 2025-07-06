import os
from dotenv import load_dotenv
import asyncio
from notion_client import AsyncClient

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
AGENT_PROMPTS_DB = os.getenv("NOTION_DATABASE_ID_AGENT_PROMPTS")

async def check_agent_prompts_db():
    """Проверяет структуру базы agent_prompts"""
    client = AsyncClient(auth=NOTION_TOKEN)
    
    try:
        print("=== СТРУКТУРА БАЗЫ AGENT_PROMPTS ===")
        db = await client.databases.retrieve(database_id=AGENT_PROMPTS_DB)
        
        print(f"Название: {db['title'][0]['plain_text']}")
        print("Поля:")
        for prop_name, prop_data in db['properties'].items():
            print(f"  - {prop_name}: {prop_data['type']}")
            if prop_data['type'] == 'select' and 'options' in prop_data:
                print(f"    Варианты: {[opt['name'] for opt in prop_data['options']]}")
            if prop_data['type'] == 'title':
                print(f"    ⭐ Это поле-заголовок!")
        
        print(f"\n=== СУЩЕСТВУЮЩИЕ ЗАПИСИ ===")
        response = await client.databases.query(database_id=AGENT_PROMPTS_DB)
        print(f"Всего записей: {len(response['results'])}")
        
        for page in response['results']:
            props = page['properties']
            # Ищем поле-заголовок
            title_field = None
            for prop_name, prop_data in props.items():
                if prop_data.get('type') == 'title' and prop_data.get('title'):
                    title_field = prop_data['title'][0]['plain_text']
                    break
            print(f"  - {title_field or 'Без названия'}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await check_agent_prompts_db()

if __name__ == "__main__":
    asyncio.run(main()) 