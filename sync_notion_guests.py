import asyncio
from notion_mcp_server import NotionMCPServer
from config.notion_users import sync_guest_uuids_from_tasks

if __name__ == "__main__":
    server = NotionMCPServer()
    tasks_db_id = server.tasks_db_id
    print(f"\n[SYNC] Синхронизация UUID гостей из базы задач: {tasks_db_id}")
    sync_guest_uuids_from_tasks(server, tasks_db_id)
    print("[SYNC] Готово!") 