import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID", "9c5f4269d61449b6a7485579a3c21da3")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

print("🔍 ПОИСК ПРАВИЛЬНОГО ПОЛЯ С НАЗВАНИЕМ ЗАДАЧИ")
print("=" * 60)

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
        
        # Если это title - показываем содержимое
        if field_type == "title" and field_data.get("title"):
            print(f"     СОДЕРЖИМОЕ: {field_data['title'][0].get('plain_text', '')}")
        elif field_type == "rich_text" and field_data.get("rich_text"):
            print(f"     СОДЕРЖИМОЕ: {field_data['rich_text'][0].get('plain_text', '')}")
        elif field_type == "status" and field_data.get("status"):
            print(f"     СОДЕРЖИМОЕ: {field_data['status']['name']}")
        elif field_type == "people" and field_data.get("people"):
            names = [p.get("name", "Без имени") for p in field_data["people"]]
            print(f"     СОДЕРЖИМОЕ: {', '.join(names)}")

print(f"\n💡 Ищем поле с НАЗВАНИЕМ ЗАДАЧИ (не подзадач)!") 