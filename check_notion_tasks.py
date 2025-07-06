import requests
import json
import os

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DESIGN_TASKS_DB_ID")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")

if not NOTION_TOKEN or not DATABASE_ID:
    raise RuntimeError("NOTION_TOKEN и NOTION_DESIGN_TASKS_DB_ID должны быть заданы в переменных окружения")

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

with open("tasks_dump.json", "w", encoding="utf-8") as f:
    json.dump({"results": results}, f, ensure_ascii=False, indent=2)

# Ключевые поля для анализа
def extract_task_info(task):
    props = task.get("properties", {})
    # Безопасно достаем дату
    date_val = props.get("Дата", {}).get("date")
    deadline = date_val.get("start", "") if isinstance(date_val, dict) and date_val else ""

    return {
        "id": task.get("id"),
        "title": props.get("Задача", {}).get("title", [{}])[0].get("plain_text", "") if props.get("Задача", {}).get("title") else "",
        "status": props.get("Статус", {}).get("status", {}).get("name", ""),
        "assignees": [p.get("name") for p in props.get("Участники", {}).get("people", [])],
        "deadline": deadline,
        "materials": props.get("Материалы", {}).get("relation", []) or [],
        "subtasks": props.get("Под задачи", {}).get("relation", []) or [],
    }

tasks_info = [extract_task_info(t) for t in results]
print("Первые 10 задач:")
for t in tasks_info[:10]:
    print(json.dumps(t, ensure_ascii=False, indent=2))

print(f"Выгружено {len(results)} задач. Сохранено в tasks_dump.json") 