import os
import sys
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")
TEAMS_DB_ID = os.getenv("NOTION_TEAMS_DB_ID")

if not NOTION_TOKEN or not TASKS_DB_ID:
    raise RuntimeError("NOTION_TOKEN и NOTION_TASKS_DB_ID должны быть заданы в переменных окружения")

class DesignerTaskManager:
    """Главный менеджер задач дизайнеров"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.designers = {}
        self.tasks = {}
        self.week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        self.week_end = self.week_start + timedelta(days=6)
        
    def show_menu(self):
        """Показываем главное меню"""
        print("\n🎨 МЕНЕДЖЕР ЗАДАЧ ДИЗАЙНЕРОВ")
        print("=" * 50)
        print("1. 📊 Анализ текущей нагрузки")
        print("2. 📋 Список задач ToDo на неделю")
        print("3. 🔄 Перераспределение задач")
        print("4. 📈 Отчет по дизайнерам")
        print("5. ⚡ Быстрый обзор")
        print("6. 🔧 Настройки")
        print("0. ❌ Выход")
        print("-" * 50)
        
        choice = input("Выберите действие (0-6): ").strip()
        return choice
    
    def quick_overview(self):
        """Быстрый обзор ситуации"""
        print("\n⚡ БЫСТРЫЙ ОБЗОР")
        print("=" * 40)
        
        # Загружаем данные
        self.load_designers()
        self.load_tasks()
        
        # Анализируем
        todo_tasks = [t for t in self.tasks.values() if t["status"].lower() in ["to do", "todo", "не начата"]]
        assigned_tasks = [t for t in todo_tasks if t["assignees"]]
        
        print(f"📊 СТАТИСТИКА:")
        print(f"   • Дизайнеров: {len(self.designers)}")
        print(f"   • Задач ToDo: {len(todo_tasks)}")
        print(f"   • С исполнителями: {len(assigned_tasks)}")
        print(f"   • Без исполнителей: {len(todo_tasks) - len(assigned_tasks)}")
        
        # Нагрузка по дизайнерам
        workload = defaultdict(int)
        for task in assigned_tasks:
            for assignee in task["assignees"]:
                for designer in self.designers.values():
                    if designer["name"].lower() == assignee.lower():
                        workload[designer["name"]] += 1
                        break
        
        if workload:
            print(f"\n👥 НАГРУЗКА:")
            for designer, count in sorted(workload.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {designer}: {count} задач")
        
        # Проблемы
        issues = []
        if len(todo_tasks) - len(assigned_tasks) > 0:
            issues.append(f"❌ {len(todo_tasks) - len(assigned_tasks)} задач без исполнителя")
        
        if workload:
            max_load = max(workload.values())
            min_load = min(workload.values())
            if max_load - min_load > 3:
                issues.append(f"⚠️ Неравномерная нагрузка ({max_load} vs {min_load})")
        
        if issues:
            print(f"\n🚨 ПРОБЛЕМЫ:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print(f"\n✅ Все в порядке!")
    
    def load_designers(self):
        """Загружаем дизайнеров"""
        if self.designers:  # Уже загружены
            return
            
        print("👥 Загружаем дизайнеров...")
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
            name = None
            for field in ["Name", "Имя", "ФИО", "Title"]:
                if field in props and props[field].get("title"):
                    name = props[field]["title"][0]["plain_text"]
                    break
            
            # Проверяем, является ли дизайнером
            is_designer = False
            for field in ["Должность", "Position", "Роль"]:
                if field in props:
                    role_obj = props[field]
                    if role_obj.get("select") and "дизайн" in role_obj["select"]["name"].lower():
                        is_designer = True
                        break
                    elif role_obj.get("rich_text"):
                        role_text = " ".join([t["plain_text"] for t in role_obj["rich_text"]])
                        if "дизайн" in role_text.lower():
                            is_designer = True
                            break
            
            if name and is_designer:
                self.designers[emp["id"]] = {
                    "name": name,
                    "id": emp["id"],
                    "tasks_count": 0,
                    "tasks": []
                }
        
        print(f"✅ Загружено {len(self.designers)} дизайнеров")
    
    def load_tasks(self):
        """Загружаем задачи"""
        if self.tasks:  # Уже загружены
            return
            
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
            task_info = self._extract_task_info(task, props)
            self.tasks[task["id"]] = task_info
        
        print(f"✅ Загружено {len(self.tasks)} задач")
    
    def _extract_task_info(self, task, props):
        """Извлекаем информацию о задаче"""
        title = ""
        for field in ["Задача", "Name", "Title", "Название"]:
            if field in props and props[field].get("title"):
                title = props[field]["title"][0]["plain_text"]
                break
        
        status = ""
        for field in ["Статус", "Status"]:
            if field in props:
                s = props[field]
                if s.get("status"):
                    status = s["status"]["name"]
                elif s.get("select"):
                    status = s["select"]["name"]
                break
        
        assignees = []
        for field in ["Участники", "Assignee", "Исполнитель", "Responsible"]:
            if field in props and props[field].get("people"):
                assignees = [p.get("name", "Без имени") for p in props[field]["people"]]
                break
        
        deadline = ""
        for field in ["Дедлайн", "Due Date", "Дата", "Deadline"]:
            if field in props and props[field].get("date"):
                deadline = props[field]["date"]["start"]
                break
        
        priority = ""
        for field in ["Приоритет", "Priority"]:
            if field in props:
                p = props[field]
                if p.get("select"):
                    priority = p["select"]["name"]
                break
        
        return {
            "id": task["id"],
            "title": title,
            "status": status,
            "assignees": assignees,
            "deadline": deadline,
            "priority": priority,
            "properties": props
        }
    
    def analyze_workload(self):
        """Анализ текущей нагрузки"""
        print("\n📊 АНАЛИЗ ТЕКУЩЕЙ НАГРУЗКИ")
        print("=" * 50)
        
        self.load_designers()
        self.load_tasks()
        
        # Фильтруем задачи ToDo
        todo_tasks = [t for t in self.tasks.values() if t["status"].lower() in ["to do", "todo", "не начата"]]
        
        # Распределяем по дизайнерам
        for task in todo_tasks:
            for assignee in task["assignees"]:
                for designer in self.designers.values():
                    if designer["name"].lower() == assignee.lower():
                        designer["tasks_count"] += 1
                        designer["tasks"].append(task)
                        break
        
        # Выводим статистику
        print(f"\n👥 НАГРУЗКА ПО ДИЗАЙНЕРАМ:")
        total_assigned = 0
        for designer in self.designers.values():
            print(f"\n🎨 {designer['name']}: {designer['tasks_count']} задач")
            total_assigned += designer["tasks_count"]
            
            if designer["tasks"]:
                print("   Задачи:")
                for task in designer["tasks"][:3]:  # Показываем первые 3
                    deadline_info = f" (до {task['deadline']})" if task['deadline'] else ""
                    priority_info = f" [{task['priority']}]" if task['priority'] else ""
                    print(f"   • {task['title'][:40]}{deadline_info}{priority_info}")
                if len(designer["tasks"]) > 3:
                    print(f"   ... и еще {len(designer['tasks']) - 3} задач")
        
        # Общая статистика
        unassigned = len([t for t in todo_tasks if not t["assignees"]])
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Всего задач ToDo: {len(todo_tasks)}")
        print(f"   • Распределено дизайнерам: {total_assigned}")
        print(f"   • Без исполнителя: {unassigned}")
        
        # Рекомендации
        if unassigned > 0:
            print(f"\n💡 РЕКОМЕНДАЦИИ:")
            print(f"   • Назначить исполнителей для {unassigned} задач")
        
        if self.designers:
            avg_load = total_assigned / len(self.designers)
            max_load = max(d["tasks_count"] for d in self.designers.values())
            if max_load > avg_load * 1.5:
                print(f"   • Перераспределить нагрузку (максимум: {max_load}, среднее: {avg_load:.1f})")
    
    def show_todo_list(self):
        """Показываем список задач ToDo на неделю"""
        print(f"\n📋 ЗАДАЧИ TODO НА НЕДЕЛЮ {self.week_start} - {self.week_end}")
        print("=" * 70)
        
        self.load_tasks()
        
        todo_tasks = [t for t in self.tasks.values() if t["status"].lower() in ["to do", "todo", "не начата"]]
        
        if not todo_tasks:
            print("✅ Нет задач в статусе ToDo")
            return
        
        # Группируем по исполнителям
        by_assignee = defaultdict(list)
        for task in todo_tasks:
            if task["assignees"]:
                for assignee in task["assignees"]:
                    by_assignee[assignee].append(task)
            else:
                by_assignee["Без исполнителя"].append(task)
        
        # Выводим по группам
        for assignee, tasks in by_assignee.items():
            print(f"\n👤 {assignee} ({len(tasks)} задач):")
            for task in tasks:
                deadline_info = f" (до {task['deadline']})" if task['deadline'] else ""
                priority_info = f" [{task['priority']}]" if task['priority'] else ""
                print(f"   • {task['title'][:50]}{deadline_info}{priority_info}")
    
    def redistribute_tasks(self):
        """Перераспределение задач"""
        print("\n🔄 ПЕРЕРАСПРЕДЕЛЕНИЕ ЗАДАЧ")
        print("=" * 40)
        
        # Запускаем скрипт перераспределения
        try:
            import redistribute_tasks
            redistributor = redistribute_tasks.TaskRedistributor()
            redistributor.fetch_designers()
            redistributor.fetch_todo_tasks()
            target_avg = redistributor.analyze_current_distribution()
            redistributor.plan_redistribution(target_avg)
            redistributor.execute_redistribution(dry_run=True)
            
            print(f"\n💡 Для выполнения изменений запустите:")
            print(f"   python redistribute_tasks.py --execute")
            
        except ImportError:
            print("❌ Модуль redistribute_tasks не найден")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def generate_report(self):
        """Генерируем отчет по дизайнерам"""
        print(f"\n📈 ОТЧЕТ ПО ДИЗАЙНЕРАМ")
        print("=" * 40)
        
        self.load_designers()
        self.load_tasks()
        
        # Анализируем все задачи дизайнеров
        designer_stats = defaultdict(lambda: {
            "todo": 0, "in_progress": 0, "done": 0, "overdue": 0, "total": 0
        })
        
        now = datetime.now().date()
        
        for task in self.tasks.values():
            for assignee in task["assignees"]:
                for designer in self.designers.values():
                    if designer["name"].lower() == assignee.lower():
                        stats = designer_stats[designer["name"]]
                        stats["total"] += 1
                        
                        status = task["status"].lower()
                        if status in ["to do", "todo", "не начата"]:
                            stats["todo"] += 1
                        elif status in ["in progress", "в работе"]:
                            stats["in_progress"] += 1
                        elif status in ["done", "выполнена", "завершена"]:
                            stats["done"] += 1
                        
                        # Проверяем просрочку
                        if task["deadline"]:
                            try:
                                deadline = datetime.fromisoformat(task["deadline"].split("T")[0]).date()
                                if deadline < now and status not in ["done", "выполнена", "завершена"]:
                                    stats["overdue"] += 1
                            except:
                                pass
                        break
        
        # Выводим отчет
        for designer_name, stats in designer_stats.items():
            print(f"\n🎨 {designer_name}:")
            print(f"   • Всего задач: {stats['total']}")
            print(f"   • ToDo: {stats['todo']}")
            print(f"   • В работе: {stats['in_progress']}")
            print(f"   • Выполнено: {stats['done']}")
            if stats['overdue'] > 0:
                print(f"   • Просрочено: {stats['overdue']} ⚠️")
            
            # Эффективность
            if stats['total'] > 0:
                efficiency = (stats['done'] / stats['total']) * 100
                print(f"   • Эффективность: {efficiency:.1f}%")
    
    def settings(self):
        """Настройки"""
        print("\n🔧 НАСТРОЙКИ")
        print("=" * 30)
        print("1. Проверить переменные окружения")
        print("2. Обновить данные")
        print("0. Назад")
        
        choice = input("Выберите (0-2): ").strip()
        
        if choice == "1":
            self.check_environment()
        elif choice == "2":
            self.designers = {}  # Сброс кэша
            self.tasks = {}
            print("✅ Кэш очищен, данные будут загружены заново")
    
    def check_environment(self):
        """Проверка переменных окружения"""
        print("\n🔍 ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
        print("=" * 40)
        
        env_vars = {
            "NOTION_TOKEN": NOTION_TOKEN,
            "NOTION_TASKS_DB_ID": TASKS_DB_ID,
            "NOTION_TEAMS_DB_ID": TEAMS_DB_ID,
        }
        
        for var, value in env_vars.items():
            status = "✅ УСТАНОВЛЕНА" if value else "❌ ОТСУТСТВУЕТ"
            print(f"   {var}: {status}")
            if value:
                print(f"      Значение: {value[:20]}..." if len(value) > 20 else f"      Значение: {value}")

def main():
    """Основная функция"""
    print("🎨 МЕНЕДЖЕР ЗАДАЧ ДИЗАЙНЕРОВ")
    print("=" * 50)
    
    manager = DesignerTaskManager()
    
    while True:
        try:
            choice = manager.show_menu()
            
            if choice == "0":
                print("👋 До свидания!")
                break
            elif choice == "1":
                manager.analyze_workload()
            elif choice == "2":
                manager.show_todo_list()
            elif choice == "3":
                manager.redistribute_tasks()
            elif choice == "4":
                manager.generate_report()
            elif choice == "5":
                manager.quick_overview()
            elif choice == "6":
                manager.settings()
            else:
                print("❌ Неверный выбор")
            
            input("\nНажмите Enter для продолжения...")
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            input("Нажмите Enter для продолжения...")
    
    return 0

if __name__ == "__main__":
    exit(main()) 