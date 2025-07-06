import asyncio
from notion_mcp_server import NotionMCPServer

async def analyze_correct_tasks():
    """Анализ правильной базы ЗАДАЧ (не подзадач)"""
    
    server = NotionMCPServer()
    
    print("🎯 АНАЛИЗ ПРАВИЛЬНОЙ БАЗЫ ЗАДАЧ")
    print("=" * 50)
    print("📋 База ЗАДАЧ: d09df250ce7e4e0d9fbe4e036d320def")
    print("📋 База ПОДЗАДАЧ: 9c5f4269d61449b6a7485579a3c21da3")
    
    # Анализируем базу ЗАДАЧ
    print("\n📊 Анализируем базу ЗАДАЧ...")
    
    result_list = list(await server.call_tool(
        "analyze_notion_completeness",
        {
            "database_id": "d09df250ce7e4e0d9fbe4e036d320def",  # Tasks DB (не подзадачи!)
            "freshness_days": 30
        }
    ))
    
    print("\n===== АНАЛИЗ БАЗЫ ЗАДАЧ =====")
    if result_list:
        print(str(result_list[0]))
    print("==============================")

if __name__ == "__main__":
    asyncio.run(analyze_correct_tasks()) 