import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.types import TextContent

async def analyze_tasks_via_mcp():
    """Анализ задач через MCP сервер"""
    
    # Подключаемся к MCP серверу
    server = StdioServerParameters(
        command="python",
        args=["-m", "mcp.server", "stdio", "--config", "mcp_config.json"]
    )
    
    async with ClientSession(server) as session:
        print("🔗 Подключение к MCP серверу...")
        
        # Получаем список доступных инструментов
        tools = await session.list_tools()
        print(f"📋 Доступные инструменты: {[t.name for t in tools.tools]}")
        
        # Анализируем базу задач
        print("\n🎯 АНАЛИЗ БАЗЫ ЗАДАЧ:")
        
        # Получаем структуру базы задач
        result = await session.call_tool("notion_get_database", {
            "database_id": "9c5f4269d61449b6a7485579a3c21da3"
        })
        
        if result.content:
            db_info = json.loads(result.content[0].text)
            print(f"📊 База задач: {db_info.get('title', 'Неизвестно')}")
            print(f"📋 Поля: {list(db_info.get('properties', {}).keys())}")
        
        # Получаем задачи в статусе To Do
        result = await session.call_tool("notion_query_database", {
            "database_id": "9c5f4269d61449b6a7485579a3c21da3",
            "filter": {
                "property": " Статус",
                "status": {
                    "equals": "To do"
                }
            }
        })
        
        if result.content:
            tasks = json.loads(result.content[0].text)
            print(f"\n🎯 ЗАДАЧИ В СТАТУСЕ 'TO DO': {len(tasks)}")
            
            # Анализируем структуру первой задачи
            if tasks:
                first_task = tasks[0]
                print(f"\n📋 СТРУКТУРА ЗАДАЧИ:")
                print(f"   ID: {first_task.get('id')}")
                print(f"   Поля: {list(first_task.get('properties', {}).keys())}")
                
                # Ищем поле с названием
                props = first_task.get('properties', {})
                for field_name, field_data in props.items():
                    if field_data.get('type') == 'title':
                        print(f"   ✅ НАЗВАНИЕ в поле '{field_name}': {field_data.get('title', [{}])[0].get('plain_text', '')}")
                    elif field_data.get('type') == 'rich_text':
                        print(f"   📝 Rich text в поле '{field_name}': {field_data.get('rich_text', [{}])[0].get('plain_text', '')}")

if __name__ == "__main__":
    asyncio.run(analyze_tasks_via_mcp()) 