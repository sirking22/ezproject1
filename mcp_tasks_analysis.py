import asyncio
from notion_mcp_server import NotionMCPServer

async def analyze_tasks_via_mcp():
    """Анализ задач через наш NotionMCPServer"""
    
    server = NotionMCPServer()
    
    print("🎯 АНАЛИЗ ЗАДАЧ ЧЕРЕЗ MCP СЕРВЕР")
    print("=" * 50)
    
    # Получаем задачи в статусе To Do
    print("📋 Получаем задачи в статусе 'To do'...")
    
    result_list = list(await server.call_tool(
        "analyze_notion_completeness",
        {
            "database_id": "9c5f4269d61449b6a7485579a3c21da3",  # Tasks DB
            "freshness_days": 30
        }
    ))
    
    print("\n===== РЕЗУЛЬТАТ АНАЛИЗА =====")
    if result_list:
        print(str(result_list[0]))
    print("=============================")
    
    # Попробуем получить структуру базы
    print("\n📊 Получаем структуру базы задач...")
    
    result_list = list(await server.call_tool(
        "get_notion_database_structure",
        {
            "database_id": "9c5f4269d61449b6a7485579a3c21da3"
        }
    ))
    
    print("\n===== СТРУКТУРА БАЗЫ =====")
    if result_list:
        print(str(result_list[0]))
    print("==========================")

if __name__ == "__main__":
    asyncio.run(analyze_tasks_via_mcp()) 