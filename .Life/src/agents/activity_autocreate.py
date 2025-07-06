import os
import sys
from dotenv import load_dotenv
import asyncio
from notion_client import AsyncClient
import traceback

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.activity_templates import ACTIVITY_TEMPLATES

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DBS = {
    "rituals": os.getenv("NOTION_DATABASE_ID_RITUALS"),
    "habits": os.getenv("NOTION_DATABASE_ID_HABITS"),
    "materials": os.getenv("NOTION_DATABASE_ID_MATERIALS"),
    "guides": os.getenv("NOTION_DATABASE_ID_GUIDES"),
    "actions": os.getenv("NOTION_DATABASE_ID_ACTIONS"),
}

# Исправленные имена полей в соответствии с реальной структурой
DB_FIELDS = {
    "rituals": ("Название", "Категория"),
    "habits": ("Привычка", None),
    "materials": ("Название", "Категория"),
    "guides": ("Name", None),
    "actions": ("Задача", "Категория"),
}

async def check_if_exists(client: AsyncClient, database_id: str, title_field: str, title_content: str) -> bool:
    """Проверяет, существует ли запись с таким названием в базе"""
    try:
        response = await client.databases.query(
            database_id=database_id,
            filter={
                "property": title_field,
                "title": {
                    "equals": title_content
                }
            }
        )
        return len(response["results"]) > 0
    except Exception:
        return False

async def create_activity_in_notion(activity: dict, client: AsyncClient):
    print(f"  Создаю активность: {activity['activity']}")
    
    # rituals
    ritual_title = activity["ritual"]
    if not await check_if_exists(client, DBS["rituals"], DB_FIELDS["rituals"][0], ritual_title):
        await client.pages.create(parent={"database_id": DBS["rituals"]}, properties={
            DB_FIELDS["rituals"][0]: {"title": [{"text": {"content": ritual_title}}]},
            DB_FIELDS["rituals"][1]: {"select": {"name": activity["activity"]}} if DB_FIELDS["rituals"][1] else {},
        })
        print(f"    ✅ Ритуал создан: {ritual_title}")
    else:
        print(f"    ⚠ Ритуал '{ritual_title}' уже существует")
    
    # habits
    habit_title = activity["habit"]
    if not await check_if_exists(client, DBS["habits"], DB_FIELDS["habits"][0], habit_title):
        await client.pages.create(parent={"database_id": DBS["habits"]}, properties={
            DB_FIELDS["habits"][0]: {"title": [{"text": {"content": habit_title}}]},
        })
        print(f"    ✅ Привычка создана: {habit_title}")
    else:
        print(f"    ⚠ Привычка '{habit_title}' уже существует")
    
    # materials
    material_title = f"{activity['activity']} — {activity['material']['type']} шаблон"
    if not await check_if_exists(client, DBS["materials"], DB_FIELDS["materials"][0], material_title):
        await client.pages.create(parent={"database_id": DBS["materials"]}, properties={
            DB_FIELDS["materials"][0]: {"title": [{"text": {"content": material_title}}]},
            DB_FIELDS["materials"][1]: {"select": {"name": activity["activity"]}} if DB_FIELDS["materials"][1] else {},
        })
        print(f"    ✅ Материал создан: {material_title}")
    else:
        print(f"    ⚠ Материал '{material_title}' уже существует")
    
    # guides
    guide_title = activity["guide"]
    if not await check_if_exists(client, DBS["guides"], DB_FIELDS["guides"][0], guide_title):
        await client.pages.create(parent={"database_id": DBS["guides"]}, properties={
            DB_FIELDS["guides"][0]: {"title": [{"text": {"content": guide_title}}]},
        })
        print(f"    ✅ Гайд создан: {guide_title}")
    else:
        print(f"    ⚠ Гайд '{guide_title}' уже существует")
    
    # actions
    action_title = activity["action"]
    if not await check_if_exists(client, DBS["actions"], DB_FIELDS["actions"][0], action_title):
        await client.pages.create(parent={"database_id": DBS["actions"]}, properties={
            DB_FIELDS["actions"][0]: {"title": [{"text": {"content": action_title}}]},
            DB_FIELDS["actions"][1]: {"select": {"name": activity["activity"]}} if DB_FIELDS["actions"][1] else {},
        })
        print(f"    ✅ Задача создана: {action_title}")
    else:
        print(f"    ⚠ Задача '{action_title}' уже существует")

async def main():
    client = AsyncClient(auth=NOTION_TOKEN)
    print(f"🚀 Массовое создание активностей в Notion")
    print(f"📊 Всего активностей для создания: {len(ACTIVITY_TEMPLATES)}")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for i, activity in enumerate(ACTIVITY_TEMPLATES, 1):
        print(f"\n[{i}/{len(ACTIVITY_TEMPLATES)}] Создаю активность: {activity['activity']}")
        try:
            await create_activity_in_notion(activity, client)
            success_count += 1
            print(f"✅ Активность '{activity['activity']}' создана во всех базах Notion!")
        except Exception as e:
            error_count += 1
            tb = traceback.format_exc()
            print(f"❌ Ошибка при создании активности '{activity['activity']}': {e}")
            print(tb)
            with open("errors.log", "a", encoding="utf-8") as f:
                f.write(f"[{activity['activity']}]: {e}\n{tb}\n---\n")
    
    print("\n" + "=" * 60)
    print(f"📈 РЕЗУЛЬТАТЫ:")
    print(f"   ✅ Успешно создано: {success_count}")
    print(f"   ❌ Ошибок: {error_count}")
    print(f"   📊 Всего: {len(ACTIVITY_TEMPLATES)}")
    print("🎉 Завершено!")

if __name__ == "__main__":
    asyncio.run(main()) 