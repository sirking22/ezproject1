import json
from datetime import datetime
import unicodedata
from collections import defaultdict

with open("tasks_dump.json", encoding="utf-8") as f:
    data = json.load(f)["results"]

def extract_task_info(task):
    props = task.get("properties", {})
    date_val = props.get("Дата", {}).get("date")
    deadline = date_val.get("start", "") if isinstance(date_val, dict) and date_val else ""
    return {
        "id": task.get("id"),
        "title": props.get("Задача", {}).get("title", [{}])[0].get("plain_text", "") if props.get("Задача", {}).get("title") else "",
        "status": props.get("Статус", {}).get("status", {}).get("name", ""),
        "assignees": [p.get("name") for p in props.get("Участники", {}).get("people", [])],
        "deadline": deadline,
        "subtasks": props.get("Под задачи", {}).get("relation", []) or [],
    }

# Загружаем сотрудников
try:
    with open("users_dump.json", encoding="utf-8") as f:
        users_data = json.load(f)["results"]
    def extract_user_name(u):
        props = u.get("properties", {})
        # Попробуем взять имя из стандартных полей
        for key in ["Name", "Имя", "ФИО", "Фамилия Имя"]:
            if key in props and props[key].get("title"):
                return props[key]["title"][0]["plain_text"]
        return None
    users = set(filter(None, (extract_user_name(u) for u in users_data)))
except Exception as e:
    print(f"Не удалось загрузить users_dump.json: {e}")
    users = set()

tasks = [extract_task_info(t) for t in data]

# KPI агрегатор
kpi = defaultdict(lambda: {"total": 0, "todo": 0, "in_progress": 0, "done": 0, "overdue": 0, "with_subtasks": 0})
now = datetime.now().date()

for t in tasks:
    assignees = t["assignees"] or ["Без исполнителя"]
    for assignee in assignees:
        name = assignee if assignee else "Без имени"
        # Нормализуем имя для сопоставления
        norm_name = unicodedata.normalize("NFKC", name.strip())
        if users and norm_name not in users:
            norm_name = f"НЕИЗВЕСТНЫЙ: {name}" if name != "Без исполнителя" else name
        kpi[norm_name]["total"] += 1
        status = t["status"].lower()
        if status == "to do":
            kpi[norm_name]["todo"] += 1
        elif status == "in progress":
            kpi[norm_name]["in_progress"] += 1
        elif status == "done":
            kpi[norm_name]["done"] += 1
        # Просрочка
        if t["deadline"]:
            try:
                d = datetime.fromisoformat(t["deadline"]).date()
                if d < now and status != "done":
                    kpi[norm_name]["overdue"] += 1
            except Exception:
                pass
        if t["subtasks"]:
            kpi[norm_name]["with_subtasks"] += 1

# Вывод
print("KPI по сотрудникам (только из базы исполнителей):")
print(f"{'Сотрудник':<25} {'Всего':<5} {'ToDo':<5} {'InPrg':<5} {'Done':<5} {'Просрочено':<10} {'С подзадачами':<15}")
for designer, stats in sorted(kpi.items()):
    if not users or designer in users or designer.startswith("НЕИЗВЕСТНЫЙ") or designer in ["Без исполнителя", "Без имени"]:
        print(f"{designer:<25} {stats['total']:<5} {stats['todo']:<5} {stats['in_progress']:<5} {stats['done']:<5} {stats['overdue']:<10} {stats['with_subtasks']:<15}") 