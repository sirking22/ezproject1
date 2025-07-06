#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 АНАЛИЗ БАЗЫ "ТИПОВЫЕ ПРОЕКТЫ" И СОЗДАНИЕ ФОРМУЛЫ
"""

import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

async def analyze_typical_projects_database():
    """Анализирует структуру базы 'Типовые проекты'"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print(f"🔍 АНАЛИЗ БАЗЫ 'ТИПОВЫЕ ПРОЕКТЫ'")
    print("=" * 50)
    
    # ID базы "Типовые проекты"
    TYPICAL_PROJECTS_DB = "21dace03-d9ff-8086-a520-c5eef064fe3b"
    
    try:
        # Получаем схему базы
        db_schema = await client.databases.retrieve(database_id=TYPICAL_PROJECTS_DB)
        properties = db_schema.get('properties', {})
        
        print(f"📋 ПОЛЯ В БАЗЕ 'ТИПОВЫЕ ПРОЕКТЫ':")
        print(f"Всего полей: {len(properties)}")
        print()
        
        relation_fields = []
        status_fields = []
        number_fields = []
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get('type', 'unknown')
            
            print(f"• {prop_name} ({prop_type})")
            
            if prop_type == 'relation':
                relation_info = prop_data.get('relation', {})
                target_db = relation_info.get('database_id', 'unknown')
                print(f"  🔗 Связана с базой: {target_db}")
                relation_fields.append({
                    'name': prop_name,
                    'target_db': target_db,
                    'data': prop_data
                })
                
                # Получаем информацию о связанной базе
                try:
                    target_schema = await client.databases.retrieve(database_id=target_db)
                    target_title = target_schema.get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
                    print(f"  📊 Название связанной базы: {target_title}")
                    
                    # Проверяем поля в связанной базе
                    target_properties = target_schema.get('properties', {})
                    print(f"  📋 Поля в связанной базе:")
                    for target_prop_name, target_prop_info in target_properties.items():
                        target_prop_type = target_prop_info.get('type', 'unknown')
                        print(f"      - {target_prop_name} ({target_prop_type})")
                        
                        if target_prop_type == 'status':
                            status_fields.append(f"{target_prop_name} (в {target_title})")
                        elif target_prop_type == 'number':
                            number_fields.append(f"{target_prop_name} (в {target_title})")
                    
                except Exception as e:
                    print(f"  ❌ Ошибка получения связанной базы: {e}")
            
            elif prop_type == 'status':
                status_options = prop_data.get('status', {}).get('options', [])
                print(f"  📊 Статусы: {[opt.get('name') for opt in status_options]}")
                status_fields.append(prop_name)
            
            elif prop_type == 'number':
                number_fields.append(prop_name)
            
            print()
        
        print(f"📊 АНАЛИЗ ДЛЯ СОЗДАНИЯ ФОРМУЛЫ:")
        print(f"🔗 Relation поля: {len(relation_fields)}")
        for rel in relation_fields:
            print(f"   • {rel['name']} → {rel['target_db']}")
        
        print(f"📊 Статус поля: {status_fields}")
        print(f"🔢 Числовые поля: {number_fields}")
        
        return {
            'relation_fields': relation_fields,
            'status_fields': status_fields,
            'number_fields': number_fields,
            'properties': properties
        }
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return None

async def suggest_formulas(analysis):
    """Предлагает формулы на основе анализа базы"""
    
    print(f"\n🧮 ПРЕДЛОЖЕНИЯ ФОРМУЛ")
    print("=" * 50)
    
    if not analysis:
        print("❌ Нет данных для анализа")
        return
    
    relation_fields = analysis['relation_fields']
    status_fields = analysis['status_fields']
    number_fields = analysis['number_fields']
    
    print(f"🎯 ВОЗМОЖНЫЕ ФОРМУЛЫ:")
    print()
    
    # Формула 1: Среднее время по проектам со статусом "Done"
    if relation_fields and any('Done' in status for status in status_fields):
        print(f"1️⃣ СРЕДНЕЕ ВРЕМЯ ПО ЗАВЕРШЕННЫМ ПРОЕКТАМ:")
        print(f"   prop('Проекты').filter(current.prop('Статус') == 'Done').map(current.prop('Время')).average()")
        print()
    
    # Формула 2: Сумма времени по проектам в продакшене
    if relation_fields and any('Production' in status for status in status_fields):
        print(f"2️⃣ СУММА ВРЕМЕНИ ПО ПРОЕКТАМ В ПРОДАКШЕНЕ:")
        print(f"   prop('Проекты').filter(current.prop('Статус') == 'In Production').map(current.prop('Время')).sum()")
        print()
    
    # Формула 3: Количество активных проектов
    if relation_fields:
        print(f"3️⃣ КОЛИЧЕСТВО АКТИВНЫХ ПРОЕКТОВ:")
        print(f"   prop('Проекты').filter(current.prop('Статус') == 'In Progress').length()")
        print()
    
    # Формула 4: Среднее время по всем проектам
    if relation_fields and number_fields:
        print(f"4️⃣ СРЕДНЕЕ ВРЕМЯ ПО ВСЕМ ПРОЕКТАМ:")
        print(f"   prop('Проекты').map(current.prop('Часы')).average()")
        print()
    
    # Формула 5: Время за текущий месяц
    if relation_fields:
        print(f"5️⃣ ВРЕМЯ ЗА ТЕКУЩИЙ МЕСЯЦ:")
        print(f"   prop('Проекты').filter(current.prop('Дата').formatDate('M') == formatDate(now(), 'M') and current.prop('Дата').formatDate('YYYY') == formatDate(now(), 'YYYY')).map(current.prop('Часы')).sum()")
        print()

async def create_manual_formula_guide():
    """Создает руководство по созданию формулы вручную"""
    
    print(f"\n📝 РУКОВОДСТВО ПО СОЗДАНИЮ ФОРМУЛЫ ВРУЧНУЮ")
    print("=" * 60)
    
    print(f"🎯 ШАГИ ДЛЯ СОЗДАНИЯ ФОРМУЛЫ В NOTION UI:")
    print()
    
    print(f"1️⃣ ОТКРОЙТЕ БАЗУ 'ТИПОВЫЕ ПРОЕКТЫ'")
    print(f"   • Перейдите в Notion")
    print(f"   • Найдите базу 'Типовые проекты'")
    print()
    
    print(f"2️⃣ СОЗДАЙТЕ НОВОЕ ПОЛЕ")
    print(f"   • Нажмите '+' рядом с заголовками")
    print(f"   • Выберите 'Formula'")
    print(f"   • Дайте название полю (например, 'Среднее время')")
    print()
    
    print(f"3️⃣ ВВЕДИТЕ ФОРМУЛУ")
    print(f"   • В поле формулы введите одну из предложенных формул")
    print(f"   • Например:")
    print(f"     prop('Проекты').filter(current.prop('Статус') == 'Done').map(current.prop('Часы')).average()")
    print()
    
    print(f"4️⃣ ПРОВЕРЬТЕ РЕЗУЛЬТАТ")
    print(f"   • Нажмите Enter или кликните вне поля")
    print(f"   • Убедитесь, что формула работает корректно")
    print()
    
    print(f"5️⃣ НАСТРОЙТЕ ОТОБРАЖЕНИЕ")
    print(f"   • При необходимости измените формат числа")
    print(f"   • Настройте количество знаков после запятой")
    print()

async def main():
    """Основная функция"""
    
    print("🔍 АНАЛИЗ И СОЗДАНИЕ ФОРМУЛЫ ДЛЯ 'ТИПОВЫЕ ПРОЕКТЫ'")
    print("=" * 70)
    
    # 1. Анализируем структуру базы
    analysis = await analyze_typical_projects_database()
    
    # 2. Предлагаем формулы
    await suggest_formulas(analysis)
    
    # 3. Создаем руководство
    await create_manual_formula_guide()
    
    print(f"\n🎯 ГОТОВО!")
    print("=" * 20)
    print(f"📝 Теперь вы можете создать формулу вручную в Notion UI")
    print(f"🔧 Используйте предложенные формулы как основу")
    print(f"✅ Все сложные операции поддерживаются в UI")

if __name__ == "__main__":
    asyncio.run(main()) 