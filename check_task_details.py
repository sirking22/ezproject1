import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = "d09df250ce7e4e0d9fbe4e036d320def"

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

def find_task_by_title(title):
    """Найти задачу по названию"""
    url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "filter": {
            "property": "Задача",
            "title": {
                "contains": title
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Ошибка поиска задачи: {response.status_code}")
        return None
    
    data = response.json()
    results = data.get('results', [])
    
    if results:
        return results[0]
    return None

def main():
    print("🔍 ДЕТАЛИ ЗАДАЧИ 'ИКОНКИ'")
    print("=" * 40)
    
    task = find_task_by_title("Иконки")
    if not task:
        print("❌ Задача 'Иконки' не найдена")
        return
    
    print(f"ID задачи: {task['id']}")
    print(f"Название: {task['properties']['Задача']['title'][0]['plain_text']}")
    
    # Проверим все свойства
    print("\n📋 ВСЕ СВОЙСТВА:")
    for prop_name, prop_value in task['properties'].items():
        print(f"\n{prop_name}:")
        print(f"  Тип: {prop_value.get('type', 'unknown')}")
        print(f"  Значение: {json.dumps(prop_value, indent=2, ensure_ascii=False)}")
    
    # Особое внимание к участникам
    if 'Участники' in task['properties']:
        participants = task['properties']['Участники']
        print(f"\n👥 УЧАСТНИКИ:")
        print(f"  Тип: {participants.get('type')}")
        if participants.get('people'):
            for person in participants['people']:
                print(f"  - {person.get('name', 'Без имени')} (ID: {person.get('id')})")
        else:
            print("  Нет участников")

if __name__ == "__main__":
    main() 