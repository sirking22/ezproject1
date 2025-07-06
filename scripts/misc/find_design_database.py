#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ПОИСК БАЗЫ ДАННЫХ С ПОЛЕМ "ДИЗАЙН"
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

async def find_design_database():
    """Находит базу данных с полем 'Дизайн'"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"🔍 ПОИСК БАЗЫ С ПОЛЕМ 'ДИЗАЙН'")
    print("=" * 50)
    
    try:
        # Поиск всех баз данных
        search_response = await client.search(
            query="",
            filter={"property": "object", "value": "database"}
        )
        
        databases = search_response.get('results', [])
        print(f"Найдено баз данных: {len(databases)}")
        
        design_databases = []
        
        for db in databases:
            db_id = db['id']
            db_title = db.get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            
            try:
                db_schema = await client.databases.retrieve(database_id=db_id)
                properties = db_schema.get('properties', {})
                
                # Ищем поле "Дизайн"
                if "Дизайн" in properties:
                    prop_data = properties["Дизайн"]
                    prop_type = prop_data.get('type', 'unknown')
                    
                    print(f"✅ НАЙДЕНА БАЗА: {db_title}")
                    print(f"   📋 ID: {db_id}")
                    print(f"   🔗 Поле 'Дизайн': {prop_type}")
                    
                    if prop_type == 'relation':
                        relation_info = prop_data.get('relation', {})
                        target_db = relation_info.get('database_id', 'unknown')
                        print(f"   🎯 Связана с базой: {target_db}")
                        
                        # Проверяем связанную базу
                        try:
                            target_schema = await client.databases.retrieve(database_id=target_db)
                            target_title = target_schema.get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
                            print(f"   📊 Название связанной базы: {target_title}")
                            
                            # Проверяем поля в связанной базе
                            target_properties = target_schema.get('properties', {})
                            print(f"   📋 Поля в связанной базе:")
                            for prop_name, prop_info in target_properties.items():
                                prop_type = prop_info.get('type', 'unknown')
                                print(f"      • {prop_name} ({prop_type})")
                            
                        except Exception as e:
                            print(f"   ❌ Ошибка получения связанной базы: {e}")
                    
                    design_databases.append({
                        'id': db_id,
                        'title': db_title,
                        'design_field_type': prop_type
                    })
                    
            except Exception as e:
                print(f"❌ Ошибка получения схемы {db_title}: {e}")
                continue
        
        print(f"\n📊 ИТОГИ ПОИСКА:")
        print(f"Найдено баз с полем 'Дизайн': {len(design_databases)}")
        
        if design_databases:
            print(f"\n📋 СПИСОК БАЗ:")
            for i, db in enumerate(design_databases, 1):
                print(f"{i}. {db['title']} ({db['id']}) - {db['design_field_type']}")
        
        return design_databases
        
    except Exception as e:
        print(f"❌ ОБЩАЯ ОШИБКА: {e}")
        return []

async def test_formula_on_design_database():
    """Тестирует формулу на базе с полем 'Дизайн'"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"\n🧪 ТЕСТИРОВАНИЕ НА БАЗЕ С ПОЛЕМ 'ДИЗАЙН'")
    print("=" * 55)
    
    # Найдем базу с полем "Дизайн"
    design_dbs = await find_design_database()
    
    if not design_dbs:
        print("❌ Не найдено баз с полем 'Дизайн'")
        return
    
    # Берем первую подходящую базу
    test_db = design_dbs[0]
    print(f"\n🎯 ТЕСТИРУЕМ НА БАЗЕ: {test_db['title']} ({test_db['id']})")
    
    # Упрощенная версия формулы пользователя
    test_formulas = [
        {
            "name": "Простой map",
            "formula": 'prop("Дизайн").map(current.prop("Часы"))'
        },
        {
            "name": "Простой filter",
            "formula": 'prop("Дизайн").filter(current.prop("Статус") == "Done")'
        },
        {
            "name": "Map с filter",
            "formula": 'prop("Дизайн").filter(current.prop("Статус") == "Done").map(current.prop("Часы"))'
        },
        {
            "name": "Сумма с map",
            "formula": 'prop("Дизайн").map(current.prop("Часы")).sum()'
        }
    ]
    
    results = []
    for i, test in enumerate(test_formulas, 1):
        print(f"\n📝 ТЕСТ {i}: {test['name']}")
        print(f"Формула: {test['formula']}")
        
        test_field_name = f"Тест_Дизайн_{i}"
        
        test_property = {
            test_field_name: {
                "type": "formula",
                "formula": {
                    "expression": test['formula']
                }
            }
        }
        
        try:
            await client.databases.update(
                database_id=test_db['id'],
                properties=test_property
            )
            print(f"✅ УСПЕШНО!")
            results.append({"test": test['name'], "status": "success"})
            
            # Удаляем тестовое поле
            await client.databases.update(
                database_id=test_db['id'],
                properties={test_field_name: None}
            )
            
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            results.append({"test": test['name'], "status": "error", "error": str(e)})
    
    # Анализ результатов
    print(f"\n📊 РЕЗУЛЬТАТЫ НА БАЗЕ С 'ДИЗАЙН':")
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    
    print(f"✅ Успешно: {len(successful)}")
    print(f"❌ Ошибки: {len(failed)}")
    
    if successful:
        print(f"\n🎉 РАБОТАЮЩИЕ ФОРМУЛЫ:")
        for success in successful:
            print(f"   • {success['test']}")
    
    if failed:
        print(f"\n❌ НЕРАБОТАЮЩИЕ ФОРМУЛЫ:")
        for fail in failed:
            print(f"   • {fail['test']}: {fail['error']}")
    
    return results

async def main():
    """Основная функция"""
    
    print("🔍 ПОИСК И ТЕСТИРОВАНИЕ БАЗ С ПОЛЕМ 'ДИЗАЙН'")
    print("=" * 60)
    
    # 1. Поиск баз с полем "Дизайн"
    design_dbs = await find_design_database()
    
    # 2. Тестирование на найденной базе
    if design_dbs:
        results = await test_formula_on_design_database()
        
        print(f"\n🎯 ВЫВОДЫ:")
        print("=" * 20)
        
        if any(r['status'] == 'success' for r in results):
            print(f"✅ Сложные формулы РАБОТАЮТ на правильной базе!")
            print(f"🔧 Проблема была в выборе базы для тестирования")
        else:
            print(f"❌ Сложные формулы НЕ работают даже на правильной базе")
            print(f"🔧 API действительно имеет ограничения")
    else:
        print(f"❌ Не найдено баз с полем 'Дизайн'")

if __name__ == "__main__":
    asyncio.run(main()) 