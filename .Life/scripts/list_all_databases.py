#!/usr/bin/env python3
"""
Скрипт для поиска всех баз данных в Notion
"""

import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

def list_all_databases():
    """Ищу все базы данных в Notion"""
    
    client = Client(auth=os.getenv("NOTION_TOKEN"))
    
    print("🔍 Ищу все базы данных в Notion...")
    
    try:
        # Ищем все базы данных
        response = client.search(
            query="",
            filter={"property": "object", "value": "database"}
        )
        
        print(f"📊 Найдено баз данных: {len(response['results'])}")
        
        for i, db in enumerate(response['results'], 1):
            db_id = db['id']
            db_title = db.get('title', [{}])[0].get('plain_text', 'БЕЗ НАЗВАНИЯ') if db.get('title') else 'БЕЗ НАЗВАНИЯ'
            
            print(f"\n{i}. {db_title}")
            print(f"   ID: {db_id}")
            
            # Проверяем количество записей
            try:
                entries = client.databases.query(database_id=db_id, page_size=1)
                total_entries = len(entries['results'])
                print(f"   Записей: {total_entries}")
                
                # Если это база привычек или похожая
                if 'привыч' in db_title.lower() or 'habit' in db_title.lower() or 'tracker' in db_title.lower():
                    print(f"   ⭐ ВОЗМОЖНО ЭТО БАЗА ПРИВЫЧЕК!")
                    
            except Exception as e:
                print(f"   Ошибка при проверке: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    list_all_databases() 