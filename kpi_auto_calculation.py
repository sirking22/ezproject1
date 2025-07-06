import os
from notion_client import Client

def explain_kpi_auto_calculation():
    """Explain how to set up automatic calculation for KPI metrics"""
    
    print("🧮 АВТОМАТИЧЕСКИЙ РАСЧЕТ KPI МЕТРИК")
    print("=" * 60)
    
    print("🎯 РЕШЕНИЕ: СВЯЗЬ + ROLLUP + FORMULA")
    print("\n📊 СТРУКТУРА KPI БАЗЫ С АВТОМАТИЧЕСКИМ РАСЧЕТОМ:")
    
    kpi_fields = {
        "Название метрики": "title",
        "Категория": "select (Полиграфия, Контент, Дизайн)",
        "Команда": "select (Дизайн-команда, Контент-команда)",
        "Тип метрики": "select (Качество, Скорость, Объем)",
        "Связанные задачи": "relation → TASKS (фильтр по типу)",
        "Всего задач": "rollup → count(Связанные задачи)", 
        "Задачи в срок": "rollup → count_if(Связанные задачи, Дата <= Дедлайн)",
        "Задачи без правок": "rollup → count_if(Связанные задачи, Правки = 0)",
        "Общее время": "rollup → sum(Связанные задачи, Фактическое время)",
        "РЕЗУЛЬТАТ": "formula → автоматический расчет",
        "Целевое значение": "number",
        "Статус": "formula → сравнение с целью"
    }
    
    for field_name, field_type in kpi_fields.items():
        print(f"   • {field_name}: {field_type}")
    
    print(f"\n🔍 КОНКРЕТНЫЕ ПРИМЕРЫ ФОРМУЛ:")
    
    examples = [
        {
            "name": "% задач полиграфии в срок",
            "relation_filter": "Тип работы = Полиграфия",
            "formula": 'round(prop("Задачи в срок") / prop("Всего задач") * 100)',
            "result": "85% (автоматически)"
        },
        {
            "name": "Среднее время на листовку", 
            "relation_filter": "Тип работы = Полиграфия AND Шаблон = Листовка",
            "formula": 'round(prop("Общее время") / prop("Всего задач"), 1)',
            "result": "2.5 часа (автоматически)"
        },
        {
            "name": "Среднее количество правок на баннер",
            "relation_filter": "Тип работы = Полиграфия AND Шаблон = Баннер", 
            "formula": 'round(prop("Общие правки") / prop("Всего задач"), 1)',
            "result": "1.2 правки (автоматически)"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}:")
        print(f"   🔗 Фильтр задач: {example['relation_filter']}")
        print(f"   🧮 Формула: {example['formula']}")
        print(f"   📊 Результат: {example['result']}")
    
    print(f"\n🛠️ КАК НАСТРОИТЬ:")
    
    setup_steps = [
        "Создать relation поле 'Связанные задачи' → TASKS",
        "Для каждой KPI записи указать фильтр связанных задач",
        "Создать rollup поля из связанных задач:",
        "  - Всего задач (count)",
        "  - Задачи в срок (count with condition)",
        "  - Общее время (sum)",
        "Создать formula поле 'РЕЗУЛЬТАТ' с расчетом",
        "Создать formula поле 'Статус' для сравнения с целью"
    ]
    
    for i, step in enumerate(setup_steps, 1):
        print(f"{i}. {step}")
    
    print(f"\n💡 ВАЖНАЯ ФИШКА - ФИЛЬТРАЦИЯ RELATION:")
    print("   Каждая KPI запись связана только с НУЖНЫМИ задачами:")
    print("   • 'Полиграфия качество' → только полиграфические задачи")
    print("   • 'Листовка скорость' → только задачи с шаблоном 'Листовка'")
    print("   • 'Команда X эффективность' → только задачи исполнителя X")
    
    print(f"\n📈 РЕЗУЛЬТАТ:")
    advantages = [
        "Все метрики считаются АВТОМАТИЧЕСКИ",
        "Добавил задачу → KPI обновился мгновенно", 
        "Фильтрация по любым критериям",
        "Масштабируется до любого количества метрик",
        "RDT получает готовые данные через rollup"
    ]
    
    for adv in advantages:
        print(f"   ✅ {adv}")
    
    print(f"\n🎯 АРХИТЕКТУРА ПОТОКА ДАННЫХ:")
    print("   TASKS (задачи) → KPI (автоматические метрики) → RDT (dashboard)")
    print("   Все считается само, ничего руками не вводим!")
    
    print(f"\n⚠️ ОДИН НЮАНС:")
    print("   Relation фильтры настраиваются вручную в Notion UI")
    print("   Но это делается один раз при создании KPI метрики")

if __name__ == "__main__":
    explain_kpi_auto_calculation() 