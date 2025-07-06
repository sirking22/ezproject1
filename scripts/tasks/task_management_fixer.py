import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")
TEAMS_DB_ID = os.getenv("NOTION_TEAMS_DB_ID")

if not all([NOTION_TOKEN, TASKS_DB_ID, TEAMS_DB_ID]):
    raise RuntimeError("Необходимы NOTION_TOKEN, NOTION_TASKS_DB_ID, NOTION_TEAMS_DB_ID")

class TaskManagementFixer:
    """Автоматическое исправление проблем в системе управления задачами"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.employees = {}
        self.tasks = []
        self.fixes_applied = defaultdict(list)
        self.errors = []
        
    def load_audit_report(self) -> bool:
        """Загружаем отчет аудита"""
        try:
            with open("task_audit_report.json", "r", encoding="utf-8") as f:
                report = json.load(f)
            
            # Загружаем сотрудников
            for emp in report.get("employees", []):
                self.employees[emp["id"]] = emp
            
            # Загружаем задачи из отчета
            if "tasks" in report:
                self.tasks = report["tasks"]
            else:
                # Если задач нет в отчете, загружаем заново
                self.fetch_tasks()
            
            print(f"✅ Загружен отчет аудита: {len(self.employees)} сотрудников, {len(self.tasks)} задач")
            return True
            
        except FileNotFoundError:
            print("❌ Файл task_audit_report.json не найден. Сначала запустите task_management_audit.py")
            return False
        except Exception as e:
            print(f"❌ Ошибка загрузки отчета: {e}")
            return False
    
    def fetch_tasks(self) -> None:
        """Загружаем задачи заново"""
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
    
    def find_employee_by_name(self, name: str) -> Optional[Dict]:
        """Находим сотрудника по имени"""
        for emp in self.employees.values():
            if emp["name"].lower() == name.lower():
                return emp
        return None
    
    def fix_no_assignee_tasks(self) -> None:
        """Исправляем задачи без исполнителей"""
        print("\n🔧 Исправляем задачи без исполнителей...")
        
        # Находим задачи без исполнителей
        no_assignee_tasks = [t for t in self.tasks if not t["assignees"]]
        
        if not no_assignee_tasks:
            print("   ✅ Нет задач без исполнителей")
            return
        
        # Назначаем случайного сотрудника (можно улучшить логику)
        available_employees = [emp for emp in self.employees.values()]
        if not available_employees:
            print("   ⚠️ Нет доступных сотрудников для назначения")
            return
        
        for task in no_assignee_tasks[:10]:  # Ограничиваем количество для безопасности
            # Простая логика: назначаем первого доступного сотрудника
            employee = available_employees[0]
            
            try:
                self._assign_employee_to_task(task["id"], employee["id"])
                self.fixes_applied["assigned_employee"].append({
                    "task": task["title"],
                    "employee": employee["name"]
                })
                print(f"   ✅ Назначен {employee['name']} на задачу: {task['title']}")
                
            except Exception as e:
                self.errors.append(f"Ошибка назначения {employee['name']} на {task['title']}: {e}")
    
    def fix_unknown_assignees(self) -> None:
        """Исправляем неизвестных исполнителей"""
        print("\n🔧 Исправляем неизвестных исполнителей...")
        
        # Собираем всех неизвестных исполнителей
        unknown_assignees = set()
        for task in self.tasks:
            for assignee in task["assignees"]:
                if not self.find_employee_by_name(assignee):
                    unknown_assignees.add(assignee)
        
        if not unknown_assignees:
            print("   ✅ Нет неизвестных исполнителей")
            return
        
        print(f"   📋 Найдено {len(unknown_assignees)} неизвестных исполнителей:")
        for name in unknown_assignees:
            print(f"      - {name}")
        
        # Предлагаем создать сотрудников или исправить имена
        print("\n   💡 Рекомендации:")
        print("      1. Добавить этих людей в базу сотрудников")
        print("      2. Исправить опечатки в именах")
        print("      3. Удалить неактуальных исполнителей")
    
    def fix_no_status_tasks(self) -> None:
        """Исправляем задачи без статуса"""
        print("\n🔧 Исправляем задачи без статуса...")
        
        no_status_tasks = [t for t in self.tasks if t["status"] in ["Не указан", ""]]
        
        if not no_status_tasks:
            print("   ✅ Нет задач без статуса")
            return
        
        # Устанавливаем статус "To Do" для задач без статуса
        for task in no_status_tasks[:10]:  # Ограничиваем количество
            try:
                self._update_task_status(task["id"], "To Do")
                self.fixes_applied["set_status"].append({
                    "task": task["title"],
                    "status": "To Do"
                })
                print(f"   ✅ Установлен статус 'To Do' для: {task['title']}")
                
            except Exception as e:
                self.errors.append(f"Ошибка установки статуса для {task['title']}: {e}")
    
    def fix_overdue_tasks(self) -> None:
        """Исправляем просроченные задачи"""
        print("\n🔧 Исправляем просроченные задачи...")
        
        now = datetime.now().date()
        overdue_tasks = []
        
        for task in self.tasks:
            if task["deadline"]:
                try:
                    deadline = datetime.fromisoformat(task["deadline"].split("T")[0]).date()
                    if deadline < now and task["status"].lower() not in ["done", "выполнена", "завершена"]:
                        overdue_tasks.append((task, deadline))
                except:
                    pass
        
        if not overdue_tasks:
            print("   ✅ Нет просроченных задач")
            return
        
        print(f"   📋 Найдено {len(overdue_tasks)} просроченных задач:")
        for task, deadline in overdue_tasks[:5]:
            print(f"      - {task['title']} (до {deadline})")
        
        # Предлагаем действия
        print("\n   💡 Рекомендации:")
        print("      1. Пересмотреть дедлайны")
        print("      2. Перевести в статус 'В работе'")
        print("      3. Отметить как выполненные")
    
    def fix_old_todo_tasks(self) -> None:
        """Исправляем старые задачи в ToDo"""
        print("\n🔧 Исправляем старые задачи в ToDo...")
        
        now = datetime.now().date()
        old_todo_tasks = []
        
        for task in self.tasks:
            if task["status"].lower() in ["to do", "todo", "не начата"]:
                if task["created"]:
                    try:
                        created = datetime.fromisoformat(task["created"].split("T")[0]).date()
                        if created < now - timedelta(days=7):
                            old_todo_tasks.append((task, created))
                    except:
                        pass
        
        if not old_todo_tasks:
            print("   ✅ Нет старых задач в ToDo")
            return
        
        print(f"   📋 Найдено {len(old_todo_tasks)} старых задач в ToDo:")
        for task, created in old_todo_tasks[:5]:
            print(f"      - {task['title']} (создана {created})")
        
        # Переводим в статус "В работе"
        for task, created in old_todo_tasks[:5]:  # Ограничиваем количество
            try:
                self._update_task_status(task["id"], "In Progress")
                self.fixes_applied["moved_to_progress"].append({
                    "task": task["title"],
                    "created": str(created)
                })
                print(f"   ✅ Переведена в 'In Progress': {task['title']}")
                
            except Exception as e:
                self.errors.append(f"Ошибка перевода статуса для {task['title']}: {e}")
    
    def _assign_employee_to_task(self, task_id: str, employee_id: str) -> None:
        """Назначаем сотрудника на задачу"""
        url = f"https://api.notion.com/v1/pages/{task_id}"
        
        # Определяем поле для исполнителя
        assignee_field = None
        for field in ["Участники", "Assignee", "Исполнитель", "Responsible"]:
            if field in self.tasks[0]["properties"]:
                assignee_field = field
                break
        
        if not assignee_field:
            raise ValueError("Не найдено поле для назначения исполнителя")
        
        properties = {
            assignee_field: {
                "people": [{"id": employee_id}]
            }
        }
        
        response = requests.patch(url, headers=self.headers, json={"properties": properties})
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
    
    def _update_task_status(self, task_id: str, status: str) -> None:
        """Обновляем статус задачи"""
        url = f"https://api.notion.com/v1/pages/{task_id}"
        
        # Определяем поле для статуса
        status_field = None
        for field in ["Статус", "Status"]:
            if field in self.tasks[0]["properties"]:
                status_field = field
                break
        
        if not status_field:
            raise ValueError("Не найдено поле для статуса")
        
        properties = {
            status_field: {
                "select": {"name": status}
            }
        }
        
        response = requests.patch(url, headers=self.headers, json={"properties": properties})
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
    
    def generate_fix_report(self) -> None:
        """Генерируем отчет об исправлениях"""
        print("\n📊 ОТЧЕТ ОБ ИСПРАВЛЕНИЯХ")
        print("=" * 40)
        
        total_fixes = sum(len(fixes) for fixes in self.fixes_applied.values())
        print(f"✅ Всего применено исправлений: {total_fixes}")
        
        for fix_type, fixes in self.fixes_applied.items():
            if fixes:
                print(f"\n🔧 {fix_type.upper()}: {len(fixes)}")
                for fix in fixes[:3]:  # Показываем первые 3
                    if isinstance(fix, dict):
                        for key, value in fix.items():
                            print(f"   • {key}: {value}")
                    else:
                        print(f"   • {fix}")
        
        if self.errors:
            print(f"\n❌ ОШИБКИ ({len(self.errors)}):")
            for error in self.errors[:5]:
                print(f"   • {error}")
        
        # Сохраняем отчет
        report = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": dict(self.fixes_applied),
            "errors": self.errors,
            "total_fixes": total_fixes
        }
        
        with open("task_fixes_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Отчет об исправлениях сохранен в task_fixes_report.json")

def main():
    """Основная функция"""
    print("🔧 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ СИСТЕМЫ УПРАВЛЕНИЯ ЗАДАЧАМИ")
    print("=" * 60)
    
    fixer = TaskManagementFixer()
    
    if not fixer.load_audit_report():
        return 1
    
    try:
        # Применяем исправления
        fixer.fix_no_assignee_tasks()
        fixer.fix_unknown_assignees()
        fixer.fix_no_status_tasks()
        fixer.fix_overdue_tasks()
        fixer.fix_old_todo_tasks()
        
        # Генерируем отчет
        fixer.generate_fix_report()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 