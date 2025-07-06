import os
from notion_client import Client

# Initialize Notion client
notion = Client(auth=os.environ["NOTION_TOKEN"])

# Database IDs
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"
RDT_DB = "195ace03d9ff80c1a1b0d236ec3564d2"

def setup_rdt_rollups():
    """Setup rollup fields in RDT to pull data from KPI"""
    
    print("📊 НАСТРОЙКА ROLLUP ПОЛЕЙ RDT ← KPI")
    print("=" * 60)
    
    # First, let's see what KPI fields are available for rollup
    try:
        kpi_db = notion.databases.retrieve(database_id=KPI_DB)
        print("📋 ДОСТУПНЫЕ ПОЛЯ В KPI ДЛЯ ROLLUP:")
        
        kpi_fields = []
        for prop_name, prop_info in kpi_db['properties'].items():
            prop_type = prop_info['type']
            if prop_type in ['number', 'formula', 'rollup']:
                kpi_fields.append((prop_name, prop_type))
                print(f"   • {prop_name} ({prop_type})")
        
        print(f"\n📊 RDT ТЕКУЩИЕ ПОЛЯ:")
        rdt_db = notion.databases.retrieve(database_id=RDT_DB)
        
        current_rollups = []
        current_formulas = []
        
        for prop_name, prop_info in rdt_db['properties'].items():
            prop_type = prop_info['type']
            if prop_type == 'rollup':
                current_rollups.append(prop_name)
                relation_prop = prop_info['rollup']['relation_property_name']
                rollup_prop = prop_info['rollup']['rollup_property_name']
                print(f"   🔗 {prop_name} (rollup via {relation_prop} → {rollup_prop})")
            elif prop_type == 'formula':
                current_formulas.append(prop_name)
                print(f"   🧮 {prop_name} (formula)")
        
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print("🎯 ПЕРЕМЕСТИТЬ РАСЧЕТЫ ИЗ RDT В KPI:")
        print("   1. В KPI создать formula поля для:")
        
        target_metrics = [
            "% задач в срок",
            "% задач без правок", 
            "Среднее отклонение времени",
            "Качество выполнения"
        ]
        
        for metric in target_metrics:
            print(f"      • {metric}")
        
        print(f"\n   2. В RDT заменить formula на rollup из KPI:")
        formulas_to_replace = [
            "% в срок",
            "% без правок", 
            "Качество",
            "Отклонение"
        ]
        
        for formula in formulas_to_replace:
            if formula in current_formulas:
                print(f"      ✅ {formula} → заменить на rollup")
            else:
                print(f"      ❓ {formula} → не найдено")
        
        print(f"\n🔧 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Настроить KPI формулы (автоматически)")
        print("2. Обновить RDT rollup поля (ручная настройка)")
        print("3. Протестировать всю цепочку")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    setup_rdt_rollups() 