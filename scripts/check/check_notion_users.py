import requests
import json
import os

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_TEAMS_DB_ID")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")

if not NOTION_TOKEN or not DATABASE_ID:
    raise RuntimeError("NOTION_TOKEN и NOTION_TEAMS_DB_ID должны быть заданы в переменных окружения")

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

results = []
payload = {}
while True:
    response = requests.post(url, headers=headers, json=payload)
    try:
        data = response.json()
    except Exception as e:
        print(f"Ошибка парсинга JSON: {e}\nStatus: {response.status_code}\nResponse: {response.text[:500]}")
        break
    results.extend(data.get('results', []))
    if not data.get('has_more'):
        break
    payload = {"start_cursor": data.get('next_cursor')}

with open("users_dump.json", "w", encoding="utf-8") as f:
    json.dump({"results": results}, f, ensure_ascii=False, indent=2)

print(f"Выгружено {len(results)} сотрудников. Сохранено в users_dump.json") 