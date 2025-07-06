#!/usr/bin/env python3
"""
Решение системы назначения задач
Проблема: база Teams содержит отделы, а не конкретных сотрудников
Решение: использовать people поле для конкретных исполнителей + relation для отделов
"""

import os
import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskAssigneeSolution:
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.tasks_db_id = os.getenv("NOTION_DESIGN_TASKS_DB_ID")
        self.subtasks_db_id = os.getenv("NOTION_SUBTASKS_DB_ID")
        self.teams_db_id = os.getenv("NOTION_TEAMS_DB_ID")
        
        if not all([self.notion_token, self.tasks_db_id, self.subtasks_db_id, self.teams_db_id]):
            raise ValueError("Не все необходимые переменные окружения установлены")
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        # Кэш отделов
        self.departments_cache = {}
        
    def analyze_current_situation(self) -> Dict:
        """Анализ текущей ситуации"""
        logger.info("🔍 Анализ текущей ситуации...")
        
        # Анализ базы отделов
        departments = self.analyze_departments()
        
        # Анализ задач
        tasks_analysis = self.analyze_tasks_assignees()
        
        # Анализ подзадач
        subtasks_analysis = self.analyze_subtasks_assignees()
        
        return {
            "departments": departments,
            "tasks": tasks_analysis,
            "subtasks": subtasks_analysis
        }
    
    def analyze_departments(self) -> Dict:
        """Анализ базы отделов"""
        logger.info("🏢 Анализ базы отделов...")
        
        schema_url = f"https://api.notion.com/v1/databases/{self.teams_db_id}"
        schema_response = requests.get(schema_url, headers=self.headers)
        schema_response.raise_for_status()
        schema = schema_response.json()
        
        # Получаем все отделы
        query_url = f"https://api.notion.com/v1/databases/{self.teams_db_id}/query"
        response = requests.post(query_url, headers=self.headers, json={"page_size": 100})
        response.raise_for_status()
        departments_data = response.json().get("results", [])
        
        departments = []
        for dept in departments_data:
            props = dept.get("properties", {})
            name = self.extract_title(props, "Name") or "Без названия"
            description = self.extract_rich_text(props, "Описание") or ""
            
            dept_info = {
                "id": dept["id"],
                "name": name,
                "description": description
            }
            
            departments.append(dept_info)
            self.departments_cache[dept["id"]] = dept_info
        
        return {
            "total": len(departments),
            "departments": departments,
            "schema_fields": list(schema['properties'].keys())
        }
    
    def analyze_tasks_assignees(self) -> Dict:
        """Анализ исполнителей в задачах"""
        logger.info("📝 Анализ исполнителей в задачах...")
        
        schema = self.get_database_schema(self.tasks_db_id)
        tasks = self.query_database(self.tasks_db_id)
        
        people_field_count = 0
        relation_field_count = 0
        tasks_with_people = []
        tasks_with_relation = []
        
        for task in tasks:
            props = task.get("properties", {})
            task_name = self.extract_title(props, "Задача") or "Без названия"
            
            # Проверяем поле "Участники" (people)
            if "Участники" in props:
                people = props["Участники"].get("people", [])
                if people:
                    people_field_count += 1
                    tasks_with_people.append({
                        "id": task["id"],
                        "name": task_name,
                        "assignees": [p.get("name", "Неизвестно") for p in people],
                        "assignee_ids": [p.get("id") for p in people]
                    })
            
            # Проверяем поле "Исполнитель" (relation)
            if "Исполнитель" in props:
                relations = props["Исполнитель"].get("relation", [])
                if relations:
                    relation_field_count += 1
                    tasks_with_relation.append({
                        "id": task["id"],
                        "name": task_name,
                        "department_ids": [r.get("id") for r in relations]
                    })
        
        return {
            "total_tasks": len(tasks),
            "tasks_with_people": people_field_count,
            "tasks_with_relation": relation_field_count,
            "people_data": tasks_with_people,
            "relation_data": tasks_with_relation,
            "schema_fields": list(schema['properties'].keys())
        }
    
    def analyze_subtasks_assignees(self) -> Dict:
        """Анализ исполнителей в подзадачах"""
        logger.info("📋 Анализ исполнителей в подзадачах...")
        
        schema = self.get_database_schema(self.subtasks_db_id)
        subtasks = self.query_database(self.subtasks_db_id)
        
        people_field_count = 0
        relation_field_count = 0
        subtasks_with_people = []
        subtasks_with_relation = []
        
        for subtask in subtasks:
            props = subtask.get("properties", {})
            subtask_name = self.extract_title(props, "Подзадачи") or "Без названия"
            
            # Проверяем поле "Исполнитель" (people)
            if "Исполнитель" in props:
                people = props["Исполнитель"].get("people", [])
                if people:
                    people_field_count += 1
                    subtasks_with_people.append({
                        "id": subtask["id"],
                        "name": subtask_name,
                        "assignees": [p.get("name", "Неизвестно") for p in people],
                        "assignee_ids": [p.get("id") for p in people]
                    })
            
            # Проверяем поле "Исполнитель" (relation)
            if "Исполнитель" in props:
                relations = props["Исполнитель"].get("relation", [])
                if relations:
                    relation_field_count += 1
                    subtasks_with_relation.append({
                        "id": subtask["id"],
                        "name": subtask_name,
                        "department_ids": [r.get("id") for r in relations]
                    })
        
        return {
            "total_subtasks": len(subtasks),
            "subtasks_with_people": people_field_count,
            "subtasks_with_relation": relation_field_count,
            "people_data": subtasks_with_people,
            "relation_data": subtasks_with_relation,
            "schema_fields": list(schema['properties'].keys())
        }
    
    def get_database_schema(self, db_id: str) -> Dict:
        """Получить схему базы данных"""
        url = f"https://api.notion.com/v1/databases/{db_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def query_database(self, db_id: str) -> List[Dict]:
        """Запрос к базе данных"""
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        all_results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {"page_size": 100}
            if start_cursor:
                payload["start_cursor"] = start_cursor
                
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            all_results.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
        
        return all_results
    
    def extract_title(self, props: Dict, field_name: str) -> str:
        """Извлечь title поле"""
        if field_name in props and props[field_name].get("type") == "title":
            title_array = props[field_name].get("title", [])
            if title_array:
                return title_array[0].get("plain_text", "")
        return ""
    
    def extract_rich_text(self, props: Dict, field_name: str) -> str:
        """Извлечь rich_text поле"""
        if field_name in props and props[field_name].get("type") == "rich_text":
            rich_text_array = props[field_name].get("rich_text", [])
            if rich_text_array:
                return rich_text_array[0].get("plain_text", "")
        return ""
    
    def propose_solution(self, analysis: Dict) -> str:
        """Предложить решение"""
        logger.info("💡 Генерация решения...")
        
        solution = f"""
# 🎯 РЕШЕНИЕ СИСТЕМЫ НАЗНАЧЕНИЯ ЗАДАЧ

## 📊 ТЕКУЩАЯ СИТУАЦИЯ

### 🏢 База отделов (Teams)
- **Всего отделов**: {analysis['departments']['total']}
- **Отделы**: {', '.join([dept['name'] for dept in analysis['departments']['departments']])}

### 📝 Задачи
- **Всего задач**: {analysis['tasks']['total_tasks']}
- **С полем 'Участники' (people)**: {analysis['tasks']['tasks_with_people']}
- **С полем 'Исполнитель' (relation)**: {analysis['tasks']['tasks_with_relation']}

### 📋 Подзадачи
- **Всего подзадач**: {analysis['subtasks']['total_subtasks']}
- **С полем 'Исполнитель' (people)**: {analysis['subtasks']['subtasks_with_people']}
- **С полем 'Исполнитель' (relation)**: {analysis['subtasks']['subtasks_with_relation']}

## 🚨 ПРОБЛЕМА
База Teams содержит **отделы**, а не конкретных сотрудников. Это создает путаницу в назначении задач.

## ✅ РЕШЕНИЕ: ГИБРИДНАЯ СИСТЕМА

### 1. Поле "Участники" (people) - для конкретных исполнителей
- **Назначение**: Конкретные люди, которые выполняют задачу
- **Тип**: people (поддерживает гостей)
- **Использование**: Основное поле для назначения

### 2. Поле "Отдел" (relation) - для привязки к отделу
- **Назначение**: Привязка задачи к отделу для аналитики
- **Тип**: relation к базе Teams
- **Использование**: Дополнительное поле для фильтрации

### 3. Автоматическая синхронизация
- При назначении участника автоматически определять отдел
- При назначении отдела предлагать участников из этого отдела

## 🛠️ ПЛАН РЕАЛИЗАЦИИ

### Этап 1: Анализ и подготовка
1. ✅ Анализ текущей структуры (выполнено)
2. 🔄 Создание маппинга "участник → отдел"
3. 🔄 Анализ существующих назначений

### Этап 2: Настройка полей
1. 🔄 Переименовать поле "Исполнитель" в "Отдел" в задачах
2. 🔄 Переименовать поле "Исполнитель" в "Отдел" в подзадачах
3. 🔄 Убедиться, что поле "Участники" настроено правильно

### Этап 3: Синхронизация данных
1. 🔄 Создать скрипт автоматической синхронизации
2. 🔄 Применить к существующим задачам
3. 🔄 Настроить автоматизацию для новых задач

### Этап 4: Автоматизация
1. 🔄 Создать Telegram бота для назначения задач
2. 🔄 Интеграция с существующими скриптами
3. 🔄 Мониторинг и отчеты

## 🎯 ПРЕИМУЩЕСТВА РЕШЕНИЯ

### ✅ Гибкость
- Поддержка как сотрудников, так и гостей
- Возможность назначения на отдел или конкретного человека
- Автоматическая синхронизация

### ✅ Аналитика
- Фильтрация по отделам
- Отчеты по загрузке отделов
- KPI по отделам и сотрудникам

### ✅ Простота использования
- Интуитивный интерфейс
- Автоматические подсказки
- Минимум ручной работы

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. **Подтвердить план** - согласовать подход
2. **Создать маппинг** - участник → отдел
3. **Настроить поля** - переименовать relation поля
4. **Реализовать синхронизацию** - автоматическое обновление
5. **Протестировать** - на небольшом объеме данных
6. **Внедрить** - применить ко всем задачам
"""
        
        return solution
    
    def create_assignee_mapping(self) -> Dict:
        """Создать маппинг участников на отделы"""
        logger.info("🗺️ Создание маппинга участников на отделы...")
        
        # Получаем всех участников из задач
        tasks = self.query_database(self.tasks_db_id)
        subtasks = self.query_database(self.subtasks_db_id)
        
        all_assignees = set()
        
        # Собираем участников из задач
        for task in tasks:
            props = task.get("properties", {})
            if "Участники" in props:
                people = props["Участники"].get("people", [])
                for person in people:
                    all_assignees.add(person.get("name", "Неизвестно"))
        
        # Собираем участников из подзадач
        for subtask in subtasks:
            props = subtask.get("properties", {})
            if "Исполнитель" in props:
                people = props["Исполнитель"].get("people", [])
                for person in people:
                    all_assignees.add(person.get("name", "Неизвестно"))
        
        # Создаем маппинг (ручной, можно доработать)
        mapping = {
            "Арсентий": "Дизайн",
            "Арсений": "Дизайн", 
            "Arsentiy": "Дизайн",
            "Arseniy": "Дизайн",
            "Саша": "Дизайн",
            "Александр": "Дизайн",
            "Вика": "Маркетинг",
            "Виктория": "Маркетинг",
            "Аня": "Контент",
            "Анна": "Контент",
            "Данил": "Креатив",
            "Данила": "Креатив",
            "Даня": "Креатив"
        }
        
        # Анализ неопределенных участников
        undefined_assignees = [name for name in all_assignees if name not in mapping]
        
        return {
            "mapping": mapping,
            "all_assignees": list(all_assignees),
            "undefined_assignees": undefined_assignees,
            "departments": [dept['name'] for dept in self.departments_cache.values()]
        }

def main():
    """Основная функция"""
    try:
        solution = TaskAssigneeSolution()
        
        # Анализ текущей ситуации
        analysis = solution.analyze_current_situation()
        
        # Генерация решения
        solution_text = solution.propose_solution(analysis)
        
        # Создание маппинга
        mapping = solution.create_assignee_mapping()
        
        # Вывод результатов
        print(solution_text)
        
        print("\n🗺️ МАППИНГ УЧАСТНИКОВ НА ОТДЕЛЫ:")
        for assignee, department in mapping['mapping'].items():
            print(f"  {assignee} → {department}")
        
        if mapping['undefined_assignees']:
            print(f"\n❓ НЕОПРЕДЕЛЕННЫЕ УЧАСТНИКИ ({len(mapping['undefined_assignees'])}):")
            for assignee in mapping['undefined_assignees']:
                print(f"  - {assignee}")
        
        # Сохранение отчета
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"reports/TASK_ASSIGNEE_SOLUTION_{timestamp}.md"
        
        os.makedirs("reports", exist_ok=True)
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(solution_text)
            f.write(f"\n\n## 🗺️ МАППИНГ УЧАСТНИКОВ\n")
            for assignee, department in mapping['mapping'].items():
                f.write(f"- {assignee} → {department}\n")
            if mapping['undefined_assignees']:
                f.write(f"\n### ❓ НЕОПРЕДЕЛЕННЫЕ УЧАСТНИКИ\n")
                for assignee in mapping['undefined_assignees']:
                    f.write(f"- {assignee}\n")
        
        print(f"\n📄 Отчет сохранен: {report_filename}")
        
        # Интерактивный выбор
        print("\n🎯 Выберите действие:")
        print("1. Создать скрипт синхронизации")
        print("2. Настроить поля в Notion")
        print("3. Создать Telegram бота для назначения")
        print("4. Только анализ (завершить)")
        
        choice = input("\nВведите номер (1-4): ").strip()
        
        if choice == "1":
            print("🔄 Создание скрипта синхронизации...")
            # TODO: Создать скрипт синхронизации
        
        elif choice == "2":
            print("⚙️ Настройка полей в Notion...")
            # TODO: Создать скрипт настройки полей
        
        elif choice == "3":
            print("🤖 Создание Telegram бота...")
            # TODO: Создать Telegram бота
        
        else:
            print("📊 Анализ завершен")
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise

if __name__ == "__main__":
    main() 