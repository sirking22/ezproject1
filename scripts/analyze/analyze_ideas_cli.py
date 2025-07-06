import os
import asyncio
from datetime import datetime, timezone
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
IDEAS_DB_ID = os.getenv("NOTION_IDEAS_DB_ID") or "ad92a6e21485428c84de8587706b3be1"
FRESHNESS_DAYS = 14

async def analyze_ideas():
    client = AsyncClient(auth=NOTION_TOKEN)
    database_id = IDEAS_DB_ID
    freshness_days = FRESHNESS_DAYS
    print(f"[CLI] Анализ базы идей: {database_id}", flush=True)
    pages = []
    next_cursor = None
    batch_num = 0
    while True:
        kwargs = dict(database_id=database_id, page_size=100)
        if next_cursor:
            kwargs["start_cursor"] = next_cursor
        response = await client.databases.query(**kwargs)
        batch = response.get("results", [])
        pages.extend(batch)
        batch_num += 1
        print(f"[CLI] Загрузка: {len(pages)} страниц (батч {batch_num})...", flush=True)
        if not response.get("has_more"):
            break
        next_cursor = response.get("next_cursor")
    now = datetime.now(timezone.utc)
    total = len(pages)
    filled = 0
    fresh = 0
    orphans = 0
    dups = 0
    seen_titles = set()
    tag_counter = {}
    status_counter = {}
    category_counter = {}
    for idx, page in enumerate(pages, 1):
        try:
            props = page.get("properties", {})
            title = ""
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "title":
                    title = "".join([t.get("plain_text", "") for t in v.get("title", []) if isinstance(t, dict)])
                    break
            desc = ""
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "rich_text":
                    desc = "".join([t.get("plain_text", "") for t in v.get("rich_text", []) if isinstance(t, dict)])
                    break
            if title and desc:
                filled += 1
            last_edited = page.get("last_edited_time")
            if last_edited:
                try:
                    dt = datetime.fromisoformat(last_edited.replace("Z", "+00:00")).astimezone(timezone.utc)
                    if (now - dt).days <= freshness_days:
                        fresh += 1
                except Exception:
                    pass
            tags = []
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "multi_select":
                    tags = v.get("multi_select", [])
                    for tag in tags:
                        if isinstance(tag, dict):
                            tag_name = tag.get("name")
                            if tag_name:
                                tag_counter[tag_name] = tag_counter.get(tag_name, 0) + 1
                    break
            status = None
            for k, v in props.items():
                if isinstance(v, dict) and v.get("type") == "select":
                    status_val = v.get("select", {})
                    if isinstance(status_val, dict):
                        status = status_val.get("name")
                        if status:
                            status_counter[status] = status_counter.get(status, 0) + 1
                    break
            for k, v in props.items():
                if (
                    isinstance(v, dict)
                    and k.lower() in ("category", "категория", "direction", "topic", "area", "направление")
                    and v.get("type") in ("select", "multi_select")
                ):
                    vals = []
                    if v.get("type") == "select":
                        val = v.get("select", {})
                        if isinstance(val, dict):
                            name = val.get("name")
                            if name:
                                vals = [name]
                    else:
                        vals = [x.get("name") for x in v.get("multi_select", []) if isinstance(x, dict) and x.get("name")]
                    for cat in vals:
                        category_counter[cat] = category_counter.get(cat, 0) + 1
            if not tags and not status:
                orphans += 1
            if title in seen_titles:
                dups += 1
            else:
                seen_titles.add(title)
            if idx % 200 == 0:
                print(f"[CLI] Анализировано {idx} страниц из {total}...", flush=True)
        except Exception as e:
            print(f"[CLI] Ошибка на странице {idx}: {e}", flush=True)
    def top_n(counter, n=5):
        return sorted(counter.items(), key=lambda x: -x[1])[:n]
    print("\n# 📊 Аналитика базы идей", flush=True)
    print(f"- Всего записей: {total}", flush=True)
    print(f"- Заполнено (title+desc): {filled} ({round(100*filled/total,1) if total else 0}%)", flush=True)
    print(f"- Свежих (изм. < {freshness_days}д): {fresh} ({round(100*fresh/total,1) if total else 0}%)", flush=True)
    print(f"- Orphan (нет тегов/статуса): {orphans} ({round(100*orphans/total,1) if total else 0}%)", flush=True)
    print(f"- Дубли по title: {dups} ({round(100*dups/total,1) if total else 0}%)", flush=True)
    print(f"- Топ теги: {top_n(tag_counter)}", flush=True)
    print(f"- Топ статусы: {top_n(status_counter)}", flush=True)
    print(f"- Топ категории/направления: {top_n(category_counter)}", flush=True)

if __name__ == "__main__":
    asyncio.run(analyze_ideas()) 