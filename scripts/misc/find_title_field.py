import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID", "9c5f4269d61449b6a7485579a3c21da3")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

print("🔍 ПОИСК ПОЛЯ С НАЗВАНИЕМ ЗАДАЧИ")
print("=" * 50)

url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Получаем первые 3 задачи
payload = {"page_size": 3}
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print(f"❌ Ошибка API: {response.status_code}")
    exit(1)

data = response.json()
results = data.get('results', [])

print(f"📊 Получено задач: {len(results)}")

for i, task in enumerate(results, 1):
    print(f"\n{i}. ЗАДАЧА {task['id']}")
    print("-" * 40)
    
    props = task.get("properties", {})
    
    # Проверяем все поля на наличие title
    for field_name, field_data in props.items():
        if field_data.get("type") == "title" and field_data.get("title"):
            print(f"✅ НАЙДЕНО НАЗВАНИЕ в поле '{field_name}':")
            for title_part in field_data["title"]:
                print(f"   {title_part.get('plain_text', '')}")
        elif field_data.get("type") == "rich_text" and field_data.get("rich_text"):
            print(f"📝 Rich text в поле '{field_name}':")
            for text_part in field_data["rich_text"]:
                print(f"   {text_part.get('plain_text', '')}")
        elif field_data.get("type") == "relation":
            print(f"🔗 Relation в поле '{field_name}': {len(field_data.get('relation', []))} связей")
        elif field_data.get("type") == "status":
            status = field_data.get("status", {})
            print(f"📊 Статус в поле '{field_name}': {status.get('name', 'Не указан')}")
        elif field_data.get("type") == "people":
            people = field_data.get("people", [])
            names = [p.get("name", "Без имени") for p in people]
            print(f"👥 Люди в поле '{field_name}': {', '.join(names)}")

print(f"\n💡 Ищем поле с реальным названием задачи!") 