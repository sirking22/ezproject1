import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID", "9c5f4269d61449b6a7485579a3c21da3")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

class CorrectTodoAnalyzer:
    """Правильный анализ только задач ToDo для дизайнеров"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.designers = {
            "Мария Безродная": {"tasks": [], "count": 0},
            "Arsentiy": {"tasks": [], "count": 0},  # Арт-директор
            "Виктория Владимировна": {"tasks": [], "count": 0},
            "Александр Трусов": {"tasks": [], "count": 0},
            "Анна Когут": {"tasks": [], "count": 0}
        }
        self.todo_tasks = []
        self.week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        self.week_end = self.week_start + timedelta(days=6)
        
    def load_todo_tasks(self):
        """Загружаем ТОЛЬКО задачи в статусе ToDo"""
        print(f"📋 Загружаем задачи в статусе ToDo на неделю {self.week_start} - {self.week_end}...")
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
        
        print(f"📊 Всего задач в базе: {len(results)}")
        
        # Фильтруем только ToDo задачи
        for task in results:
            props = task.get("properties", {})
            task_info = self._extract_task_info(task, props)
            
            # Проверяем статус ToDo
            status = task_info["status"].lower()
            if status in ["to do", "todo", "не начата"]:
                self.todo_tasks.append(task_info)
        
        print(f"✅ Найдено задач в статусе ToDo: {len(self.todo_tasks)}")
    
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
    
    def analyze_designer_workload(self):
        """Анализируем нагрузку дизайнеров"""
        print(f"\n🎨 АНАЛИЗ НАГРУЗКИ ДИЗАЙНЕРОВ (ТОЛЬКО TODO)")
        print("=" * 70)
        
        # Распределяем задачи по дизайнерам
        for task in self.todo_tasks:
            for assignee_name in task["assignees"]:
                # Исключаем Account (общий рабочий аккаунт)
                if assignee_name.lower() == "account":
                    continue
                
                # Проверяем, является ли дизайнером
                if assignee_name in self.designers:
                    self.designers[assignee_name]["tasks"].append(task)
                    self.designers[assignee_name]["count"] += 1
                else:
                    # Если не дизайнер, добавляем в "другие"
                    if "другие" not in self.designers:
                        self.designers["другие"] = {"tasks": [], "count": 0}
                    self.designers["другие"]["tasks"].append(task)
                    self.designers["другие"]["count"] += 1
        
        # Выводим статистику
        print(f"\n👥 НАГРУЗКА ПО ДИЗАЙНЕРАМ:")
        total_designer_tasks = 0
        
        for designer_name, data in self.designers.items():
            if data["count"] > 0:
                print(f"\n🎨 {designer_name}: {data['count']} задач ToDo")
                total_designer_tasks += data["count"]
                
                if data["tasks"]:
                    print("   Примеры задач:")
                    for task in data["tasks"][:3]:  # Показываем первые 3
                        deadline_info = f" (до {task['deadline']})" if task['deadline'] else ""
                        priority_info = f" [{task['priority']}]" if task['priority'] else ""
                        print(f"   • {task['title'][:50]}{deadline_info}{priority_info}")
                    if len(data["tasks"]) > 3:
                        print(f"   ... и еще {len(data['tasks']) - 3} задач")
        
        # Общая статистика
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Всего задач ToDo: {len(self.todo_tasks)}")
        print(f"   • У дизайнеров: {total_designer_tasks}")
        print(f"   • У других: {len(self.todo_tasks) - total_designer_tasks}")
        
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
    
    def generate_recommendations(self):
        """Генерируем рекомендации"""
        print(f"\n💡 РЕКОМЕНДАЦИИ ПО РАСПРЕДЕЛЕНИЮ")
        print("=" * 50)
        
        # Находим дизайнеров с задачами
        active_designers = {name: data for name, data in self.designers.items() if data["count"] > 0}
        
        if len(active_designers) > 1:
            # Сортируем по количеству задач
            sorted_designers = sorted(active_designers.items(), key=lambda x: x[1]["count"], reverse=True)
            
            max_load = sorted_designers[0]
            min_load = sorted_designers[-1]
            
            print(f"📊 АНАЛИЗ НАГРУЗКИ:")
            print(f"   • Максимальная нагрузка: {max_load[0]} ({max_load[1]['count']} задач)")
            print(f"   • Минимальная нагрузка: {min_load[0]} ({min_load[1]['count']} задач)")
            
            if max_load[1]["count"] - min_load[1]["count"] > 5:
                print(f"\n🔄 РЕКОМЕНДАЦИЯ ПО ПЕРЕРАСПРЕДЕЛЕНИЮ:")
                print(f"   • Передать {max_load[0]} → {min_load[0]}")
                print(f"   • Количество задач для передачи: {min(10, max_load[1]['count'] - min_load[1]['count'])}")
        
        # Рекомендации по приоритизации
        low_priority_count = sum(1 for task in self.todo_tasks if not task["priority"] or task["priority"] == "Не указан")
        if low_priority_count > 0:
            print(f"\n🎯 ПРИОРИТИЗАЦИЯ:")
            print(f"   • {low_priority_count} задач без приоритета")
            print(f"   • Рекомендуется установить приоритеты")
        
        # Рекомендации по дедлайнам
        overdue_count = 0
        today = datetime.now().date()
        for task in self.todo_tasks:
            if task["deadline"]:
                try:
                    deadline_date = datetime.fromisoformat(task["deadline"].split("T")[0]).date()
                    if deadline_date < today:
                        overdue_count += 1
                except:
                    pass
        
        if overdue_count > 0:
            print(f"\n⏰ ПРОСРОЧЕННЫЕ ЗАДАЧИ:")
            print(f"   • {overdue_count} просроченных задач")
            print(f"   • Рекомендуется перенести на следующую неделю")
    
    def create_weekly_plan(self):
        """Создаем план на неделю"""
        print(f"\n📋 ПЛАН НА НЕДЕЛЮ {self.week_start} - {self.week_end}")
        print("=" * 60)
        
        total_todo = len(self.todo_tasks)
        designer_tasks = sum(data["count"] for data in self.designers.values())
        
        print(f"🎯 ЦЕЛИ НА НЕДЕЛЮ:")
        print(f"   • Завершить {total_todo} задач ToDo")
        print(f"   • Равномерно распределить {designer_tasks} задач между дизайнерами")
        print(f"   • Установить приоритеты для всех задач")
        
        print(f"\n📊 МЕТРИКИ:")
        if designer_tasks > 0:
            avg_tasks = designer_tasks / len([d for d in self.designers.values() if d["count"] > 0])
            print(f"   • Средняя нагрузка на дизайнера: {avg_tasks:.1f} задач")
        
        max_tasks = max([d["count"] for d in self.designers.values()]) if self.designers else 0
        print(f"   • Максимальная нагрузка: {max_tasks} задач")
        
        print(f"\n✅ КРИТЕРИИ УСПЕХА:")
        print(f"   • Все задачи ToDo выполнены к концу недели")
        print(f"   • Нагрузка распределена равномерно (±3 задачи)")
        print(f"   • Все задачи имеют приоритет")

def main():
    """Основная функция"""
    print("🎨 ПРАВИЛЬНЫЙ АНАЛИЗ ЗАДАЧ TODO ДЛЯ ДИЗАЙНЕРОВ")
    print("=" * 70)
    
    analyzer = CorrectTodoAnalyzer()
    
    try:
        analyzer.load_todo_tasks()
        analyzer.analyze_designer_workload()
        analyzer.generate_recommendations()
        analyzer.create_weekly_plan()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 