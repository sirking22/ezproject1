#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ИНТЕРАКТИВНАЯ НАСТРОЙКА БИЗНЕС-ЦЕПОЧЕК

Пошаговое добавление полей с запросом согласия пользователя
"""

import os
import requests
import json
from dotenv import load_dotenv

Аудио
Виктор Васильев. «Белая книга»
Максим Суслов

load_dotenv()

class InteractiveSetup:
    """Интерактивная настройка полей"""
    
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
            'tasks': 'd09df250ce7e4e0d9fbe4e036d320def',
            'materials': '1d9ace03d9ff804191a4d35aeedcbbd4',
            'guides': '47c6086858d442ebaeceb4fad1b23ba3',
            'kpi': '1d6ace03d9ff80bfb809ed21dfd2150c'
        }
    
    def ask_confirmation(self, question):
        """Запрашивает подтверждение у пользователя"""
        while True:
            response = input(f"\n{question} (да/нет): ").lower().strip()
            if response in ['да', 'y', 'yes', 'д']:
                return True
            elif response in ['нет', 'n', 'no', 'н']:
                return False
            else:
                print("Пожалуйста, ответьте 'да' или 'нет'")
    
    def add_field_with_confirmation(self, database_name, field_name, field_type, options=None):
        """Добавляет поле с запросом подтверждения"""
        
        question = f"Добавить поле '{field_name}' ({field_type}) в базу {database_name.upper()}?"
        
        if self.ask_confirmation(question):
            success = self._add_field(database_name, field_name, field_type, options)
            if success:
                print(f"✅ Поле '{field_name}' добавлено успешно!")
            else:
                print(f"❌ Ошибка добавления поля '{field_name}'")
            return success
        else:
            print(f"⏭️ Поле '{field_name}' пропущено")
            return False
    
    def _add_field(self, database_name, field_name, field_type, options=None):
        """Добавляет поле в базу данных"""
        
        database_id = self.databases[database_name]
        
        if field_type == 'relation':
            property_data = {
                "name": field_name,
                "type": "relation",
                "relation": {
                    "database_id": options  # options содержит target_db_id
                }
            }
        elif field_type == 'select':
            property_data = {
                "name": field_name,
                "type": "select",
                "select": {
                    "options": [{"name": option} for option in options]
                }
            }
        elif field_type == 'rich_text':
            property_data = {
                "name": field_name,
                "type": "rich_text"
            }
        elif field_type == 'number':
            property_data = {
                "name": field_name,
                "type": "number"
            }
        elif field_type == 'date':
            property_data = {
                "name": field_name,
                "type": "date"
            }
        elif field_type == 'person':
            property_data = {
                "name": field_name,
                "type": "people"
            }
        else:
            print(f"❌ Неизвестный тип поля: {field_type}")
            return False
        
        try:
            response = requests.patch(
                f"https://api.notion.com/v1/databases/{database_id}",
                headers=self.headers,
                json={
                    "properties": {
                        field_name: property_data
                    }
                }
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"   Ошибка API: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   Ошибка: {e}")
            return False
    
    def setup_concepts_testing_fields(self):
        """Настраивает поля тестирования для концептов"""
        
        print("\n🎯 ЭТАП 1: ПОЛЯ ТЕСТИРОВАНИЯ В CONCEPTS")
        print("=" * 60)
        
        # Поля для тестирования концептов
        fields_to_add = [
            {
                'name': 'Статус тестирования',
                'type': 'select',
                'options': ['Не тестировался', 'В тестировании', 'Успешен', 'Провален']
            },
            {
                'name': 'Результаты теста',
                'type': 'rich_text'
            },
            {
                'name': 'Рекомендация',
                'type': 'select',
                'options': ['Внедрять', 'Доработать', 'Отклонить']
            },
            {
                'name': 'Дата начала тестирования',
                'type': 'date'
            },
            {
                'name': 'Дата завершения тестирования',
                'type': 'date'
            }
        ]
        
        added_count = 0
        for field in fields_to_add:
            success = self.add_field_with_confirmation(
                'concepts',
                field['name'],
                field['type'],
                field.get('options')
            )
            if success:
                added_count += 1
        
        print(f"\n📊 ИТОГИ ЭТАПА 1:")
        print(f"✅ Добавлено полей: {added_count}/{len(fields_to_add)}")
        
        return added_count > 0
    
    def setup_guides_activity_fields(self):
        """Настраивает поля активности для гайдов"""
        
        print("\n🎯 ЭТАП 2: ПОЛЯ АКТИВНОСТИ В GUIDES")
        print("=" * 60)
        
        # Поля для активности гайдов
        fields_to_add = [
            {
                'name': 'Количество использований',
                'type': 'number'
            },
            {
                'name': 'Статус актуальности',
                'type': 'select',
                'options': ['Актуальный', 'Требует обновления', 'Устарел']
            },
            {
                'name': 'Дата последнего обновления',
                'type': 'date'
            },
            {
                'name': 'Автор обновления',
                'type': 'person'
            },
            {
                'name': 'Статус гайда',
                'type': 'select',
                'options': ['Активный', 'В доработке', 'Архивный']
            },
            {
                'name': 'Причина архивирования',
                'type': 'rich_text'
            }
        ]
        
        added_count = 0
        for field in fields_to_add:
            success = self.add_field_with_confirmation(
                'guides',
                field['name'],
                field['type'],
                field.get('options')
            )
            if success:
                added_count += 1
        
        print(f"\n📊 ИТОГИ ЭТАПА 2:")
        print(f"✅ Добавлено полей: {added_count}/{len(fields_to_add)}")
        
        return added_count > 0
    
    def setup_additional_relations(self):
        """Настраивает дополнительные связи"""
        
        print("\n🎯 ЭТАП 3: ДОПОЛНИТЕЛЬНЫЕ СВЯЗИ")
        print("=" * 60)
        
        # Дополнительные связи
        relations_to_add = [
            {
                'database': 'guides',
                'name': 'Заменяющий гайд',
                'target': 'guides'  # рекурсивная связь
            }
        ]
        
        added_count = 0
        for relation in relations_to_add:
            success = self.add_field_with_confirmation(
                relation['database'],
                relation['name'],
                'relation',
                self.databases[relation['target']]
            )
            if success:
                added_count += 1
        
        print(f"\n📊 ИТОГИ ЭТАПА 3:")
        print(f"✅ Добавлено связей: {added_count}/{len(relations_to_add)}")
        
        return added_count > 0
    
    def run_interactive_setup(self):
        """Запускает интерактивную настройку"""
        
        print("🚀 ИНТЕРАКТИВНАЯ НАСТРОЙКА БИЗНЕС-ЦЕПОЧЕК")
        print("🎯 Пошаговое добавление полей с подтверждением")
        print("=" * 80)
        
        print("\n💡 Для каждого поля будет запрошено подтверждение.")
        print("💡 Ответьте 'да' для добавления, 'нет' для пропуска.")
        
        # Этап 1: Поля тестирования в концептах
        concepts_success = self.setup_concepts_testing_fields()
        
        # Этап 2: Поля активности в гайдах
        guides_success = self.setup_guides_activity_fields()
        
        # Этап 3: Дополнительные связи
        relations_success = self.setup_additional_relations()
        
        # Итоги
        print(f"\n📊 ФИНАЛЬНЫЕ ИТОГИ")
        print("=" * 50)
        
        if concepts_success:
            print("✅ Поля тестирования в CONCEPTS - НАСТРОЕНЫ")
        else:
            print("❌ Поля тестирования в CONCEPTS - НЕ НАСТРОЕНЫ")
        
        if guides_success:
            print("✅ Поля активности в GUIDES - НАСТРОЕНЫ")
        else:
            print("❌ Поля активности в GUIDES - НЕ НАСТРОЕНЫ")
        
        if relations_success:
            print("✅ Дополнительные связи - НАСТРОЕНЫ")
        else:
            print("❌ Дополнительные связи - НЕ НАСТРОЕНЫ")
        
        if concepts_success or guides_success or relations_success:
            print(f"\n🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
            print("🚀 Новые поля готовы к использованию")
        else:
            print(f"\n⚠️ НИЧЕГО НЕ БЫЛО НАСТРОЕНО")
            print("🔧 Проверьте настройки и повторите")

def main():
    """Главная функция"""
    
    try:
        setup = InteractiveSetup()
        setup.run_interactive_setup()
    
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 