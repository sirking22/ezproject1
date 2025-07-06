import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID", "9c5f4269d61449b6a7485579a3c21da3")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

print("🔍 ОТЛАДКА СЫРЫХ ДАННЫХ API")
print("=" * 50)
print(f"База данных: {TASKS_DB_ID}")

url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Получаем только первые 5 задач
payload = {"page_size": 5}
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print(f"❌ Ошибка API: {response.status_code}")
    print(f"Ответ: {response.text}")
    exit(1)

data = response.json()
results = data.get('results', [])

print(f"📊 Получено задач: {len(results)}")

for i, task in enumerate(results, 1):
    print(f"\n{i}. ЗАДАЧА {task['id']}")
    print("-" * 40)
    
    props = task.get("properties", {})
    print(f"Поля: {list(props.keys())}")
    
    # Показываем сырые данные статуса
    if " Статус" in props:
        print(f"Статус (сырые данные): {json.dumps(props[' Статус'], indent=2)}")
    elif "Статус" in props:
        print(f"Статус (сырые данные): {json.dumps(props['Статус'], indent=2)}")
    else:
        print("Статус: НЕ НАЙДЕН")
    
    # Показываем название
    if "Задачи" in props:
        print(f"Название (сырые данные): {json.dumps(props['Задачи'], indent=2)}")
    else:
        print("Название: НЕ НАЙДЕНО")
    
    # Показываем исполнителя
    if "Исполнитель" in props:
        print(f"Исполнитель (сырые данные): {json.dumps(props['Исполнитель'], indent=2)}")
    else:
        print("Исполнитель: НЕ НАЙДЕН")

print(f"\n💡 Проверь, что я правильно читаю статусы!") 