#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 НАСТРОЙКА БИЗНЕС-ЦЕПОЧЕК

Автоматическая настройка связок:
1. КОНЦЕПТ/СЦЕНАРИЙ + ИДЕИ = ТЕСТЫ
2. ЗАДАЧИ = МАТЕРИАЛЫ + ПОКАЗАТЕЛИ + ГАЙДЫ  
3. ГАЙДЫ = ПОВТОРНЫЕ АКТИВНОСТИ + ПОКАЗАТЕЛИ + ДОРАБОТКА/АРХИВ
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class BusinessChainSetup:
    """Настройка бизнес-цепочек в Notion"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        if not self.notion_token:
            raise ValueError("❌ NOTION_TOKEN не найден в .env")
        
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # ID баз данных
        self.databases = {
            'concepts': '6fc4322e6d0c45a6b37ac49b818a063a',
            'ideas': 'ad92a6e21485428c84de8587706b3be1',
            'tasks': 'd09df250ce7e4e0d9fbe4e036d320def',
            'materials': '1d9ace03d9ff804191a4d35aeedcbbd4',
            'guides': '47c6086858d442ebaeceb4fad1b23ba3',
            'kpi': '1d6ace03d9ff80bfb809ed21dfd2150c'
        }
    
    def analyze_current_relations(self):
        """Анализирует текущие связи между базами"""
        
        print("📊 АНАЛИЗ ТЕКУЩИХ СВЯЗЕЙ")
        print("=" * 50)
        
        relations_map = {}
        
        for db_name, db_id in self.databases.items():
            try:
                response = requests.get(
                    f"https://api.notion.com/v1/databases/{db_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    db_data = response.json()
                    properties = db_data.get('properties', {})
                    
                    relations = []
                    for prop_name, prop_data in properties.items():
                        if prop_data.get('type') == 'relation':
                            target_db = prop_data.get('relation', {}).get('database_id')
                            if target_db:
                                relations.append({
                                    'property': prop_name,
                                    'target_db': target_db
                                })
                    
                    relations_map[db_name] = relations
                    print(f"✅ {db_name.upper()}: {len(relations)} связей")
                    
                    for rel in relations:
                        target_name = self._get_db_name_by_id(rel['target_db'])
                        print(f"   • {rel['property']} → {target_name}")
                        
                else:
                    print(f"❌ {db_name.upper()}: ошибка {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {db_name.upper()}: {e}")
        
        return relations_map
    
    def _get_db_name_by_id(self, db_id):
        """Получает название базы по ID"""
        for name, id_val in self.databases.items():
            if id_val == db_id:
                return name.upper()
        return f"UNKNOWN ({db_id[:8]}...)"
    
    def create_relation_property(self, database_id, property_name, target_db_id):
        """Создает relation property в базе данных"""
        
        property_data = {
            "name": property_name,
            "type": "relation",
            "relation": {
                "database_id": target_db_id
            }
        }
        
        try:
            response = requests.patch(
                f"https://api.notion.com/v1/databases/{database_id}",
                headers=self.headers,
                json={
                    "properties": {
                        property_name: property_data
                    }
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Создана связь: {property_name}")
                return True
            else:
                print(f"❌ Ошибка создания {property_name}: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def setup_concept_testing_chain(self):
        """Настраивает цепочку КОНЦЕПТ + ИДЕИ = ТЕСТЫ"""
        
        print(f"\n🎯 ЭТАП 1: НАСТРОЙКА КОНЦЕПТЫ + ТЕСТЫ")
        print("=" * 60)
        
        # 1. Создать связь CONCEPTS → TASKS
        print("1️⃣ Создание связи CONCEPTS → TASKS...")
        success1 = self.create_relation_property(
            self.databases['concepts'],
            "Тестовые задачи",
            self.databases['tasks']
        )
        
        # 2. Добавить поля для тестирования в CONCEPTS
        print("2️⃣ Добавление полей тестирования в CONCEPTS...")
        
        # Статус тестирования
        success2 = self._add_select_property(
            self.databases['concepts'],
            "Статус тестирования",
            ["Не тестировался", "В тестировании", "Успешен", "Провален"]
        )
        
        # Результаты теста
        success3 = self._add_rich_text_property(
            self.databases['concepts'],
            "Результаты теста"
        )
        
        # Рекомендация
        success4 = self._add_select_property(
            self.databases['concepts'],
            "Рекомендация",
            ["Внедрять", "Доработать", "Отклонить"]
        )
        
        return success1 and success2 and success3 and success4
    
    def setup_tasks_integration_chain(self):
        """Настраивает цепочку ЗАДАЧИ = МАТЕРИАЛЫ + ГАЙДЫ + KPI"""
        
        print(f"\n🎯 ЭТАП 2: НАСТРОЙКА ЗАДАЧИ + МАТЕРИАЛЫ + ГАЙДЫ")
        print("=" * 60)
        
        # 1. TASKS → MATERIALS
        print("1️⃣ Создание связи TASKS → MATERIALS...")
        success1 = self.create_relation_property(
            self.databases['tasks'],
            "Связанные материалы",
            self.databases['materials']
        )
        
        # 2. TASKS → GUIDES
        print("2️⃣ Создание связи TASKS → GUIDES...")
        success2 = self.create_relation_property(
            self.databases['tasks'],
            "Связанные гайды",
            self.databases['guides']
        )
        
        # 3. TASKS → KPI
        print("3️⃣ Создание связи TASKS → KPI...")
        success3 = self.create_relation_property(
            self.databases['tasks'],
            "KPI метрики",
            self.databases['kpi']
        )
        
        # 4. MATERIALS → TASKS
        print("4️⃣ Создание связи MATERIALS → TASKS...")
        success4 = self.create_relation_property(
            self.databases['materials'],
            "Связанные задачи",
            self.databases['tasks']
        )
        
        # 5. GUIDES → TASKS
        print("5️⃣ Создание связи GUIDES → TASKS...")
        success5 = self.create_relation_property(
            self.databases['guides'],
            "Связанные задачи",
            self.databases['guides']
        )
        
        return success1 and success2 and success3 and success4 and success5
    
    def setup_guides_activity_chain(self):
        """Настраивает цепочку ГАЙДЫ = АКТИВНОСТИ + МЕТРИКИ + АРХИВ"""
        
        print(f"\n🎯 ЭТАП 3: НАСТРОЙКА ГАЙДЫ + АКТИВНОСТИ + АРХИВ")
        print("=" * 60)
        
        # 1. Количество использований
        print("1️⃣ Добавление поля 'Количество использований'...")
        success1 = self._add_number_property(
            self.databases['guides'],
            "Количество использований"
        )
        
        # 2. Статус актуальности
        print("2️⃣ Добавление поля 'Статус актуальности'...")
        success2 = self._add_select_property(
            self.databases['guides'],
            "Статус актуальности",
            ["Актуальный", "Требует обновления", "Устарел"]
        )
        
        # 3. Дата последнего обновления
        print("3️⃣ Добавление поля 'Дата последнего обновления'...")
        success3 = self._add_date_property(
            self.databases['guides'],
            "Дата последнего обновления"
        )
        
        # 4. Автор обновления
        print("4️⃣ Добавление поля 'Автор обновления'...")
        success4 = self._add_person_property(
            self.databases['guides'],
            "Автор обновления"
        )
        
        # 5. Статус гайда
        print("5️⃣ Добавление поля 'Статус гайда'...")
        success5 = self._add_select_property(
            self.databases['guides'],
            "Статус гайда",
            ["Активный", "В доработке", "Архивный"]
        )
        
        # 6. Причина архивирования
        print("6️⃣ Добавление поля 'Причина архивирования'...")
        success6 = self._add_rich_text_property(
            self.databases['guides'],
            "Причина архивирования"
        )
        
        # 7. Заменяющий гайд
        print("7️⃣ Добавление связи 'Заменяющий гайд'...")
        success7 = self.create_relation_property(
            self.databases['guides'],
            "Заменяющий гайд",
            self.databases['guides']  # рекурсивная связь
        )
        
        return success1 and success2 and success3 and success4 and success5 and success6 and success7
    
    def _add_select_property(self, database_id, property_name, options):
        """Добавляет select property"""
        
        property_data = {
            "name": property_name,
            "type": "select",
            "select": {
                "options": [{"name": option} for option in options]
            }
        }
        
        try:
            response = requests.patch(
                f"https://api.notion.com/v1/databases/{database_id}",
                headers=self.headers,
                json={
                    "properties": {
                        property_name: property_data
                    }
                }
            )
            
            if response.status_code == 200:
                print(f"   ✅ {property_name}")
                return True
            else:
                print(f"   ❌ {property_name}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {property_name}: {e}")
            return False
    
    def _add_rich_text_property(self, database_id, property_name):
        """Добавляет rich_text property"""
        
        property_data = {
            "name": property_name,
            "type": "rich_text"
        }
        
        try:
            response = requests.patch(
                f"https://api.notion.com/v1/databases/{database_id}",
                headers=self.headers,
                json={
                    "properties": {
                        property_name: property_data
                    }
                }
            )
            
            if response.status_code == 200:
                print(f"   ✅ {property_name}")
                return True
            else:
                print(f"   ❌ {property_name}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {property_name}: {e}")
            return False
    
    def _add_number_property(self, database_id, property_name):
        """Добавляет number property"""
        
        property_data = {
            "name": property_name,
            "type": "number"
        }
        
        try:
            response = requests.patch(
                f"https://api.notion.com/v1/databases/{database_id}",
                headers=self.headers,
                json={
                    "properties": {
                        property_name: property_data
                    }
                }
            )
            
            if response.status_code == 200:
                print(f"   ✅ {property_name}")
                return True
            else:
                print(f"   ❌ {property_name}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {property_name}: {e}")
            return False
    
    def _add_date_property(self, database_id, property_name):
        """Добавляет date property"""
        
        property_data = {
            "name": property_name,
            "type": "date"
        }
        
        try:
            response = requests.patch(
                f"https://api.notion.com/v1/databases/{database_id}",
                headers=self.headers,
                json={
                    "properties": {
                        property_name: property_data
                    }
                }
            )
            
            if response.status_code == 200:
                print(f"   ✅ {property_name}")
                return True
            else:
                print(f"   ❌ {property_name}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {property_name}: {e}")
            return False
    
    def _add_person_property(self, database_id, property_name):
        """Добавляет person property"""
        
        property_data = {
            "name": property_name,
            "type": "people"
        }
        
        try:
            response = requests.patch(
                f"https://api.notion.com/v1/databases/{database_id}",
                headers=self.headers,
                json={
                    "properties": {
                        property_name: property_data
                    }
                }
            )
            
            if response.status_code == 200:
                print(f"   ✅ {property_name}")
                return True
            else:
                print(f"   ❌ {property_name}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {property_name}: {e}")
            return False
    
    def run_full_setup(self):
        """Запускает полную настройку всех цепочек"""
        
        print("🚀 НАСТРОЙКА БИЗНЕС-ЦЕПОЧЕК")
        print("🎯 Автоматизация связок между базами")
        print("=" * 80)
        
        # Анализ текущего состояния
        relations_map = self.analyze_current_relations()
        
        # Этап 1: Концепты + Тесты
        print(f"\n📋 ЭТАП 1: КОНЦЕПТЫ + ТЕСТЫ")
        concept_success = self.setup_concept_testing_chain()
        
        # Этап 2: Задачи + Материалы + Гайды
        print(f"\n📋 ЭТАП 2: ЗАДАЧИ + МАТЕРИАЛЫ + ГАЙДЫ")
        tasks_success = self.setup_tasks_integration_chain()
        
        # Этап 3: Гайды + Активности + Архив
        print(f"\n📋 ЭТАП 3: ГАЙДЫ + АКТИВНОСТИ + АРХИВ")
        guides_success = self.setup_guides_activity_chain()
        
        # Итоги
        print(f"\n📊 ИТОГИ НАСТРОЙКИ")
        print("=" * 50)
        
        if concept_success:
            print("✅ ЭТАП 1: Концепты + Тесты - УСПЕШНО")
        else:
            print("❌ ЭТАП 1: Концепты + Тесты - ОШИБКИ")
        
        if tasks_success:
            print("✅ ЭТАП 2: Задачи + Материалы + Гайды - УСПЕШНО")
        else:
            print("❌ ЭТАП 2: Задачи + Материалы + Гайды - ОШИБКИ")
        
        if guides_success:
            print("✅ ЭТАП 3: Гайды + Активности + Архив - УСПЕШНО")
        else:
            print("❌ ЭТАП 3: Гайды + Активности + Архив - ОШИБКИ")
        
        if concept_success and tasks_success and guides_success:
            print(f"\n🎉 ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ УСПЕШНО!")
            print("🚀 Бизнес-цепочки готовы к использованию")
        else:
            print(f"\n⚠️ ЕСТЬ ОШИБКИ В НАСТРОЙКЕ")
            print("🔧 Проверьте логи и повторите неудачные этапы")
        
        return concept_success and tasks_success and guides_success

def main():
    """Главная функция"""
    
    try:
        setup = BusinessChainSetup()
        success = setup.run_full_setup()
        
        if success:
            print(f"\n✅ НАСТРОЙКА ЗАВЕРШЕНА!")
            print("📖 Смотрите BUSINESS_CHAIN_SETUP.md для деталей")
        else:
            print(f"\n❌ НАСТРОЙКА НЕ ЗАВЕРШЕНА")
            print("🔧 Проверьте ошибки и повторите")
    
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 