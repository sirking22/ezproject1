import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "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")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID", "9c5f4269d61449b6a7485579a3c21da3")
TEAMS_DB_ID = os.getenv("NOTION_TEAMS_DB_ID", "d09df250ce7e4e0d9fbe4e036d320def")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN не найден")

class TaskManagementAudit:
    """Аудит системы управления задачами"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.employees = {}
        self.tasks = []
        self.issues = defaultdict(list)
        
    def fetch_employees(self) -> None:
        """Загружаем базу сотрудников"""
        print("📋 Загружаем базу сотрудников...")
        url = f"https://api.notion.com/v1/databases/{TEAMS_DB_ID}/query"
        
        results = []
        payload = {}
        while True:
            response = requests.post(url, headers=self.headers, json=payload)
            data = response.json()
            results.extend(data.get('results', []))
            if not data.get('has_more'):
                break
            payload = {"start_cursor": data.get('next_cursor')}
        
        for emp in results:
            props = emp.get("properties", {})
            # Ищем имя в разных возможных полях
            name = None
            for field in ["Name", "Имя", "ФИО", "Фамилия Имя", "Title"]:
                if field in props and props[field].get("title"):
                    name = props[field]["title"][0]["plain_text"]
                    break
            
            if name:
                self.employees[emp["id"]] = {
                    "name": name,
                    "id": emp["id"],
                    "properties": props
                }
        
        print(f"✅ Загружено {len(self.employees)} сотрудников")
        
    def fetch_tasks(self) -> None:
        """Загружаем задачи"""
        print("📋 Загружаем задачи...")
        url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
        
        results = []
        payload = {}
        while True:
            response = requests.post(url, headers=self.headers, json=payload)
            data = response.json()
            results.extend(data.get('results', []))
            if not data.get('has_more'):
                break
            payload = {"start_cursor": data.get('next_cursor')}
        
        for task in results:
            props = task.get("properties", {})
            task_info = {
                "id": task["id"],
                "title": self._extract_title(props),
                "status": self._extract_status(props),
                "assignees": self._extract_assignees(props),
                "deadline": self._extract_deadline(props),
                "created": self._extract_created(props),
                "properties": props
            }
            self.tasks.append(task_info)
        
        print(f"✅ Загружено {len(self.tasks)} задач")
    
    def _extract_title(self, props: Dict) -> str:
        """Извлекаем название задачи"""
        for field in ["Задача", "Name", "Title", "Название"]:
            if field in props and props[field].get("title"):
                return props[field]["title"][0]["plain_text"]
        return "Без названия"
    
    def _extract_status(self, props: Dict) -> str:
        """Извлекаем статус"""
        for field in ["Статус", "Status"]:
            if field in props:
                status_obj = props[field]
                if status_obj.get("status"):
                    return status_obj["status"]["name"]
                elif status_obj.get("select"):
                    return status_obj["select"]["name"]
        return "Не указан"
    
    def _extract_assignees(self, props: Dict) -> List[str]:
        """Извлекаем исполнителей"""
        for field in ["Участники", "Assignee", "Исполнитель", "Responsible"]:
            if field in props and props[field].get("people"):
                return [p.get("name", "Без имени") for p in props[field]["people"]]
        return []
    
    def _extract_deadline(self, props: Dict) -> str:
        """Извлекаем дедлайн"""
        for field in ["Дедлайн", "Due Date", "Дата", "Deadline"]:
            if field in props and props[field].get("date"):
                return props[field]["date"]["start"]
        return ""
    
    def _extract_created(self, props: Dict) -> str:
        """Извлекаем дату создания"""
        if "Created time" in props:
            return props["Created time"]["created_time"]
        return ""
    
    def analyze_issues(self) -> None:
        """Анализируем проблемы"""
        print("\n🔍 Анализируем проблемы...")
        
        now = datetime.now().date()
        
        for task in self.tasks:
            # Проблемы с исполнителями
            if not task["assignees"]:
                self.issues["no_assignee"].append(task)
            
            # Неизвестные исполнители
            for assignee in task["assignees"]:
                if assignee not in [emp["name"] for emp in self.employees.values()]:
                    self.issues["unknown_assignee"].append((task, assignee))
            
            # Проблемы со статусами
            if task["status"] in ["Не указан", ""]:
                self.issues["no_status"].append(task)
            
            # Просроченные задачи
            if task["deadline"]:
                try:
                    deadline = datetime.fromisoformat(task["deadline"].split("T")[0]).date()
                    if deadline < now and task["status"].lower() not in ["done", "выполнена", "завершена"]:
                        self.issues["overdue"].append((task, deadline))
                except:
                    self.issues["invalid_deadline"].append(task)
            
            # Задачи без дедлайна
            if not task["deadline"]:
                self.issues["no_deadline"].append(task)
            
            # Старые задачи в ToDo
            if task["status"].lower() in ["to do", "todo", "не начата"]:
                if task["created"]:
                    try:
                        created = datetime.fromisoformat(task["created"].split("T")[0]).date()
                        if created < now - timedelta(days=7):
                            self.issues["old_todo"].append((task, created))
                    except:
                        pass
    
    def generate_report(self) -> None:
        """Генерируем отчет"""
        print("\n📊 ОТЧЕТ ПО АУДИТУ СИСТЕМЫ УПРАВЛЕНИЯ ЗАДАЧАМИ")
        print("=" * 60)
        
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Всего задач: {len(self.tasks)}")
        print(f"   • Всего сотрудников: {len(self.employees)}")
        
        # Статистика по статусам
        status_counts = defaultdict(int)
        for task in self.tasks:
            status_counts[task["status"]] += 1
        
        print(f"\n📋 СТАТУСЫ ЗАДАЧ:")
        for status, count in sorted(status_counts.items()):
            print(f"   • {status}: {count}")
        
        # Проблемы
        print(f"\n🚨 ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ:")
        
        if self.issues["no_assignee"]:
            print(f"   ❌ Задачи без исполнителя: {len(self.issues['no_assignee'])}")
            for task in self.issues["no_assignee"][:3]:
                print(f"      - {task['title']}")
        
        if self.issues["unknown_assignee"]:
            print(f"   ⚠️ Неизвестные исполнители: {len(self.issues['unknown_assignee'])}")
            unknown_names = set(assignee for _, assignee in self.issues["unknown_assignee"])
            for name in list(unknown_names)[:5]:
                print(f"      - {name}")
        
        if self.issues["no_status"]:
            print(f"   ❌ Задачи без статуса: {len(self.issues['no_status'])}")
        
        if self.issues["overdue"]:
            print(f"   🔴 Просроченные задачи: {len(self.issues['overdue'])}")
            for task, deadline in self.issues["overdue"][:3]:
                print(f"      - {task['title']} (до {deadline})")
        
        if self.issues["no_deadline"]:
            print(f"   ⚠️ Задачи без дедлайна: {len(self.issues['no_deadline'])}")
        
        if self.issues["old_todo"]:
            print(f"   ⏰ Старые задачи в ToDo: {len(self.issues['old_todo'])}")
            for task, created in self.issues["old_todo"][:3]:
                print(f"      - {task['title']} (создана {created})")
        
        if self.issues["invalid_deadline"]:
            print(f"   ❌ Некорректные дедлайны: {len(self.issues['invalid_deadline'])}")
    
    def suggest_actions(self) -> None:
        """Предлагаем действия для исправления"""
        print(f"\n🎯 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
        
        if self.issues["no_assignee"]:
            print("   1. Назначить исполнителей для задач без ответственных")
        
        if self.issues["unknown_assignee"]:
            print("   2. Синхронизировать имена исполнителей с базой сотрудников")
        
        if self.issues["no_status"]:
            print("   3. Установить статусы для задач без статуса")
        
        if self.issues["overdue"]:
            print("   4. Пересмотреть дедлайны просроченных задач")
        
        if self.issues["old_todo"]:
            print("   5. Перевести старые ToDo задачи в соответствующие статусы")
        
        print("\n   6. Настроить автоматические правила:")
        print("      - Автоматическое назначение исполнителей")
        print("      - Уведомления о просроченных задачах")
        print("      - Автоматическое обновление статусов")
    
    def save_detailed_report(self) -> None:
        """Сохраняем детальный отчет"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tasks": len(self.tasks),
                "total_employees": len(self.employees),
                "issues_count": {k: len(v) for k, v in self.issues.items()}
            },
            "employees": list(self.employees.values()),
            "issues": {
                k: [{"id": t["id"], "title": t["title"]} for t in v] if v and isinstance(v[0], dict) else v
                for k, v in self.issues.items()
            }
        }
        
        with open("task_audit_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Детальный отчет сохранен в task_audit_report.json")

def main():
    """Основная функция"""
    print("🔍 АУДИТ СИСТЕМЫ УПРАВЛЕНИЯ ЗАДАЧАМИ")
    print("=" * 50)
    
    audit = TaskManagementAudit()
    
    try:
        audit.fetch_employees()
        audit.fetch_tasks()
        audit.analyze_issues()
        audit.generate_report()
        audit.suggest_actions()
        audit.save_detailed_report()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 