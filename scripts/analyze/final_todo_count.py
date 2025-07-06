import os
import requests
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = "d09df250ce7e4e0d9fbe4e036d320def"  # Правильная база задач

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

print("🎯 ФИНАЛЬНЫЙ ПРАВИЛЬНЫЙ ПОДСЧЕТ ЗАДАЧ В СТАТУСЕ 'TO DO'")
print("=" * 70)
print("📋 База ЗАДАЧ (не подзадач): d09df250ce7e4e0d9fbe4e036d320def")

url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Получаем ВСЕ задачи
print("📋 Загружаем все задачи...")
results = []
payload = {}
while True:
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    results.extend(data.get('results', []))
    if not data.get('has_more'):
        break
    payload = {"start_cursor": data.get('next_cursor')}

print(f"📊 Всего задач в базе: {len(results)}")

# Анализируем статусы
status_counts = defaultdict(int)
todo_tasks = []
assignee_counts = defaultdict(int)

for task in results:
    props = task.get("properties", {})
    
    # Извлекаем статус
    status = "Не указан"
    if "Статус" in props:
        s = props["Статус"]
        if s.get("status"):
            status = s["status"]["name"]
    
    status_counts[status] += 1
    
    # Если статус To do - сохраняем задачу
    if status.lower() in ["to do", "todo", "не начата"]:
        # Извлекаем название из поля "Задача"
        title = "Без названия"
        if "Задача" in props and props["Задача"].get("title"):
            title = props["Задача"]["title"][0]["plain_text"]
        
        # Извлекаем исполнителей
        assignees = []
        if "Участники" in props and props["Участники"].get("people"):
            for person in props["Участники"]["people"]:
                assignee_name = person.get("name", "Без имени")
                if assignee_name.lower() != "account":  # Исключаем Account
                    assignees.append(assignee_name)
                    assignee_counts[assignee_name] += 1
        
        todo_tasks.append({
            "id": task["id"],
            "title": title,
            "assignees": assignees
        })

print(f"\n📈 СТАТИСТИКА ПО СТАТУСАМ:")
for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   • {status}: {count}")

print(f"\n🎯 ЗАДАЧИ В СТАТУСЕ 'TO DO': {len(todo_tasks)}")

print(f"\n👥 РАСПРЕДЕЛЕНИЕ TODO ЗАДАЧ ПО ИСПОЛНИТЕЛЯМ:")
for assignee, count in sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   • {assignee}: {count}")

# Показываем примеры задач To do
print(f"\n📋 ПРИМЕРЫ ЗАДАЧ TO DO:")
for i, task in enumerate(todo_tasks[:15], 1):
    assignees_str = ", ".join(task["assignees"]) if task["assignees"] else "Без исполнителя"
    print(f"   {i}. {task['title'][:80]} → {assignees_str}")

if len(todo_tasks) > 15:
    print(f"   ... и еще {len(todo_tasks) - 15} задач")

print(f"\n✅ ФИНАЛЬНЫЙ РЕЗУЛЬТАТ: {len(todo_tasks)} задач в статусе To Do")
print(f"💡 Это РЕАЛЬНОЕ количество ЗАДАЧ (не подзадач)!") 