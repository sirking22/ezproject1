import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")

if not NOTION_TOKEN or not TASKS_DB_ID:
    raise RuntimeError("NOTION_TOKEN и NOTION_TASKS_DB_ID должны быть заданы в переменных окружения")

url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

results = []
payload = {}
while True:
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    results.extend(data.get('results', []))
    if not data.get('has_more'):
        break
    payload = {"start_cursor": data.get('next_cursor')}

def extract_task_info(task):
    props = task.get("properties", {})
    title = ""
    for key in ["Задача", "Name", "Title", "Название"]:
        if key in props and props[key].get("title"):
            title = props[key]["title"][0]["plain_text"]
            break
    status = ""
    for key in ["Статус", "Status"]:
        if key in props:
            s = props[key]
            if s.get("status"):
                status = s["status"]["name"]
            elif s.get("select"):
                status = s["select"]["name"]
            break
    assignees = []
    for key in ["Участники", "Assignee", "Исполнитель", "Responsible"]:
        if key in props and props[key].get("people"):
            assignees = [p.get("name", "Без имени") for p in props[key]["people"]]
            break
    return {"title": title, "status": status, "assignees": assignees}

tasks = [extract_task_info(t) for t in results]

print(f"{'Задача':<40} {'Статус':<15} {'Исполнители'}")
print("-" * 80)
for t in tasks:
    if t["status"].lower() in ["to do", "todo", "не начата"] and t["assignees"]:
        print(f"{t['title'][:40]:<40} {t['status']:<15} {', '.join(t['assignees'])}") 