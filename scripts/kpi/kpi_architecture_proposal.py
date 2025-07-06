import os
from notion_client import Client

# Initialize Notion client
notion = Client(auth=os.environ["NOTION_TOKEN"])

def propose_kpi_architecture():
    """Propose scalable KPI architecture for 30+ metrics"""
    
    print("🏗️ ПРЕДЛОЖЕНИЕ МАСШТАБИРУЕМОЙ АРХИТЕКТУРЫ KPI")
    print("=" * 60)
    
    print("🎯 РЕКОМЕНДУЕМЫЙ ПОДХОД: КАТЕГОРИЗИРОВАННЫЕ МЕТРИКИ")
    print("\n📊 СТРУКТУРА KPI БАЗЫ:")
    
    kpi_structure = {
        "Название метрики": "title",
        "Категория": "select (Полиграфия, Контент, Дизайн, Общие)",
        "Команда": "select (Дизайн-команда, Контент-команда, Вся компания)",
        "Тип метрики": "select (Качество, Скорость, Объем, Эффективность)",
        "Целевое значение": "number",
        "Текущее значение": "number", 
        "Формула расчета": "rich_text",
        "Единица измерения": "select (%, часы, количество, баллы)",
        "Период": "select (день, неделя, месяц, квартал)",
        "Статус": "select (🟢 Норма, 🟡 Внимание, 🔴 Критично)"
    }
    
    for field_name, field_type in kpi_structure.items():
        print(f"   • {field_name}: {field_type}")
    
    print(f"\n📋 ПРИМЕРЫ МЕТРИК:")
    
    sample_metrics = [
        {
            "name": "% задач полиграфии в срок",
            "category": "Полиграфия", 
            "team": "Дизайн-команда",
            "type": "Качество",
            "unit": "%",
            "target": 85
        },
        {
            "name": "Среднее время на листовку",
            "category": "Полиграфия",
            "team": "Дизайн-команда", 
            "type": "Скорость",
            "unit": "часы",
            "target": 2.5
        },
        {
            "name": "Количество правок на баннер",
            "category": "Полиграфия",
            "team": "Дизайн-команда",
            "type": "Качество", 
            "unit": "количество",
            "target": 1
        },
        {
            "name": "Общая эффективность команды",
            "category": "Общие",
            "team": "Вся компания",
            "type": "Эффективность",
            "unit": "баллы",
            "target": 90
        }
    ]
    
    for i, metric in enumerate(sample_metrics, 1):
        print(f"{i}. {metric['name']}")
        print(f"   Категория: {metric['category']} | Команда: {metric['team']}")
        print(f"   Тип: {metric['type']} | Цель: {metric['target']} {metric['unit']}")
    
    print(f"\n🎯 ПРЕИМУЩЕСТВА ТАКОГО ПОДХОДА:")
    advantages = [
        "Один KPI на строку - легко добавлять новые",
        "Фильтрация по категориям/командам",
        "Унифицированная структура метрик",
        "Масштабируется до 100+ метрик",
        "Легко создавать дашборды в RDT"
    ]
    
    for adv in advantages:
        print(f"   ✅ {adv}")
    
    print(f"\n📊 КАК БУДЕТ РАБОТАТЬ RDT:")
    print("   RDT сделает rollup из KPI по категориям:")
    print("   • Полиграфия → среднее по всем полиграфическим метрикам")  
    print("   • Дизайн → среднее по всем дизайнерским метрикам")
    print("   • Команда X → все метрики конкретной команды")
    
    print(f"\n🚀 МИГРАЦИЯ:")
    print("1. Создать новые поля в текущей KPI базе")
    print("2. Перенести существующие метрики в новый формат")
    print("3. Настроить фильтры в RDT по категориям")
    print("4. Добавлять новые метрики как отдельные записи")
    
    print(f"\n💡 РЕЗУЛЬТАТ:")
    print("   Вместо 30 полей → 30 строк с 10 полями")
    print("   Гибко, масштабируемо, удобно для анализа!")

if __name__ == "__main__":
    propose_kpi_architecture() 