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

class TaskRedistributor:
    """Автоматическое перераспределение задач между дизайнерами"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.designers = {}
        self.todo_tasks = []
        self.redistributions = []
        
    def fetch_designers(self):
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
        
        print(f"✅ Найдено {len(self.designers)} дизайнеров")
    
    def fetch_todo_tasks(self):
        """Загружаем задачи ToDo"""
        print("📋 Загружаем задачи ToDo...")
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
            "priority": priority,
            "properties": props
        }
    
    def analyze_current_distribution(self):
        """Анализируем текущее распределение"""
        print("\n📊 АНАЛИЗ ТЕКУЩЕГО РАСПРЕДЕЛЕНИЯ")
        print("=" * 50)
        
        # Распределяем задачи по дизайнерам
        for task in self.todo_tasks:
            for assignee_name in task["assignees"]:
                for designer in self.designers.values():
                    if designer["name"].lower() == assignee_name.lower():
                        designer["tasks_count"] += 1
                        designer["tasks"].append(task)
                        break
        
        # Выводим текущую нагрузку
        print("\n👥 ТЕКУЩАЯ НАГРУЗКА:")
        for designer in self.designers.values():
            print(f"   • {designer['name']}: {designer['tasks_count']} задач")
        
        # Находим среднюю нагрузку
        total_tasks = sum(d["tasks_count"] for d in self.designers.values())
        avg_tasks = total_tasks / len(self.designers) if self.designers else 0
        
        print(f"\n📈 СРЕДНЯЯ НАГРУЗКА: {avg_tasks:.1f} задач")
        
        return avg_tasks
    
    def plan_redistribution(self, target_avg):
        """Планируем перераспределение"""
        print(f"\n🔄 ПЛАНИРОВАНИЕ ПЕРЕРАСПРЕДЕЛЕНИЯ")
        print("=" * 50)
        
        # Сортируем дизайнеров по нагрузке
        designers_list = list(self.designers.values())
        designers_list.sort(key=lambda x: x["tasks_count"], reverse=True)
        
        # Находим перегруженных и недогруженных
        overloaded = [d for d in designers_list if d["tasks_count"] > target_avg + 1]
        underloaded = [d for d in designers_list if d["tasks_count"] < target_avg - 1]
        
        print(f"   🎯 Перегруженные дизайнеры: {len(overloaded)}")
        print(f"   🎯 Недогруженные дизайнеры: {len(underloaded)}")
        
        # Планируем передачи задач
        for overloaded_designer in overloaded:
            excess_tasks = int(overloaded_designer["tasks_count"] - target_avg)
            
            for underloaded_designer in underloaded:
                if excess_tasks <= 0:
                    break
                
                needed_tasks = int(target_avg - underloaded_designer["tasks_count"])
                if needed_tasks <= 0:
                    continue
                
                # Выбираем задачи для передачи
                tasks_to_transfer = min(excess_tasks, needed_tasks, 2)  # Максимум 2 за раз
                
                # Выбираем задачи с низким приоритетом
                low_priority_tasks = [
                    task for task in overloaded_designer["tasks"]
                    if task["priority"].lower() in ["низкий", "low", "низкий приоритет"]
                ]
                
                if not low_priority_tasks:
                    low_priority_tasks = overloaded_designer["tasks"][:tasks_to_transfer]
                else:
                    low_priority_tasks = low_priority_tasks[:tasks_to_transfer]
                
                for task in low_priority_tasks:
                    self.redistributions.append({
                        "task_id": task["id"],
                        "task_title": task["title"],
                        "from_designer": overloaded_designer["name"],
                        "to_designer": underloaded_designer["name"],
                        "reason": "Равномерное распределение нагрузки"
                    })
                
                excess_tasks -= len(low_priority_tasks)
                underloaded_designer["tasks_count"] += len(low_priority_tasks)
                overloaded_designer["tasks_count"] -= len(low_priority_tasks)
        
        print(f"\n📋 ПЛАНИРУЕМЫЕ ИЗМЕНЕНИЯ: {len(self.redistributions)}")
        for redist in self.redistributions[:5]:  # Показываем первые 5
            print(f"   • {redist['task_title'][:40]} → {redist['from_designer']} → {redist['to_designer']}")
        
        if len(self.redistributions) > 5:
            print(f"   ... и еще {len(self.redistributions) - 5} изменений")
    
    def execute_redistribution(self, dry_run=True):
        """Выполняем перераспределение"""
        if not self.redistributions:
            print("\n✅ Перераспределение не требуется")
            return
        
        print(f"\n{'🔍 ТЕСТОВЫЙ РЕЖИМ' if dry_run else '🚀 ВЫПОЛНЕНИЕ ПЕРЕРАСПРЕДЕЛЕНИЯ'}")
        print("=" * 60)
        
        success_count = 0
        error_count = 0
        
        for redist in self.redistributions:
            try:
                if not dry_run:
                    # Находим ID дизайнера назначения
                    target_designer_id = None
                    for designer in self.designers.values():
                        if designer["name"].lower() == redist["to_designer"].lower():
                            target_designer_id = designer["id"]
                            break
                    
                    if target_designer_id:
                        # Обновляем задачу в Notion
                        url = f"https://api.notion.com/v1/pages/{redist['task_id']}"
                        
                        # Определяем поле для исполнителя
                        assignee_field = None
                        for field in ["Участники", "Assignee", "Исполнитель", "Responsible"]:
                            if field in self.todo_tasks[0]["properties"]:
                                assignee_field = field
                                break
                        
                        if assignee_field:
                            properties = {
                                assignee_field: {
                                    "people": [{"id": target_designer_id}]
                                }
                            }
                            
                            response = requests.patch(url, headers=self.headers, json={"properties": properties})
                            if response.status_code == 200:
                                success_count += 1
                                print(f"   ✅ {redist['task_title'][:40]} → {redist['to_designer']}")
                            else:
                                error_count += 1
                                print(f"   ❌ Ошибка API: {response.status_code}")
                        else:
                            error_count += 1
                            print(f"   ❌ Не найдено поле исполнителя")
                    else:
                        error_count += 1
                        print(f"   ❌ Не найден дизайнер: {redist['to_designer']}")
                else:
                    print(f"   🔍 {redist['task_title'][:40]} → {redist['from_designer']} → {redist['to_designer']}")
                    success_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"   ❌ Ошибка: {e}")
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"   ✅ Успешно: {success_count}")
        print(f"   ❌ Ошибки: {error_count}")
        
        if dry_run and success_count > 0:
            print(f"\n💡 Для выполнения изменений запустите скрипт с параметром --execute")
    
    def generate_report(self):
        """Генерируем отчет"""
        print(f"\n📋 ОТЧЕТ О ПЕРЕРАСПРЕДЕЛЕНИИ")
        print("=" * 50)
        
        print(f"   • Всего задач ToDo: {len(self.todo_tasks)}")
        print(f"   • Дизайнеров: {len(self.designers)}")
        print(f"   • Планируемых изменений: {len(self.redistributions)}")
        
        if self.redistributions:
            print(f"\n🎯 ЦЕЛЬ: Равномерное распределение нагрузки")
            print(f"   • Улучшение баланса между дизайнерами")
            print(f"   • Оптимизация производительности команды")
            print(f"   • Снижение риска перегрузки")

def main():
    """Основная функция"""
    import sys
    
    dry_run = "--execute" not in sys.argv
    
    print("🔄 ПЕРЕРАСПРЕДЕЛЕНИЕ ЗАДАЧ МЕЖДУ ДИЗАЙНЕРАМИ")
    print("=" * 60)
    
    redistributor = TaskRedistributor()
    
    try:
        redistributor.fetch_designers()
        redistributor.fetch_todo_tasks()
        target_avg = redistributor.analyze_current_distribution()
        redistributor.plan_redistribution(target_avg)
        redistributor.execute_redistribution(dry_run)
        redistributor.generate_report()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 