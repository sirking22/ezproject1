import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

HABITS_DB = os.getenv('NOTION_DATABASE_ID_HABITS')
RITUALS_DB = os.getenv('NOTION_DATABASE_ID_RITUALS')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')

async def remove_nutrition_habits_and_rituals():
    if not NOTION_TOKEN or not HABITS_DB or not RITUALS_DB:
        print('NOTION_TOKEN или базы не найдены!')
        return
    
    client = AsyncClient(auth=NOTION_TOKEN)
    
    # 1. Удаляем привычки с питанием
    print("=== Удаление привычек с питанием ===")
    response = await client.databases.query(database_id=HABITS_DB)
    habits = response.get('results', [])
    
    nutrition_habits_removed = 0
    for habit in habits:
        name = habit['properties'].get('Привычка', {}).get('title', [])
        if name:
            title = name[0]['plain_text']
            if 'питание' in title.lower() or 'масса' in title.lower():
                await client.pages.update(page_id=habit['id'], archived=True)
                print(f"🗑️  Удалена привычка: {title}")
                nutrition_habits_removed += 1
    
    # 2. Удаляем ритуалы с питанием
    print("\n=== Удаление ритуалов с питанием ===")
    response = await client.databases.query(database_id=RITUALS_DB)
    rituals = response.get('results', [])
    
    nutrition_rituals_removed = 0
    for ritual in rituals:
        name = ritual['properties'].get('Название', {}).get('title', [])
        if name:
            title = name[0]['plain_text']
            if 'питание' in title.lower() or 'масса' in title.lower():
                await client.pages.update(page_id=ritual['id'], archived=True)
                print(f"🗑️  Удалён ритуал: {title}")
                nutrition_rituals_removed += 1
    
    print(f"\n=== Удаление завершено ===")
    print(f"Удалено привычек: {nutrition_habits_removed}")
    print(f"Удалено ритуалов: {nutrition_rituals_removed}")

if __name__ == '__main__':
    asyncio.run(remove_nutrition_habits_and_rituals()) 