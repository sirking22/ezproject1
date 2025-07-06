import os
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

class TodoWeekAnalyzer:
    """Анализ задач ToDo на текущую неделю"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.designers = {}
        self.todo_tasks = []
        self.week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        self.week_end = self.week_start + timedelta(days=6)
        
    def fetch_designers(self):
        """Загружаем дизайнеров из базы сотрудников"""
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
            
            # Извлекаем имя из поля Name (select)
            if "Name" in props and props["Name"].get("select"):
                name = props["Name"]["select"]["name"]
            
            # Проверяем, является ли дизайнером
            is_designer = False
            if "Name" in props and props["Name"].get("select"):
                name_value = props["Name"]["select"]["name"].lower()
                if "дизайн" in name_value:
                    is_designer = True
            
            if name and is_designer:
                self.designers[emp["id"]] = {
                    "name": name,
                    "id": emp["id"],
                    "tasks_count": 0,
                    "tasks": []
                }
        
        # Добавляем Марию Безродную как дизайнера (если её нет в базе)
        maria_found = any("мария" in d["name"].lower() for d in self.designers.values())
        if not maria_found:
            self.designers["maria_bezrodnaya"] = {
                "name": "Мария Безродная",
                "id": "maria_bezrodnaya",
                "tasks_count": 0,
                "tasks": []
            }
        
        print(f"✅ Найдено {len(self.designers)} дизайнеров")
        for designer in self.designers.values():
            print(f"   • {designer['name']}")
    
    def fetch_todo_tasks(self):
        """Загружаем задачи в статусе ToDo"""
        print(f"\n📋 Загружаем задачи ToDo на неделю {self.week_start} - {self.week_end}...")
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
            
            # Проверяем, что задача в ToDo и имеет исполнителя
            if (task_info["status"].lower() in ["to do", "todo", "не начата"] and 
                task_info["assignees"]):
                self.todo_tasks.append(task_info)
        
        print(f"✅ Найдено {len(self.todo_tasks)} задач ToDo с исполнителями")
    
    def _extract_task_info(self, task, props):
        """Извлекаем информацию о задаче"""
        title = ""
        for field in ["Задачи", "Задача", "Name", "Title", "Название"]:
            if field in props and props[field].get("title"):
                title = props[field]["title"][0]["plain_text"]
                break
        
        status = ""
        for field in [" Статус", "Статус", "Status"]:
            if field in props:
                s = props[field]
                if s.get("status"):
                    status = s["status"]["name"]
                elif s.get("select"):
                    status = s["select"]["name"]
                break
        
        assignees = []
        for field in ["Исполнитель", "Участники", "Assignee", "Responsible"]:
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
        """Анализируем нагрузку дизайнеров"""
        print(f"\n📊 АНАЛИЗ НАГРУЗКИ ДИЗАЙНЕРОВ")
        print("=" * 60)
        
        # Распределяем задачи по дизайнерам
        for task in self.todo_tasks:
            for assignee_name in task["assignees"]:
                # Ищем дизайнера по имени
                for designer in self.designers.values():
                    if designer["name"].lower() == assignee_name.lower():
                        designer["tasks_count"] += 1
                        designer["tasks"].append(task)
                        break
        
        # Выводим статистику
        print(f"\n👥 НАГРУЗКА ПО ДИЗАЙНЕРАМ:")
        total_tasks = 0
        for designer in self.designers.values():
            print(f"\n🎨 {designer['name']}: {designer['tasks_count']} задач")
            total_tasks += designer["tasks_count"]
            
            if designer["tasks"]:
                print("   Задачи:")
                for task in designer["tasks"][:5]:  # Показываем первые 5
                    deadline_info = f" (до {task['deadline']})" if task['deadline'] else ""
                    priority_info = f" [{task['priority']}]" if task['priority'] else ""
                    print(f"   • {task['title'][:50]}{deadline_info}{priority_info}")
                if len(designer["tasks"]) > 5:
                    print(f"   ... и еще {len(designer['tasks']) - 5} задач")
        
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Всего задач ToDo: {len(self.todo_tasks)}")
        print(f"   • Распределено дизайнерам: {total_tasks}")
        print(f"   • Не распределено: {len(self.todo_tasks) - total_tasks}")
        
        # Анализ приоритетов
        priorities = defaultdict(int)
        for task in self.todo_tasks:
            priorities[task["priority"] or "Не указан"] += 1
        
        print(f"\n🎯 ПРИОРИТЕТЫ:")
        for priority, count in priorities.items():
            print(f"   • {priority}: {count}")
        
        # Анализ дедлайнов
        deadlines = defaultdict(int)
        for task in self.todo_tasks:
            if task["deadline"]:
                try:
                    deadline_date = datetime.fromisoformat(task["deadline"].split("T")[0]).date()
                    if deadline_date <= self.week_end:
                        deadlines["На этой неделе"] += 1
                    else:
                        deadlines["После недели"] += 1
                except:
                    deadlines["Некорректная дата"] += 1
            else:
                deadlines["Без дедлайна"] += 1
        
        print(f"\n📅 ДЕДЛАЙНЫ:")
        for deadline_type, count in deadlines.items():
            print(f"   • {deadline_type}: {count}")
    
    def suggest_redistribution(self):
        """Предлагаем перераспределение задач"""
        print(f"\n🔄 ПРЕДЛОЖЕНИЯ ПО ПЕРЕРАСПРЕДЕЛЕНИЮ:")
        print("=" * 50)
        
        # Находим дизайнеров с максимальной и минимальной нагрузкой
        designers_list = list(self.designers.values())
        designers_list.sort(key=lambda x: x["tasks_count"], reverse=True)
        
        if len(designers_list) >= 2:
            max_load = designers_list[0]
            min_load = designers_list[-1]
            
            print(f"   🎯 Максимальная нагрузка: {max_load['name']} ({max_load['tasks_count']} задач)")
            print(f"   🎯 Минимальная нагрузка: {min_load['name']} ({min_load['tasks_count']} задач)")
            
            if max_load["tasks_count"] - min_load["tasks_count"] > 2:
                print(f"\n   💡 РЕКОМЕНДАЦИЯ: Передать {max_load['name']} → {min_load['name']}")
                
                # Предлагаем конкретные задачи для передачи
                tasks_to_transfer = max_load["tasks"][:2]  # Первые 2 задачи
                print(f"   📋 Задачи для передачи:")
                for task in tasks_to_transfer:
                    print(f"      • {task['title'][:40]}")
        
        # Задачи без дизайнера
        unassigned_tasks = []
        for task in self.todo_tasks:
            has_designer = False
            for assignee_name in task["assignees"]:
                for designer in self.designers.values():
                    if designer["name"].lower() == assignee_name.lower():
                        has_designer = True
                        break
                if has_designer:
                    break
            if not has_designer:
                unassigned_tasks.append(task)
        
        if unassigned_tasks:
            print(f"\n   ⚠️ Задачи без дизайнера ({len(unassigned_tasks)}):")
            for task in unassigned_tasks[:3]:
                print(f"      • {task['title'][:40]} → {', '.join(task['assignees'])}")
    
    def generate_weekly_report(self):
        """Генерируем отчет на неделю"""
        print(f"\n📋 ОТЧЕТ НА НЕДЕЛЮ {self.week_start} - {self.week_end}")
        print("=" * 60)
        
        print(f"\n🎯 ЦЕЛИ НА НЕДЕЛЮ:")
        print(f"   • Завершить {len(self.todo_tasks)} задач ToDo")
        print(f"   • Равномерно распределить нагрузку между {len(self.designers)} дизайнерами")
        
        print(f"\n📊 МЕТРИКИ:")
        avg_tasks = len(self.todo_tasks) / len(self.designers) if self.designers else 0
        print(f"   • Средняя нагрузка на дизайнера: {avg_tasks:.1f} задач")
        
        # Находим дизайнера с максимальной нагрузкой
        max_tasks = max([d["tasks_count"] for d in self.designers.values()]) if self.designers else 0
        print(f"   • Максимальная нагрузка: {max_tasks} задач")
        
        print(f"\n✅ КРИТЕРИИ УСПЕХА:")
        print(f"   • Все задачи ToDo выполнены к концу недели")
        print(f"   • Нагрузка распределена равномерно (±2 задачи)")
        print(f"   • Нет просроченных задач")

def main():
    """Основная функция"""
    print("🎨 АНАЛИЗ ЗАДАЧ TODO НА НЕДЕЛЮ")
    print("=" * 50)
    
    analyzer = TodoWeekAnalyzer()
    
    try:
        analyzer.fetch_designers()
        analyzer.fetch_todo_tasks()
        analyzer.analyze_workload()
        analyzer.suggest_redistribution()
        analyzer.generate_weekly_report()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 