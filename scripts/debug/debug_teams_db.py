import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TEAMS_DB_ID = os.getenv("NOTION_TEAMS_DB_ID", "1d6ace03d9ff805787b9")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

print(f"🔍 ОТЛАДКА БАЗЫ СОТРУДНИКОВ: {TEAMS_DB_ID}")
print("=" * 50)

url = f"https://api.notion.com/v1/databases/{TEAMS_DB_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Получаем первые 10 сотрудников
payload = {"page_size": 10}
response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print(f"❌ Ошибка API: {response.status_code}")
    print(f"Ответ: {response.text}")
    exit(1)

data = response.json()
results = data.get('results', [])

print(f"✅ Найдено сотрудников: {len(results)}")
print(f"📊 Всего в базе: {data.get('total', 'неизвестно')}")

if not results:
    print("❌ Сотрудники не найдены")
    exit(0)

print(f"\n📋 ПЕРВЫЕ {len(results)} СОТРУДНИКОВ:")
print("=" * 60)

for i, emp in enumerate(results, 1):
    print(f"\n{i}. СОТРУДНИК {emp['id']}")
    print("-" * 40)
    
    props = emp.get("properties", {})
    print(f"   Доступные поля: {list(props.keys())}")
    
    # Пытаемся извлечь основные поля
    name = "Не найдено"
    role = "Не найдено"
    
    for field_name, field_data in props.items():
        print(f"   {field_name}: {type(field_data)}")
        
        if field_data.get("title"):
            name = field_data["title"][0]["plain_text"] if field_data["title"] else "Пустое имя"
        elif field_data.get("select"):
            role = field_data["select"]["name"] if field_data["select"] else "Без роли"
        elif field_data.get("rich_text"):
            role = " ".join([t["plain_text"] for t in field_data["rich_text"]]) if field_data["rich_text"] else "Без роли"
    
    print(f"   Имя: {name}")
    print(f"   Роль: {role}")
    
    # Проверяем, является ли дизайнером
    is_designer = False
    if "дизайн" in role.lower():
        is_designer = True
    
    print(f"   Дизайнер: {'✅' if is_designer else '❌'}")

print(f"\n💡 РЕКОМЕНДАЦИИ:")
print(f"   • Проверьте правильность ID базы сотрудников")
print(f"   • Убедитесь, что у токена есть доступ к этой базе")
print(f"   • Проверьте названия полей в базе") 