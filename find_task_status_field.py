import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = "d09df250ce7e4e0d9fbe4e036d320def"  # Правильная база задач

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

print("🔍 ПОИСК ПОЛЯ СТАТУСА В БАЗЕ ЗАДАЧ")
print("=" * 50)

url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Получаем первые 5 задач
payload = {"page_size": 5}
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print(f"❌ Ошибка API: {response.status_code}")
    exit(1)

data = response.json()
results = data.get('results', [])

print(f"📊 Получено задач: {len(results)}")

for i, task in enumerate(results, 1):
    print(f"\n{i}. ЗАДАЧА {task['id']}")
    print("-" * 50)
    
    props = task.get("properties", {})
    
    # Показываем ВСЕ поля с их типами
    print("📋 ВСЕ ПОЛЯ:")
    for field_name, field_data in props.items():
        field_type = field_data.get("type", "unknown")
        print(f"   • {field_name} ({field_type})")
        
        # Если это status - показываем содержимое
        if field_type == "status" and field_data.get("status"):
            print(f"     СТАТУС: {field_data['status']['name']}")
        elif field_type == "title" and field_data.get("title"):
            print(f"     НАЗВАНИЕ: {field_data['title'][0].get('plain_text', '')}")
        elif field_type == "rich_text" and field_data.get("rich_text"):
            print(f"     ТЕКСТ: {field_data['rich_text'][0].get('plain_text', '')}")
        elif field_type == "people" and field_data.get("people"):
            names = [p.get("name", "Без имени") for p in field_data["people"]]
            print(f"     ЛЮДИ: {', '.join(names)}")
        elif field_type == "select" and field_data.get("select"):
            print(f"     SELECT: {field_data['select']['name']}")

print(f"\n💡 Ищем поле со статусом задач!") 