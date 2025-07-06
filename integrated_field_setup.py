#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ИНТЕГРИРОВАННАЯ НАСТРОЙКА ПОЛЕЙ

Использует актуальные ресурсы кодовой базы:
- src/services/notion/service.py (NotionService)
- src/config.py (Settings)
- notion_client для корректной работы с API
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from dotenv import load_dotenv

# Добавляем путь к src для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.notion.service import NotionService
from src.config import Settings

load_dotenv()

class IntegratedFieldSetup:
    """Интегрированная настройка полей с использованием актуальных ресурсов"""
    
    def __init__(self):
        """Инициализация с использованием актуальных настроек"""
        self.settings = Settings()
        self.notion_service = NotionService()
        
        # ID баз данных из актуальной конфигурации
        self.databases = {
            'concepts': '6fc4322e6d0c45a6b37ac49b818a063a',
            'guides': '47c6086858d442ebaeceb4fad1b23ba3',
            'tasks': 'd09df250ce7e4e0d9fbe4e036d320def',
            'materials': '1d9ace03d9ff804191a4d35aeedcbbd4',
            'kpi': '1d6ace03d9ff80bfb809ed21dfd2150c'
        }
    
    async def initialize(self):
        """Инициализация сервиса"""
        await self.notion_service.initialize()
        print("✅ NotionService инициализирован")
    
    async def cleanup(self):
        """Очистка ресурсов"""
        await self.notion_service.cleanup()
    
    def create_property_schema(self, field_name: str, field_type: str, options: List[str] = None) -> Dict[str, Any]:
        """Создает корректную схему свойства для Notion API"""
        
        if field_type == 'select':
            return {
                "name": field_name,
                "type": "select",
                "select": {
                    "options": [{"name": option} for option in options]
                }
            }
        elif field_type == 'rich_text':
            return {
                "name": field_name,
                "type": "rich_text"
            }
        elif field_type == 'number':
            return {
                "name": field_name,
                "type": "number"
            }
        elif field_type == 'date':
            return {
                "name": field_name,
                "type": "date"
            }
        elif field_type == 'people':
            return {
                "name": field_name,
                "type": "people"
            }
        elif field_type == 'relation':
            return {
                "name": field_name,
                "type": "relation",
                "relation": {
                    "database_id": options  # options содержит target_db_id
                }
            }
        else:
            raise ValueError(f"Неизвестный тип поля: {field_type}")
    
    async def add_fields_to_database(self, database_name: str, fields: List[Dict[str, Any]]) -> int:
        """Добавляет поля в базу данных используя NotionService"""
        
        database_id = self.databases[database_name]
        print(f"\n🎯 ДОБАВЛЕНИЕ ПОЛЕЙ В {database_name.upper()}")
        print("=" * 60)
        
        # Создаем схему свойств
        properties = {}
        for field in fields:
            property_schema = self.create_property_schema(
                field['name'], 
                field['type'], 
                field.get('options')
            )
            properties[field['name']] = property_schema
        
        try:
            # Используем актуальный метод update_database
            await self.notion_service.update_database(database_id, properties)
            print(f"✅ Все поля успешно добавлены в {database_name.upper()}")
            return len(fields)
            
        except Exception as e:
            print(f"❌ Ошибка добавления полей в {database_name.upper()}: {e}")
            return 0
    
    async def setup_concepts_testing_fields(self) -> int:
        """Настраивает поля тестирования для концептов"""
        
        fields = [
            {
                'name': 'Test Status',
                'type': 'select',
                'options': ['Not Tested', 'In Testing', 'Success', 'Failed']
            },
            {
                'name': 'Test Results',
                'type': 'rich_text'
            },
            {
                'name': 'Recommendation',
                'type': 'select',
                'options': ['Implement', 'Improve', 'Reject']
            },
            {
                'name': 'Test Start Date',
                'type': 'date'
            },
            {
                'name': 'Test End Date',
                'type': 'date'
            },
            {
                'name': 'Success Metrics',
                'type': 'rich_text'
            }
        ]
        
        return await self.add_fields_to_database('concepts', fields)
    
    async def setup_guides_activity_fields(self) -> int:
        """Настраивает поля активности для гайдов"""
        
        fields = [
            {
                'name': 'Usage Count',
                'type': 'number'
            },
            {
                'name': 'Relevance Status',
                'type': 'select',
                'options': ['Relevant', 'Needs Update', 'Outdated']
            },
            {
                'name': 'Last Update Date',
                'type': 'date'
            },
            {
                'name': 'Update Author',
                'type': 'people'
            },
            {
                'name': 'Guide Status',
                'type': 'select',
                'options': ['Active', 'In Progress', 'Archived']
            },
            {
                'name': 'Archive Reason',
                'type': 'rich_text'
            }
        ]
        
        return await self.add_fields_to_database('guides', fields)
    
    async def setup_additional_relations(self) -> int:
        """Настраивает дополнительные связи"""
        
        print("\n🎯 ДОБАВЛЕНИЕ ДОПОЛНИТЕЛЬНЫХ СВЯЗЕЙ")
        print("=" * 60)
        
        relations = [
            {
                'database': 'guides',
                'name': 'Replacing Guide',
                'target': 'guides'  # рекурсивная связь
            }
        ]
        
        total_added = 0
        for relation in relations:
            database_id = self.databases[relation['database']]
            target_db_id = self.databases[relation['target']]
            
            properties = {
                relation['name']: self.create_property_schema(
                    relation['name'], 
                    'relation', 
                    target_db_id
                )
            }
            
            try:
                await self.notion_service.update_database(database_id, properties)
                print(f"✅ Связь '{relation['name']}' добавлена в {relation['database'].upper()}")
                total_added += 1
            except Exception as e:
                print(f"❌ Ошибка добавления связи '{relation['name']}': {e}")
        
        return total_added
    
    async def verify_fields_added(self) -> Dict[str, int]:
        """Проверяет, какие поля были добавлены"""
        
        print("\n🔍 ПРОВЕРКА ДОБАВЛЕННЫХ ПОЛЕЙ")
        print("=" * 60)
        
        verification_results = {}
        
        for db_name, db_id in self.databases.items():
            try:
                database = await self.notion_service.get_database(db_id)
                properties = database.properties
                
                # Ищем новые поля
                new_fields = [
                    'Test Status', 'Test Results', 'Recommendation', 
                    'Test Start Date', 'Test End Date', 'Success Metrics',
                    'Usage Count', 'Relevance Status', 'Last Update Date',
                    'Update Author', 'Guide Status', 'Archive Reason'
                ]
                
                found_count = 0
                for field_name in new_fields:
                    if field_name in properties:
                        found_count += 1
                
                verification_results[db_name] = found_count
                print(f"📊 {db_name.upper()}: {found_count} новых полей найдено")
                
            except Exception as e:
                print(f"❌ Ошибка проверки {db_name.upper()}: {e}")
                verification_results[db_name] = 0
        
        return verification_results
    
    async def run_setup(self):
        """Запускает полную настройку полей"""
        
        print("🚀 ИНТЕГРИРОВАННАЯ НАСТРОЙКА ПОЛЕЙ")
        print("🎯 Использует актуальные ресурсы кодовой базы")
        print("=" * 80)
        
        try:
            # Инициализация
            await self.initialize()
            
            # Этап 1: Поля тестирования в концептах
            concepts_success = await self.setup_concepts_testing_fields()
            
            # Этап 2: Поля активности в гайдах
            guides_success = await self.setup_guides_activity_fields()
            
            # Этап 3: Дополнительные связи
            relations_success = await self.setup_additional_relations()
            
            # Проверка результатов
            verification = await self.verify_fields_added()
            
            # Итоги
            print(f"\n📊 ФИНАЛЬНЫЕ ИТОГИ")
            print("=" * 50)
            print(f"✅ CONCEPTS: {concepts_success} полей добавлено")
            print(f"✅ GUIDES: {guides_success} полей добавлено")
            print(f"✅ Связи: {relations_success} связей добавлено")
            
            total_verified = sum(verification.values())
            print(f"🔍 Проверено полей: {total_verified}")
            
            if total_verified > 0:
                print("🎉 Настройка полей завершена успешно!")
            else:
                print("⚠️ Поля не были добавлены")
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
        
        finally:
            # Очистка ресурсов
            await self.cleanup()

async def main():
    """Главная функция"""
    
    setup = IntegratedFieldSetup()
    await setup.run_setup()

if __name__ == "__main__":
    asyncio.run(main()) 