#!/usr/bin/env python3
"""
Выводит статус и участников для первых 20 задач (отладка структуры поля)
"""
import asyncio
import json
from mcp_notion_server import NotionMCPServer

async def debug_participants_status():
    server = NotionMCPServer()
    tasks_db_id = server.tasks_db_id or "d09df250ce7e4e0d9fbe4e036d320def"
    tasks_response = await server.get_database_pages(tasks_db_id)
    if not tasks_response.get('success'):
        print(f"❌ Ошибка получения задач: {tasks_response.get('error')}")
        return
    tasks = tasks_response.get('pages', [])
    print(f"Всего задач: {len(tasks)}\n")
    for i, task in enumerate(tasks[:20]):
        props = task.get('properties', {})
        title = props.get('Задача', 'Без названия')
        status = props.get('Статус', '')
        participants = props.get('Участники', '')
        print(f"{i+1}. {title}")
        print(f"   Статус: {status}")
        print(f"   Участники: {participants}")
        print('-'*40)

if __name__ == "__main__":
    asyncio.run(debug_participants_status()) 