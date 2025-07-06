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

DB_FIELDS = {
    "rituals": ("Название", "Категория"),
    "habits": ("Привычка", None),
    "materials": ("Название", "Категория"),
    "guides": ("Name", None),
    "actions": ("Задача", "Категория"),
}

async def clean_duplicates():
    """Удаляет дубликаты из всех баз"""
    client = AsyncClient(auth=NOTION_TOKEN)
    
    for db_name, db_id in DBS.items():
        print(f"\n=== Очистка дубликатов в {db_name.upper()} ===")
        title_field = DB_FIELDS[db_name][0]
        
        try:
            # Получаем все записи
            response = await client.databases.query(database_id=db_id)
            pages = response["results"]
            
            # Группируем по названию
            titles = {}
            for page in pages:
                title_prop = page["properties"].get(title_field, {})
                if title_prop.get("type") == "title" and title_prop["title"]:
                    title = title_prop["title"][0]["plain_text"]
                    if title not in titles:
                        titles[title] = []
                    titles[title].append(page["id"])
            
            # Удаляем дубликаты (оставляем первый)
            deleted_count = 0
            for title, page_ids in titles.items():
                if len(page_ids) > 1:
                    print(f"  Найдено {len(page_ids)} дубликатов для '{title}'")
                    # Удаляем все кроме первого
                    for page_id in page_ids[1:]:
                        try:
                            await client.pages.update(page_id=page_id, archived=True)
                            deleted_count += 1
                            print(f"    Удалён дубликат: {page_id}")
                        except Exception as e:
                            print(f"    Ошибка удаления {page_id}: {e}")
            
            print(f"  Удалено дубликатов: {deleted_count}")
            
        except Exception as e:
            print(f"  Ошибка при очистке {db_name}: {e}")

async def main():
    print("Начинаю очистку дубликатов...")
    await clean_duplicates()
    print("\nОчистка завершена!")

if __name__ == "__main__":
    asyncio.run(main()) 