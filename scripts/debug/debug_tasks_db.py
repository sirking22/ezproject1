import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID", "9c5f4269d61449b6a7485579a3c21da3")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

print(f"🔍 ОТЛАДКА БАЗЫ ЗАДАЧ: {TASKS_DB_ID}")
print("=" * 50)

url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Получаем первые 10 задач
payload = {"page_size": 10}
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print(f"❌ Ошибка API: {response.status_code}")
    print(f"Ответ: {response.text}")
    exit(1)

data = response.json()
results = data.get('results', [])

print(f"✅ Найдено задач: {len(results)}")
print(f"📊 Всего в базе: {data.get('total', 'неизвестно')}")

if not results:
    print("❌ Задачи не найдены")
    exit(0)

print(f"\n📋 ПЕРВЫЕ {len(results)} ЗАДАЧ:")
print("=" * 60)

for i, task in enumerate(results, 1):
    print(f"\n{i}. ЗАДАЧА {task['id']}")
    print("-" * 40)
    
    props = task.get("properties", {})
    print(f"   Доступные поля: {list(props.keys())}")
    
    # Пытаемся извлечь основные поля
    title = "Не найдено"
    status = "Не найдено"
    assignees = []
    
    for field_name, field_data in props.items():
        print(f"   {field_name}: {type(field_data)}")
        
        if field_data.get("title"):
            title = field_data["title"][0]["plain_text"] if field_data["title"] else "Пустое название"
        elif field_data.get("select"):
            status = field_data["select"]["name"] if field_data["select"] else "Без статуса"
        elif field_data.get("status"):
            status = field_data["status"]["name"] if field_data["status"] else "Без статуса"
        elif field_data.get("people"):
            assignees = [p.get("name", "Без имени") for p in field_data["people"]]
    
    print(f"   Название: {title}")
    print(f"   Статус: {status}")
    print(f"   Исполнители: {assignees}")

print(f"\n💡 РЕКОМЕНДАЦИИ:")
print(f"   • Проверьте правильность ID базы данных")
print(f"   • Убедитесь, что у токена есть доступ к этой базе")
print(f"   • Проверьте названия полей в базе") 