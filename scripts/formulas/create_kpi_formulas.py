import os
from notion_client import Client

# Initialize Notion client
notion = Client(auth=os.environ["NOTION_TOKEN"])

# Database IDs
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"

def create_kpi_formulas():
    """Create formula fields in KPI database for centralized metrics"""
    
    print("🧮 СОЗДАНИЕ ФОРМУЛ В KPI БАЗЕ")
    print("=" * 60)
    
    # Define KPI formulas to create
    kpi_formulas = [
        {
            "name": "% задач в срок", 
            "formula": 'round(prop("Задачи в срок") / prop("Всего задач") * 100)',
            "description": "Процент задач выполненных в срок"
        },
        {
            "name": "% задач без правок",
            "formula": 'round(prop("Задачи без правок") / prop("Всего задач") * 100)', 
            "description": "Процент задач выполненных без правок"
        },
        {
            "name": "Среднее отклонение времени",
            "formula": 'round(prop("Общее отклонение") / prop("Всего задач"), 1)',
            "description": "Среднее отклонение фактического времени от планового"
        },
        {
            "name": "Качество выполнения",
            "formula": 'round((prop("% задач в срок") + prop("% задач без правок")) / 2)',
            "description": "Общий показатель качества работы"
        }
    ]
    
    try:
        # First check current KPI structure
        kpi_db = notion.databases.retrieve(database_id=KPI_DB)
        current_props = list(kpi_db['properties'].keys())
        print(f"📋 Текущие поля в KPI: {len(current_props)}")
        
        print(f"\n🎯 ФОРМУЛЫ ДЛЯ СОЗДАНИЯ:")
        for formula in kpi_formulas:
            print(f"   • {formula['name']}")
            print(f"     Формула: {formula['formula']}")
            print(f"     Описание: {formula['description']}")
        
        print(f"\n⚠️ ВАЖНО!")
        print("Notion API не позволяет создавать formula поля программно.")
        print("Эти формулы нужно добавить ВРУЧНУЮ в KPI базе:")
        print(f"🔗 https://www.notion.so/{KPI_DB.replace('-', '')}")
        
        print(f"\n📋 ИНСТРУКЦИЯ:")
        print("1. Открыть KPI базу в Notion")
        print("2. Добавить новое поле (+ справа)")
        print("3. Выбрать тип 'Formula'")
        print("4. Ввести название и формулу")
        print("5. Повторить для всех 4 формул")
        
        print(f"\n💡 ПОСЛЕ СОЗДАНИЯ:")
        print("В RDT нужно будет настроить rollup из этих KPI полей")
        
        # Also suggest what data fields might be needed
        print(f"\n📊 ВОЗМОЖНО НУЖНЫ ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ В KPI:")
        suggested_fields = [
            "Всего задач (number)",
            "Задачи в срок (number)", 
            "Задачи без правок (number)",
            "Общее отклонение (number)"
        ]
        
        for field in suggested_fields:
            print(f"   • {field}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    create_kpi_formulas() 