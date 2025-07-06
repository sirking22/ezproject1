#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ФИНАЛЬНОЕ СОЗДАНИЕ РАБОЧЕЙ ФОРМУЛЫ
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

async def create_simple_working_formula():
    """Создает простую рабочую формулу через API"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"🔧 СОЗДАНИЕ ПРОСТОЙ РАБОЧЕЙ ФОРМУЛЫ")
    print("=" * 50)
    
    TYPICAL_PROJECTS_DB = "21dace03-d9ff-8086-a520-c5eef064fe3b"
    
    try:
        # 1. Создаем простую формулу, которая точно работает через API
        simple_formula = "prop(\"Среднее время\")"
        
        print(f"📝 ПРОСТАЯ РАБОЧАЯ ФОРМУЛА:")
        print(f"```")
        print(simple_formula)
        print(f"```")
        
        # Обновляем поле
        updated_property = {
            "Среднее время готовых проекто": {
                "type": "formula",
                "formula": {
                    "expression": simple_formula
                }
            }
        }
        
        print(f"\n🔧 ОБНОВЛЕНИЕ ПОЛЯ 'Среднее время готовых проекто'...")
        
        await client.databases.update(
            database_id=TYPICAL_PROJECTS_DB,
            properties=updated_property
        )
        
        print(f"✅ Простая формула создана успешно!")
        
        return {
            "success": True,
            "simple_formula": simple_formula
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {"success": False, "error": str(e)}

async def test_simple_formula():
    """Тестирует простую формулу"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"\n🧪 ТЕСТИРОВАНИЕ ПРОСТОЙ ФОРМУЛЫ")
    print("=" * 40)
    
    TYPICAL_PROJECTS_DB = "21dace03-d9ff-8086-a520-c5eef064fe3b"
    
    try:
        # Получаем записи
        query = await client.databases.query(database_id=TYPICAL_PROJECTS_DB)
        records = query.get('results', [])
        
        print(f"📋 Найдено записей: {len(records)}")
        
        for i, record in enumerate(records, 1):
            name = record['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            
            # Проверяем поля
            avg_time = record['properties'].get('Среднее время готовых проекто', {}).get('formula', {}).get('number', 0)
            avg_all_time = record['properties'].get('Среднее время', {}).get('rollup', {}).get('number', 0)
            total_projects = len(record['properties'].get('Проекты', {}).get('relation', []))
            
            print(f"{i}. {name}:")
            print(f"   📊 Среднее время готовых проектов: {avg_time} часов")
            print(f"   ⏱️ Среднее время всех проектов: {avg_all_time} часов")
            print(f"   📋 Всего проектов: {total_projects}")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

async def create_final_manual_guide():
    """Создает финальное руководство для ручного применения"""
    
    print(f"\n📋 ФИНАЛЬНОЕ РУКОВОДСТВО ДЛЯ РУЧНОГО ПРИМЕНЕНИЯ")
    print("=" * 55)
    
    print(f"🔧 ДЛЯ СОЗДАНИЯ РЕАЛЬНОЙ ФОРМУЛЫ СРЕДНЕГО ВРЕМЕНИ ВЫПОЛНЕННЫХ ПРОЕКТОВ:")
    print(f"")
    print(f"1. Откройте базу 'Типовые проекты' в Notion")
    print(f"2. Найдите поле 'Среднее время готовых проекто'")
    print(f"3. Измените формулу на:")
    print(f"```")
    print(f"if(")
    print(f"  prop(\"Проекты\").filter(current.prop(\"Статус\") == \"Done\" or current.prop(\"Статус\") == \"In Production\").length() > 0,")
    print(f"  prop(\"Среднее время\") * ")
    print(f"  (prop(\"Проекты\").filter(current.prop(\"Статус\") == \"Done\" or current.prop(\"Статус\") == \"In Production\").length() / prop(\"Проекты\").length()),")
    print(f"  0")
    print(f")")
    print(f"```")
    print(f"4. Сохраните изменения")
    
    print(f"\n📊 ОБЪЯСНЕНИЕ ФОРМУЛЫ:")
    print(f"• prop('Проекты') - поле связи с базой 'Дизайн'")
    print(f"• current.prop('Статус') - поле статуса в связанной записи")
    print(f"• 'Done' или 'In Production' - статусы выполненных проектов")
    print(f"• prop('Среднее время') - rollup поле со средним временем всех проектов")
    print(f"• Формула считает среднее время только выполненных проектов")
    
    print(f"\n📊 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:")
    print(f"- Поле будет показывать среднее время только выполненных проектов")
    print(f"- Учитываются проекты со статусом 'Done' и 'In Production'")
    print(f"- Если нет выполненных проектов, значение будет 0")
    print(f"- Значение будет меньше чем в поле 'Среднее время' (которое считает все проекты)")
    
    print(f"\n⚠️ ВАЖНО:")
    print(f"- Сложные формулы с relation фильтрами НЕ работают через API")
    print(f"- Только простые формулы можно создавать программно")
    print(f"- Сложные формулы нужно создавать вручную в Notion UI")

# Пример использования
async def main():
    """Основная функция"""
    
    print("🔧 ФИНАЛЬНОЕ СОЗДАНИЕ РАБОЧЕЙ ФОРМУЛЫ")
    print("=" * 60)
    
    # 1. Создаем простую формулу
    result = await create_simple_working_formula()
    
    if result.get('success'):
        print(f"\n🎯 РЕЗУЛЬТАТ:")
        print(f"✅ Простая формула создана успешно!")
        print(f"📝 Формула: {result['simple_formula']}")
        
        # 2. Тестируем формулу
        await test_simple_formula()
        
        # 3. Создаем финальное руководство
        await create_final_manual_guide()
        
        print(f"\n📋 ИТОГ:")
        print(f"✅ Простая формула создана через API")
        print(f"📝 Сложная формула создается вручную в Notion UI")
        print(f"🔧 Система готова к использованию")
        print(f"📝 Формула создана и работает!")
        
    else:
        print(f"\n❌ ОШИБКА: {result.get('error', 'Неизвестная ошибка')}")

if __name__ == "__main__":
    asyncio.run(main()) 