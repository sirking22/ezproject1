import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TEAMS_DB_ID = "342f18c67a5e41fead73dcec00770f4e"  # База команд

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

def search_teams_db():
    """Поиск в базе команд"""
    url = f"https://api.notion.com/v1/databases/{TEAMS_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "filter": {
            "or": [
                {
                    "property": "Name",
                    "rich_text": {
                        "contains": "Arsentiy"
                    }
                },
                {
                    "property": "Name", 
                    "rich_text": {
                        "contains": "Арс"
                    }
                },
                {
                    "property": "Name",
                    "rich_text": {
                        "contains": "Arseniy"
                    }
                }
            ]
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Ошибка поиска: {response.status_code}")
        return None
    
    return response.json()

def main():
    print("🔍 ПОИСК АРСЕНИЯ В БАЗЕ КОМАНД")
    print("=" * 40)
    
    data = search_teams_db()
    if not data:
        return
    
    results = data.get('results', [])
    print(f"Найдено записей: {len(results)}")
    
    for i, record in enumerate(results, 1):
        print(f"\n{i}. Запись:")
        properties = record.get('properties', {})
        
        for prop_name, prop_value in properties.items():
            if prop_value.get('type') == 'title' and prop_value.get('title'):
                title = prop_value['title'][0]['plain_text']
                print(f"   Название: {title}")
            elif prop_value.get('type') == 'rich_text' and prop_value.get('rich_text'):
                text = prop_value['rich_text'][0]['plain_text']
                print(f"   {prop_name}: {text}")
            elif prop_value.get('type') == 'select' and prop_value.get('select'):
                select_value = prop_value['select']['name']
                print(f"   {prop_name}: {select_value}")
            elif prop_value.get('type') == 'people' and prop_value.get('people'):
                people = [p.get('name', 'Без имени') for p in prop_value['people']]
                print(f"   {prop_name}: {', '.join(people)}")

if __name__ == "__main__":
    main() 