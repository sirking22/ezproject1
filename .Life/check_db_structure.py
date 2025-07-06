#!/usr/bin/env python3
"""
Автоматическая проверка структуры Notion баз данных
"""

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

async def check_db_structure():
    """Проверяет структуру всех баз данных"""
    client = AsyncClient(auth=NOTION_TOKEN)
    
    print("🔍 Проверка структуры Notion баз данных...")
    print("=" * 50)
    
    for db_name, db_id in DBS.items():
        print(f"\n📊 {db_name.upper()}")
        print("-" * 30)
        
        if not db_id:
            print(f"❌ ID базы данных не найден в переменных окружения")
            continue
            
        try:
            db = await client.databases.retrieve(database_id=db_id)
            print(f"✅ База найдена: {db['title'][0]['plain_text']}")
            print(f"📋 Поля:")
            
            for prop_name, prop_data in db['properties'].items():
                prop_type = prop_data['type']
                print(f"   • {prop_name}: {prop_type}")
                
        except Exception as e:
            print(f"❌ Ошибка доступа к базе: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Проверка завершена")

if __name__ == "__main__":
    asyncio.run(check_db_structure()) 