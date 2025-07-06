import asyncio
import time
import os
from notion_mcp_server import NotionMCPServer

# Список баз (ID брать из env)
BASES = {
    'tasks': os.getenv('NOTION_TASKS_DB_ID'),
    'subtasks': os.getenv('NOTION_SUBTASKS_DB_ID'),
    'projects': os.getenv('NOTION_PROJECTS_DB_ID'),
    'ideas': os.getenv('NOTION_IDEAS_DB_ID'),
    'materials': os.getenv('NOTION_MATERIALS_DB_ID'),
    'kpi': os.getenv('NOTION_KPI_DB_ID'),
    'epics': os.getenv('NOTION_EPICS_DB_ID'),
    'guides': os.getenv('NOTION_GUIDES_DB_ID'),
    'superguide': os.getenv('NOTION_SUPER_GUIDES_DB_ID'),
    'marketing': os.getenv('NOTION_MARKETING_TASKS_DB_ID'),
    'smm': os.getenv('NOTION_SMM_TASKS_DB_ID'),
    # Добавь остальные базы по необходимости
}

# Проверка наличия всех переменных
missing_vars = [name for name, db_id in BASES.items() if not db_id]
if missing_vars:
    print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
    print("Добавьте их в .env файл или скопируйте из env.example")
    exit(1)

print(f"✅ Все переменные окружения найдены: {len(BASES)} баз")

LOG_FILE = "mcp_test_log.txt"

async def test_crud(server, db_name, db_id):
    ts = int(time.time())
    title = f"MCP_TEST_OBJECT_{db_name}_{ts}"
    log = []
    try:
        # Получить схему
        schema = await server.get_database_info({"database_id": db_id})
        log.append(f"[{db_name}] Схема: {schema}")
        # Создать объект
        props = {}
        # Найти поле title по type=="title"
        title_key = None
        if schema and isinstance(schema, list) and "properties" in schema[0]:
            props_dict = schema[0]["properties"]
            for k, v in props_dict.items():
                if isinstance(v, dict) and v.get("type") == "title":
                    title_key = k
                    break
        if title_key:
            props = {title_key: {"title": [{"type": "text", "text": {"content": title}}]}}
        else:
            # Fallback: стандартное поле
            props = {"Name": {"title": [{"type": "text", "text": {"content": title}}]}}
        res = await server.create_page({"database_id": db_id, "properties": props})
        log.append(f"[{db_name}] Создание: {res}")
        page_id = res[0].get("page_id") if res and res[0].get("success") else None
        # Проверить наличие
        found = False
        if page_id:
            pages = await server.get_pages(db_id, None)
            for p in pages:
                if p.get("id") == page_id:
                    found = True
                    break
        log.append(f"[{db_name}] Найден: {found}")
        # Удалить
        if page_id:
            del_res = await server.delete_page({"page_id": page_id})
            log.append(f"[{db_name}] Удаление: {del_res}")
        else:
            log.append(f"[{db_name}] Не удалось создать объект, удаление пропущено")
    except Exception as e:
        log.append(f"[{db_name}] Ошибка: {e}")
    # Лог в файл
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for l in log:
            f.write(l + "\n")
    print(f"[{db_name}] Готово")

async def main():
    server = NotionMCPServer()
    for db_name, db_id in BASES.items():
        await test_crud(server, db_name, db_id)

if __name__ == "__main__":
    asyncio.run(main()) 