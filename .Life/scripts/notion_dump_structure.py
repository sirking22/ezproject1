import os
import asyncio
import logging
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'yearly_goals': os.getenv('NOTION_DATABASE_ID_YEARLY_GOALS'),
    'genius_list': os.getenv('NOTION_DATABASE_ID_GENIUS_LIST'),
    'journal': os.getenv('NOTION_DATABASE_ID_JOURNAL'),
    'rituals': os.getenv('NOTION_DATABASE_ID_RITUALS'),
    'habits': os.getenv('NOTION_DATABASE_ID_HABITS'),
    'reflection': os.getenv('NOTION_DATABASE_ID_REFLECTION'),
    'guides': os.getenv('NOTION_DATABASE_ID_GUIDES'),
    'tasks': os.getenv('NOTION_TASKS_DB'),
    'terms': os.getenv('NOTION_DATABASE_ID_TERMS'),
    'materials': os.getenv('NOTION_DATABASE_ID_MATERIALS'),
    'agent_prompts': os.getenv('NOTION_DATABASE_ID_AGENT_PROMPTS'),
    'ideas': os.getenv('NOTION_DATABASE_ID_IDEAS'),
    'experience_hub': os.getenv('NOTION_DATABASE_ID_EXPERIENCE_HUB'),
}

NOTION_TOKEN = os.getenv('NOTION_TOKEN')

async def dump_notion_schemas():
    if not NOTION_TOKEN:
        print("NOTION_TOKEN не найден в env!")
        return
    client = AsyncClient(auth=NOTION_TOKEN)
    dump_lines = ["# Notion Database Schema Dump\n"]
    for db_key, db_id in DATABASES.items():
        if not db_id:
            dump_lines.append(f"## {db_key}\nID не найден в env\n")
            continue
        try:
            db_meta = await client.databases.retrieve(database_id=db_id)
            title = db_meta['title'][0]['plain_text'] if db_meta['title'] else db_key
            dump_lines.append(f"## {db_key} ({title})\nID: {db_id}\n")
            dump_lines.append("| Property | Type |\n|---|---|\n")
            for prop, val in db_meta['properties'].items():
                dump_lines.append(f"| {prop} | {val['type']} |\n")
            dump_lines.append("\n")
        except Exception as e:
            dump_lines.append(f"## {db_key}\nОшибка: {e}\n")
    with open("docs/NOTION_SCHEMA_DUMP.md", "w", encoding="utf-8") as f:
        f.writelines(dump_lines)
    print("Схемы всех баз сохранены в docs/NOTION_SCHEMA_DUMP.md")

async def dump_notion_entries():
    if not NOTION_TOKEN:
        print("NOTION_TOKEN не найден в env!")
        return
    client = AsyncClient(auth=NOTION_TOKEN)
    entries_lines = ["# Notion Habits & Rituals Entries\n"]
    for db_key in ["habits", "rituals"]:
        db_id = DATABASES.get(db_key)
        if not db_id:
            entries_lines.append(f"## {db_key}\nID не найден в env\n")
            continue
        try:
            entries_lines.append(f"## {db_key}\n")
            query = {"database_id": db_id}
            response = await client.databases.query(**query)
            results = response.get("results", [])
            for page in results:
                props = page.get("properties", {})
                # Формируем краткое описание привычки/ритуала
                summary = []
                for k, v in props.items():
                    val = v.get(v["type"], None)
                    if isinstance(val, list):
                        val = ", ".join([i.get("plain_text", str(i)) for i in val if isinstance(i, dict)])
                    elif isinstance(val, dict) and "name" in val:
                        val = val["name"]
                    summary.append(f"{k}: {val}")
                entries_lines.append("; ".join(summary) + "\n")
            entries_lines.append("\n")
        except Exception as e:
            entries_lines.append(f"Ошибка: {e}\n")
    with open("docs/HABITS_RITUALS_ENTRIES.md", "w", encoding="utf-8") as f:
        f.writelines(entries_lines)
    print("Содержимое привычек и ритуалов сохранено в docs/HABITS_RITUALS_ENTRIES.md")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "entries":
        asyncio.run(dump_notion_entries())
    else:
        asyncio.run(dump_notion_schemas()) 