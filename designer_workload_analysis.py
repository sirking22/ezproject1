import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID", "9c5f4269d61449b6a7485579a3c21da3")
TEAMS_DB_ID = os.getenv("NOTION_TEAMS_DB_ID", "1d6ace03d9ff805787b9")

if not NOTION_TOKEN:
    raise RuntimeError("NOTION_TOKEN должен быть задан в переменных окружения")

class DesignerWorkloadAnalyzer:
    """Детальный анализ нагрузки дизайнеров"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.designers = {}
        self.todo_tasks = []
        self.other_assignees = defaultdict(list)
        self.week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        self.week_end = self.week_start + timedelta(days=6)
        
    def load_designers(self):
        """Загружаем дизайнеров"""
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
            if "Name" in props and props["Name"].get("select"):
                name = props["Name"]["select"]["name"]
                name_lower = name.lower()
                
                # Проверяем, является ли дизайнером
                if "дизайн" in name_lower:
                    self.designers[emp["id"]] = {
                        "name": name,
                        "id": emp["id"],
                        "tasks_count": 0,
                        "tasks": []
                    }
        
        # Добавляем Марию Безродную
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
    
    def load_todo_tasks(self):
        """Загружаем задачи ToDo"""
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
            
            if task_info["status"].lower() in ["to do", "todo", "не начата"]:
                self.todo_tasks.append(task_info)
        
        print(f"✅ Найдено {len(self.todo_tasks)} задач ToDo")
    
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
        """Анализируем нагрузку"""
        print(f"\n📊 ДЕТАЛЬНЫЙ АНАЛИЗ НАГРУЗКИ")
        print("=" * 60)
        
        # Распределяем задачи
        for task in self.todo_tasks:
            assigned_to_designer = False
            
            for assignee_name in task["assignees"]:
                # Проверяем, назначена ли на дизайнера
                for designer in self.designers.values():
                    if designer["name"].lower() == assignee_name.lower():
                        designer["tasks_count"] += 1
                        designer["tasks"].append(task)
                        assigned_to_designer = True
                        break
                
                if not assigned_to_designer:
                    # Задача назначена на не-дизайнера
                    self.other_assignees[assignee_name].append(task)
        
        # Выводим статистику по дизайнерам
        print(f"\n🎨 НАГРУЗКА ДИЗАЙНЕРОВ:")
        total_designer_tasks = 0
        for designer in self.designers.values():
            print(f"\n👤 {designer['name']}: {designer['tasks_count']} задач")
            total_designer_tasks += designer["tasks_count"]
            
            if designer["tasks"]:
                # Анализ приоритетов
                priorities = defaultdict(int)
                for task in designer["tasks"]:
                    priorities[task["priority"] or "Не указан"] += 1
                
                print(f"   Приоритеты:")
                for priority, count in priorities.items():
                    print(f"     • {priority}: {count}")
                
                # Анализ дедлайнов
                deadlines = defaultdict(int)
                for task in designer["tasks"]:
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
                
                print(f"   Дедлайны:")
                for deadline_type, count in deadlines.items():
                    print(f"     • {deadline_type}: {count}")
        
        # Выводим статистику по не-дизайнерам
        print(f"\n👥 ЗАДАЧИ НЕ-ДИЗАЙНЕРОВ:")
        total_other_tasks = 0
        for assignee, tasks in sorted(self.other_assignees.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"   • {assignee}: {len(tasks)} задач")
            total_other_tasks += len(tasks)
        
        # Общая статистика
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   • Всего задач ToDo: {len(self.todo_tasks)}")
        print(f"   • У дизайнеров: {total_designer_tasks}")
        print(f"   • У не-дизайнеров: {total_other_tasks}")
        print(f"   • Без исполнителя: {len(self.todo_tasks) - total_designer_tasks - total_other_tasks}")
    
    def generate_recommendations(self):
        """Генерируем рекомендации"""
        print(f"\n💡 РЕКОМЕНДАЦИИ ПО РАСПРЕДЕЛЕНИЮ")
        print("=" * 60)
        
        # Анализируем перегрузку
        if self.designers:
            max_tasks = max(d["tasks_count"] for d in self.designers.values())
            avg_tasks = sum(d["tasks_count"] for d in self.designers.values()) / len(self.designers)
            
            print(f"📊 АНАЛИЗ НАГРУЗКИ:")
            print(f"   • Максимальная нагрузка: {max_tasks} задач")
            print(f"   • Средняя нагрузка: {avg_tasks:.1f} задач")
            print(f"   • Разница: {max_tasks - avg_tasks:.1f} задач")
            
            if max_tasks > avg_tasks * 2:
                print(f"   ⚠️ КРИТИЧЕСКАЯ ПЕРЕГРУЗКА!")
            elif max_tasks > avg_tasks * 1.5:
                print(f"   ⚠️ СИЛЬНАЯ ПЕРЕГРУЗКА!")
            elif max_tasks > avg_tasks * 1.2:
                print(f"   ⚠️ УМЕРЕННАЯ ПЕРЕГРУЗКА!")
            else:
                print(f"   ✅ НАГРУЗКА РАВНОМЕРНАЯ")
        
        # Рекомендации по перераспределению
        print(f"\n🔄 РЕКОМЕНДАЦИИ:")
        
        # 1. Задачи от не-дизайнеров к дизайнерам
        design_related_tasks = []
        for assignee, tasks in self.other_assignees.items():
            for task in tasks:
                # Определяем, связана ли задача с дизайном
                title_lower = task["title"].lower()
                design_keywords = ["дизайн", "макет", "графика", "иллюстрация", "фото", "изображение", "визуал"]
                if any(keyword in title_lower for keyword in design_keywords):
                    design_related_tasks.append((task, assignee))
        
        if design_related_tasks:
            print(f"   1. 🎨 Дизайн-задачи у не-дизайнеров ({len(design_related_tasks)}):")
            for task, assignee in design_related_tasks[:5]:
                print(f"      • {task['title'][:40]} → {assignee}")
            if len(design_related_tasks) > 5:
                print(f"      ... и еще {len(design_related_tasks) - 5} задач")
        
        # 2. Распределение между дизайнерами
        if len(self.designers) > 1:
            designers_list = list(self.designers.values())
            designers_list.sort(key=lambda x: x["tasks_count"], reverse=True)
            
            overloaded = designers_list[0]
            underloaded = designers_list[-1]
            
            if overloaded["tasks_count"] - underloaded["tasks_count"] > 10:
                print(f"   2. ⚖️ Перераспределение между дизайнерами:")
                print(f"      • {overloaded['name']} → {underloaded['name']}")
                print(f"      • Передать {min(20, overloaded['tasks_count'] - underloaded['tasks_count'])} задач")
        
        # 3. Приоритизация
        low_priority_tasks = []
        for designer in self.designers.values():
            for task in designer["tasks"]:
                if not task["priority"] or task["priority"] == "Не указан":
                    low_priority_tasks.append((task, designer["name"]))
        
        if low_priority_tasks:
            print(f"   3. 🎯 Приоритизация:")
            print(f"      • {len(low_priority_tasks)} задач без приоритета")
            print(f"      • Рекомендуется установить приоритеты")
        
        # 4. Дедлайны
        overdue_tasks = []
        today = datetime.now().date()
        for designer in self.designers.values():
            for task in designer["tasks"]:
                if task["deadline"]:
                    try:
                        deadline_date = datetime.fromisoformat(task["deadline"].split("T")[0]).date()
                        if deadline_date < today:
                            overdue_tasks.append((task, designer["name"]))
                    except:
                        pass
        
        if overdue_tasks:
            print(f"   4. ⏰ Просроченные задачи:")
            print(f"      • {len(overdue_tasks)} просроченных задач")
            for task, designer in overdue_tasks[:3]:
                print(f"      • {task['title'][:40]} → {designer}")
    
    def create_action_plan(self):
        """Создаем план действий"""
        print(f"\n📋 ПЛАН ДЕЙСТВИЙ НА НЕДЕЛЮ")
        print("=" * 50)
        
        print(f"🎯 ЦЕЛИ:")
        print(f"   • Равномерно распределить {len(self.todo_tasks)} задач")
        print(f"   • Снизить нагрузку на перегруженных дизайнеров")
        print(f"   • Установить приоритеты для всех задач")
        
        print(f"\n📅 РАСПИСАНИЕ:")
        print(f"   Понедельник: Анализ и планирование")
        print(f"   Вторник-Среда: Перераспределение задач")
        print(f"   Четверг: Установка приоритетов")
        print(f"   Пятница: Контроль и корректировка")
        
        print(f"\n✅ КРИТЕРИИ УСПЕХА:")
        print(f"   • Нагрузка ±20% между дизайнерами")
        print(f"   • Все задачи имеют приоритет")
        print(f"   • Нет просроченных задач")

def main():
    """Основная функция"""
    print("🎨 ДЕТАЛЬНЫЙ АНАЛИЗ НАГРУЗКИ ДИЗАЙНЕРОВ")
    print("=" * 60)
    
    analyzer = DesignerWorkloadAnalyzer()
    
    try:
        analyzer.load_designers()
        analyzer.load_todo_tasks()
        analyzer.analyze_workload()
        analyzer.generate_recommendations()
        analyzer.create_action_plan()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 