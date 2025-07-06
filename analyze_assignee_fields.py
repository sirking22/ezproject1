#!/usr/bin/env python3
"""
Анализ проблемы с двумя полями исполнителей в Notion
"""

import json
import os
import sys
from notion_client import Client
from typing import Dict, List, Set

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    """Загружаем переменные окружения"""
    from dotenv import load_dotenv
    load_dotenv()
    
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        raise ValueError("NOTION_TOKEN не найден в .env")
    
    return notion_token

class AssigneeFieldAnalyzer:
    """Анализатор полей исполнителей"""
    
    def __init__(self):
        """Инициализация анализатора"""
        self.notion_token = load_env()
        self.client = Client(auth=self.notion_token)
        
        # ID баз данных
        self.tasks_db_id = "d09df250ce7e4e0d9fbe4e036d320def"
        self.subtasks_db_id = "9c5f4269d61449b6a7485579a3c21da3"
        self.teams_db_id = "1d6ace03d9ff805787b9ec31f5b4dde7"
        
        # Результаты анализа
        self.tasks_analysis = {}
        self.subtasks_analysis = {}
        self.teams_analysis = {}
    
    def analyze_tasks_assignee_fields(self):
        """Анализ полей исполнителей в задачах"""
        print("🔍 АНАЛИЗ ПОЛЕЙ ИСПОЛНИТЕЛЕЙ В ЗАДАЧАХ")
        print("=" * 50)
        
        try:
            # Получаем несколько задач для анализа
            response = self.client.databases.query(
                database_id=self.tasks_db_id,
                page_size=10
            )
            
            tasks = response["results"]
            print(f"📊 Проанализировано задач: {len(tasks)}")
            
            for i, task in enumerate(tasks, 1):
                print(f"\n📋 ЗАДАЧА {i}:")
                
                properties = task.get("properties", {})
                
                # Название
                title_prop = properties.get("Задача", {})
                if title_prop.get("title"):
                    title = title_prop["title"][0]["plain_text"]
                    print(f"Название: {title}")
                
                # Поле "Участники" (people)
                participants_prop = properties.get("Участники", {})
                print(f"👥 Участники (people):")
                if participants_prop.get("people"):
                    for person in participants_prop["people"]:
                        print(f"  - {person.get('name', 'Без имени')} (ID: {person.get('id')})")
                        print(f"    Email: {person.get('person', {}).get('email', 'Не указан')}")
                else:
                    print("  Нет участников")
                
                # Поле "Участник (стата)" (relation)
                stats_prop = properties.get("Участник (стата)", {})
                print(f"📊 Участник (стата) (relation):")
                if stats_prop.get("relation"):
                    for relation in stats_prop["relation"]:
                        print(f"  - ID: {relation.get('id')}")
                        # Получаем детали связанной записи
                        try:
                            related_page = self.client.pages.retrieve(relation["id"])
                            related_props = related_page.get("properties", {})
                            related_name = related_props.get("Name", {})
                            if related_name.get("title"):
                                name = related_name["title"][0]["plain_text"]
                                print(f"    Название: {name}")
                        except Exception as e:
                            print(f"    Ошибка получения деталей: {e}")
                else:
                    print("  Нет связей")
                
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Ошибка анализа задач: {e}")
    
    def analyze_subtasks_assignee_fields(self):
        """Анализ полей исполнителей в подзадачах"""
        print("\n🔍 АНАЛИЗ ПОЛЕЙ ИСПОЛНИТЕЛЕЙ В ПОДЗАДАЧАХ")
        print("=" * 50)
        
        try:
            # Получаем несколько подзадач для анализа
            response = self.client.databases.query(
                database_id=self.subtasks_db_id,
                page_size=10
            )
            
            subtasks = response["results"]
            print(f"📊 Проанализировано подзадач: {len(subtasks)}")
            
            for i, subtask in enumerate(subtasks, 1):
                print(f"\n📋 ПОДЗАДАЧА {i}:")
                
                properties = subtask.get("properties", {})
                
                # Название
                title_prop = properties.get("Подзадачи", {})
                if title_prop.get("title"):
                    title = title_prop["title"][0]["plain_text"]
                    print(f"Название: {title}")
                
                # Поле "Исполнитель" (people)
                assignee_prop = properties.get("Исполнитель", {})
                print(f"👤 Исполнитель (people):")
                if assignee_prop.get("people"):
                    for person in assignee_prop["people"]:
                        print(f"  - {person.get('name', 'Без имени')} (ID: {person.get('id')})")
                        print(f"    Email: {person.get('person', {}).get('email', 'Не указан')}")
                else:
                    print("  Нет исполнителя")
                
                # Поле "Исполнитель (стата)" (relation)
                stats_prop = properties.get("Исполнитель (стата)", {})
                print(f"📊 Исполнитель (стата) (relation):")
                if stats_prop.get("relation"):
                    for relation in stats_prop["relation"]:
                        print(f"  - ID: {relation.get('id')}")
                        # Получаем детали связанной записи
                        try:
                            related_page = self.client.pages.retrieve(relation["id"])
                            related_props = related_page.get("properties", {})
                            related_name = related_props.get("Name", {})
                            if related_name.get("title"):
                                name = related_name["title"][0]["plain_text"]
                                print(f"    Название: {name}")
                        except Exception as e:
                            print(f"    Ошибка получения деталей: {e}")
                else:
                    print("  Нет связей")
                
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Ошибка анализа подзадач: {e}")
    
    def analyze_teams_database(self):
        """Анализ базы Teams"""
        print("\n🔍 АНАЛИЗ БАЗЫ TEAMS")
        print("=" * 50)
        
        try:
            response = self.client.databases.query(
                database_id=self.teams_db_id,
                page_size=100
            )
            
            teams = response["results"]
            print(f"📊 Всего записей в Teams: {len(teams)}")
            
            print("\n📋 СОДЕРЖИМОЕ БАЗЫ TEAMS:")
            for i, team in enumerate(teams, 1):
                properties = team.get("properties", {})
                
                # Название
                name_prop = properties.get("Name", {})
                if name_prop.get("title"):
                    name = name_prop["title"][0]["plain_text"]
                    print(f"{i}. {name}")
                    
                    # Дополнительные поля
                    description_prop = properties.get("Описание", {})
                    if description_prop.get("rich_text"):
                        description = description_prop["rich_text"][0]["plain_text"]
                        print(f"   Описание: {description}")
                    
                    manager_prop = properties.get("Руководитель", {})
                    if manager_prop.get("rich_text"):
                        manager = manager_prop["rich_text"][0]["plain_text"]
                        print(f"   Руководитель: {manager}")
            
            print("\n🚨 ВЫВОД:")
            print("База Teams содержит ОТДЕЛЫ, а не сотрудников!")
            print("Это объясняет проблему с полем 'стата' - оно ссылается на отделы, а не на людей.")
            
        except Exception as e:
            print(f"❌ Ошибка анализа Teams: {e}")
    
    def find_arsentiy_tasks(self):
        """Поиск задач Арсентию"""
        print("\n🔍 ПОИСК ЗАДАЧ АРСЕНТИЮ")
        print("=" * 50)
        
        try:
            # Поиск в задачах
            tasks_response = self.client.databases.query(
                database_id=self.tasks_db_id,
                filter={
                    "property": "Участники",
                    "people": {
                        "contains": "Arsentiy"
                    }
                }
            )
            
            tasks = tasks_response["results"]
            print(f"📊 Задач с Арсентием: {len(tasks)}")
            
            for i, task in enumerate(tasks[:5], 1):  # Показываем первые 5
                properties = task.get("properties", {})
                
                title_prop = properties.get("Задача", {})
                if title_prop.get("title"):
                    title = title_prop["title"][0]["plain_text"]
                    print(f"{i}. {title}")
                    
                    # Проверяем поле стата
                    stats_prop = properties.get("Участник (стата)", {})
                    if stats_prop.get("relation"):
                        print(f"   Стата: Есть связь с {len(stats_prop['relation'])} записью")
                    else:
                        print(f"   Стата: Нет связи")
            
            # Поиск в подзадачах
            subtasks_response = self.client.databases.query(
                database_id=self.subtasks_db_id,
                filter={
                    "property": "Исполнитель",
                    "people": {
                        "contains": "Arsentiy"
                    }
                }
            )
            
            subtasks = subtasks_response["results"]
            print(f"\n📊 Подзадач с Арсентием: {len(subtasks)}")
            
            for i, subtask in enumerate(subtasks[:5], 1):  # Показываем первые 5
                properties = subtask.get("properties", {})
                
                title_prop = properties.get("Подзадачи", {})
                if title_prop.get("title"):
                    title = title_prop["title"][0]["plain_text"]
                    print(f"{i}. {title}")
                    
                    # Проверяем поле стата
                    stats_prop = properties.get("Исполнитель (стата)", {})
                    if stats_prop.get("relation"):
                        print(f"   Стата: Есть связь с {len(stats_prop['relation'])} записью")
                    else:
                        print(f"   Стата: Нет связи")
            
        except Exception as e:
            print(f"❌ Ошибка поиска задач Арсентию: {e}")
    
    def generate_recommendations(self):
        """Генерация рекомендаций"""
        print("\n💡 РЕКОМЕНДАЦИИ")
        print("=" * 50)
        
        print("1. 🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА:")
        print("   - Поле 'стата' ссылается на базу Teams (отделы), а не на сотрудников")
        print("   - Это нарушает логику фильтрации и статистики")
        
        print("\n2. 🔧 КРАТКОСРОЧНЫЕ РЕШЕНИЯ:")
        print("   - Использовать только поле people для фильтрации")
        print("   - Игнорировать поле relation 'стата' в автоматизации")
        print("   - Создать локальный registry для гостей")
        
        print("\n3. 🎯 ДОЛГОСРОЧНЫЕ РЕШЕНИЯ:")
        print("   - Создать отдельную базу сотрудников Employees")
        print("   - Исправить поле 'стата' для ссылки на сотрудников")
        print("   - Настроить автоматическую синхронизацию people → relation")
        print("   - Мигрировать гостей в полных пользователей")
        
        print("\n4. 📊 ПЛАН ДЕЙСТВИЙ:")
        print("   Неделя 1: Создать Employees базу, исправить поля")
        print("   Неделя 2: Настроить синхронизацию, протестировать")
        print("   Неделя 3: Мигрировать гостей, обновить скрипты")
        print("   Неделя 4: Полная автоматизация и мониторинг")

def main():
    """Основная функция"""
    print("🚀 АНАЛИЗ ПРОБЛЕМЫ С ДВУМЯ ПОЛЯМИ ИСПОЛНИТЕЛЕЙ")
    print("=" * 60)
    
    analyzer = AssigneeFieldAnalyzer()
    
    # Анализируем все аспекты
    analyzer.analyze_tasks_assignee_fields()
    analyzer.analyze_subtasks_assignee_fields()
    analyzer.analyze_teams_database()
    analyzer.find_arsentiy_tasks()
    analyzer.generate_recommendations()
    
    print("\n✅ Анализ завершен")

if __name__ == "__main__":
    main() 