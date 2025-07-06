#!/usr/bin/env python3
"""
Система управления исполнителями задач
Анализ и исправление связей между задачами и сотрудниками
"""

import os
import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmployeeAssigneeSystem:
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.tasks_db_id = os.getenv("NOTION_DESIGN_TASKS_DB_ID")  # Задачи
        self.subtasks_db_id = os.getenv("NOTION_SUBTASKS_DB_ID")   # Подзадачи
        self.teams_db_id = os.getenv("NOTION_TEAMS_DB_ID")         # Сотрудники
        self.projects_db_id = os.getenv("NOTION_PROJECTS_DB_ID")   # Проекты
        
        if not all([self.notion_token, self.tasks_db_id, self.subtasks_db_id, self.teams_db_id]):
            raise ValueError("Не все необходимые переменные окружения установлены")
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        # Кэш для сотрудников
        self.employees_cache = {}
        self.employees_by_name = {}
        
    def get_database_schema(self, db_id: str) -> Dict:
        """Получить схему базы данных"""
        url = f"https://api.notion.com/v1/databases/{db_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def query_database(self, db_id: str, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Запрос к базе данных"""
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        payload = {"page_size": 100}
        
        if filter_dict:
            payload["filter"] = filter_dict
            
        all_results = []
        has_more = True
        
        while has_more:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            all_results.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            
            if has_more:
                payload["start_cursor"] = data.get("next_cursor")
        
        return all_results
    
    def analyze_employees_database(self) -> Dict:
        """Анализ базы сотрудников"""
        logger.info("🔍 Анализ базы сотрудников...")
        
        schema = self.get_database_schema(self.teams_db_id)
        logger.info(f"📋 Схема базы сотрудников: {list(schema['properties'].keys())}")
        
        employees = self.query_database(self.teams_db_id)
        logger.info(f"👥 Найдено сотрудников: {len(employees)}")
        
        # Анализ структуры
        employee_data = []
        for emp in employees:
            props = emp.get("properties", {})
            
            # Извлекаем данные сотрудника
            name = self.extract_title(props, "Name") or self.extract_title(props, "Имя") or "Без имени"
            role = self.extract_select(props, "Role") or self.extract_select(props, "Роль") or "Не указана"
            status = self.extract_select(props, "Status") or self.extract_select(props, "Статус") or "Активен"
            email = self.extract_email(props, "Email") or self.extract_email(props, "Почта") or ""
            
            employee_info = {
                "id": emp["id"],
                "name": name,
                "role": role,
                "status": status,
                "email": email,
                "created_time": emp.get("created_time"),
                "last_edited_time": emp.get("last_edited_time")
            }
            
            employee_data.append(employee_info)
            
            # Кэшируем для быстрого поиска
            self.employees_cache[emp["id"]] = employee_info
            self.employees_by_name[name.lower()] = employee_info
        
        return {
            "total_employees": len(employees),
            "employees": employee_data,
            "schema_fields": list(schema['properties'].keys())
        }
    
    def analyze_tasks_assignee_fields(self) -> Dict:
        """Анализ полей исполнителей в задачах"""
        logger.info("🔍 Анализ полей исполнителей в задачах...")
        
        schema = self.get_database_schema(self.tasks_db_id)
        logger.info(f"📋 Схема задач: {list(schema['properties'].keys())}")
        
        tasks = self.query_database(self.tasks_db_id)
        logger.info(f"📝 Найдено задач: {len(tasks)}")
        
        assignee_fields = {}
        people_field_data = []
        relation_field_data = []
        
        for task in tasks:
            props = task.get("properties", {})
            
            # Анализ поля "Участники" (people)
            if "Участники" in props:
                people = props["Участники"].get("people", [])
                if people:
                    people_field_data.append({
                        "task_id": task["id"],
                        "task_name": self.extract_title(props, "Задача") or "Без названия",
                        "assignees": [p.get("name", "Неизвестно") for p in people],
                        "assignee_ids": [p.get("id") for p in people]
                    })
            
            # Анализ поля "Исполнитель" (relation)
            if "Исполнитель" in props:
                relations = props["Исполнитель"].get("relation", [])
                if relations:
                    relation_field_data.append({
                        "task_id": task["id"],
                        "task_name": self.extract_title(props, "Задача") or "Без названия",
                        "assignee_ids": [r.get("id") for r in relations]
                    })
        
        return {
            "total_tasks": len(tasks),
            "tasks_with_people": len(people_field_data),
            "tasks_with_relation": len(relation_field_data),
            "people_field_data": people_field_data,
            "relation_field_data": relation_field_data,
            "schema_fields": list(schema['properties'].keys())
        }
    
    def analyze_subtasks_assignee_fields(self) -> Dict:
        """Анализ полей исполнителей в подзадачах"""
        logger.info("🔍 Анализ полей исполнителей в подзадачах...")
        
        schema = self.get_database_schema(self.subtasks_db_id)
        logger.info(f"📋 Схема подзадач: {list(schema['properties'].keys())}")
        
        subtasks = self.query_database(self.subtasks_db_id)
        logger.info(f"📝 Найдено подзадач: {len(subtasks)}")
        
        assignee_fields = {}
        people_field_data = []
        relation_field_data = []
        
        for subtask in subtasks:
            props = subtask.get("properties", {})
            
            # Анализ поля "Исполнитель" (people)
            if "Исполнитель" in props:
                people = props["Исполнитель"].get("people", [])
                if people:
                    people_field_data.append({
                        "subtask_id": subtask["id"],
                        "subtask_name": self.extract_title(props, "Подзадачи") or "Без названия",
                        "assignees": [p.get("name", "Неизвестно") for p in people],
                        "assignee_ids": [p.get("id") for p in people]
                    })
            
            # Анализ поля "Исполнитель" (relation)
            if "Исполнитель" in props:
                relations = props["Исполнитель"].get("relation", [])
                if relations:
                    relation_field_data.append({
                        "subtask_id": subtask["id"],
                        "subtask_name": self.extract_title(props, "Подзадачи") or "Без названия",
                        "assignee_ids": [r.get("id") for r in relations]
                    })
        
        return {
            "total_subtasks": len(subtasks),
            "subtasks_with_people": len(people_field_data),
            "subtasks_with_relation": len(relation_field_data),
            "people_field_data": people_field_data,
            "relation_field_data": relation_field_data,
            "schema_fields": list(schema['properties'].keys())
        }
    
    def find_arsentiy_in_employees(self) -> Optional[Dict]:
        """Поиск Арсентия в базе сотрудников"""
        logger.info("🔍 Поиск Арсентия в базе сотрудников...")
        
        # Поиск по имени
        search_variants = ["арсентий", "arsentiy", "арсений", "arseniy"]
        
        for variant in search_variants:
            if variant in self.employees_by_name:
                employee = self.employees_by_name[variant]
                logger.info(f"✅ Найден Арсентий: {employee}")
                return employee
        
        # Поиск по частичному совпадению
        for name, employee in self.employees_by_name.items():
            if any(variant in name for variant in search_variants):
                logger.info(f"✅ Найден Арсентий (частичное совпадение): {employee}")
                return employee
        
        logger.warning("❌ Арсентий не найден в базе сотрудников")
        return None
    
    def sync_assignee_fields(self, use_relation: bool = True) -> Dict:
        """Синхронизация полей исполнителей"""
        logger.info(f"🔄 Синхронизация полей исполнителей (использовать relation: {use_relation})")
        
        if use_relation:
            # Используем relation к базе сотрудников
            return self.sync_to_relation_field()
        else:
            # Используем people поле
            return self.sync_to_people_field()
    
    def sync_to_relation_field(self) -> Dict:
        """Синхронизация в relation поле"""
        logger.info("🔄 Синхронизация в relation поле...")
        
        # Получаем задачи с people полем
        tasks = self.query_database(self.tasks_db_id)
        updated_count = 0
        errors = []
        
        for task in tasks:
            props = task.get("properties", {})
            
            # Проверяем people поле
            if "Участники" in props:
                people = props["Участники"].get("people", [])
                if people:
                    # Ищем соответствующих сотрудников
                    relation_ids = []
                    for person in people:
                        person_name = person.get("name", "").lower()
                        if person_name in self.employees_by_name:
                            relation_ids.append({"id": self.employees_by_name[person_name]["id"]})
                    
                    if relation_ids:
                        # Обновляем relation поле
                        try:
                            self.update_task_assignee(task["id"], relation_ids)
                            updated_count += 1
                            logger.info(f"✅ Обновлена задача {task['id']}")
                        except Exception as e:
                            errors.append(f"Ошибка обновления задачи {task['id']}: {e}")
        
        return {
            "updated_tasks": updated_count,
            "errors": errors
        }
    
    def sync_to_people_field(self) -> Dict:
        """Синхронизация в people поле"""
        logger.info("🔄 Синхронизация в people поле...")
        
        # Получаем задачи с relation полем
        tasks = self.query_database(self.tasks_db_id)
        updated_count = 0
        errors = []
        
        for task in tasks:
            props = task.get("properties", {})
            
            # Проверяем relation поле
            if "Исполнитель" in props:
                relations = props["Исполнитель"].get("relation", [])
                if relations:
                    # Ищем соответствующих людей
                    people_ids = []
                    for relation in relations:
                        emp_id = relation.get("id")
                        if emp_id in self.employees_cache:
                            # Здесь нужно получить UUID пользователя Notion
                            # Это сложнее, так как нужно знать UUID пользователя
                            pass
                    
                    if people_ids:
                        # Обновляем people поле
                        try:
                            self.update_task_people(task["id"], people_ids)
                            updated_count += 1
                            logger.info(f"✅ Обновлена задача {task['id']}")
                        except Exception as e:
                            errors.append(f"Ошибка обновления задачи {task['id']}: {e}")
        
        return {
            "updated_tasks": updated_count,
            "errors": errors
        }
    
    def update_task_assignee(self, task_id: str, relation_ids: List[Dict]) -> None:
        """Обновить поле исполнителя в задаче"""
        url = f"https://api.notion.com/v1/pages/{task_id}"
        payload = {
            "properties": {
                "Исполнитель": {
                    "relation": relation_ids
                }
            }
        }
        
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
    
    def update_task_people(self, task_id: str, people_ids: List[Dict]) -> None:
        """Обновить поле участников в задаче"""
        url = f"https://api.notion.com/v1/pages/{task_id}"
        payload = {
            "properties": {
                "Участники": {
                    "people": people_ids
                }
            }
        }
        
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
    
    def extract_title(self, props: Dict, field_name: str) -> Optional[str]:
        """Извлечь значение title поля"""
        if field_name in props and props[field_name].get("type") == "title":
            title_array = props[field_name].get("title", [])
            if title_array:
                return title_array[0].get("plain_text", "")
        return None
    
    def extract_select(self, props: Dict, field_name: str) -> Optional[str]:
        """Извлечь значение select поля"""
        if field_name in props and props[field_name].get("type") == "select":
            select_obj = props[field_name].get("select")
            if select_obj:
                return select_obj.get("name", "")
        return None
    
    def extract_email(self, props: Dict, field_name: str) -> Optional[str]:
        """Извлечь значение email поля"""
        if field_name in props and props[field_name].get("type") == "email":
            return props[field_name].get("email", "")
        return None
    
    def generate_report(self) -> str:
        """Генерация отчета"""
        logger.info("📊 Генерация отчета...")
        
        # Анализ всех баз
        employees_analysis = self.analyze_employees_database()
        tasks_analysis = self.analyze_tasks_assignee_fields()
        subtasks_analysis = self.analyze_subtasks_assignee_fields()
        arsentiy_info = self.find_arsentiy_in_employees()
        
        report = f"""
# 📊 ОТЧЕТ ПО СИСТЕМЕ ИСПОЛНИТЕЛЕЙ
**Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 👥 БАЗА СОТРУДНИКОВ
- **Всего сотрудников**: {employees_analysis['total_employees']}
- **Поля схемы**: {', '.join(employees_analysis['schema_fields'])}

### Сотрудники:
"""
        
        for emp in employees_analysis['employees']:
            report += f"- **{emp['name']}** ({emp['role']}) - {emp['status']}\n"
        
        report += f"""
## 📝 ЗАДАЧИ
- **Всего задач**: {tasks_analysis['total_tasks']}
- **С полем 'Участники' (people)**: {tasks_analysis['tasks_with_people']}
- **С полем 'Исполнитель' (relation)**: {tasks_analysis['tasks_with_relation']}
- **Поля схемы**: {', '.join(tasks_analysis['schema_fields'])}

## 📋 ПОДЗАДАЧИ
- **Всего подзадач**: {subtasks_analysis['total_subtasks']}
- **С полем 'Исполнитель' (people)**: {subtasks_analysis['subtasks_with_people']}
- **С полем 'Исполнитель' (relation)**: {subtasks_analysis['subtasks_with_relation']}
- **Поля схемы**: {', '.join(subtasks_analysis['schema_fields'])}

## 🔍 ПОИСК АРСЕНТИЯ
"""
        
        if arsentiy_info:
            report += f"✅ **Найден**: {arsentiy_info['name']} ({arsentiy_info['role']})\n"
        else:
            report += "❌ **Не найден** в базе сотрудников\n"
        
        report += """
## 🎯 РЕКОМЕНДАЦИИ

### Вариант 1: Использовать relation к базе сотрудников
**Плюсы:**
- Полный контроль над данными сотрудников
- Возможность фильтрации по ролям, статусам
- Синхронизация с базой сотрудников

**Минусы:**
- Нужно правильно настроить relation поле
- Сложнее для гостей (нужно добавлять в базу)

### Вариант 2: Использовать people поле
**Плюсы:**
- Простота использования
- Автоматическая поддержка гостей
- Стандартный подход Notion

**Минусы:**
- Нет контроля над данными
- Сложно фильтровать по ролям
- Гости не видны через API

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. **Определить приоритетный подход** (relation vs people)
2. **Настроить правильную схему** полей
3. **Синхронизировать существующие данные**
4. **Создать скрипты автоматизации**
5. **Добавить Арсентия в базу сотрудников** (если не найден)
"""
        
        return report

def main():
    """Основная функция"""
    try:
        system = EmployeeAssigneeSystem()
        
        # Генерация отчета
        report = system.generate_report()
        
        # Сохранение отчета
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"reports/EMPLOYEE_ASSIGNEE_REPORT_{timestamp}.md"
        
        os.makedirs("reports", exist_ok=True)
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n📄 Отчет сохранен: {report_filename}")
        
        # Интерактивный выбор действия
        print("\n🎯 Выберите действие:")
        print("1. Синхронизировать в relation поле (к базе сотрудников)")
        print("2. Синхронизировать в people поле")
        print("3. Только анализ (без изменений)")
        
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            result = system.sync_assignee_fields(use_relation=True)
            print(f"✅ Обновлено задач: {result['updated_tasks']}")
            if result['errors']:
                print(f"❌ Ошибки: {result['errors']}")
        
        elif choice == "2":
            result = system.sync_assignee_fields(use_relation=False)
            print(f"✅ Обновлено задач: {result['updated_tasks']}")
            if result['errors']:
                print(f"❌ Ошибки: {result['errors']}")
        
        else:
            print("📊 Только анализ выполнен")
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise

if __name__ == "__main__":
    main() 