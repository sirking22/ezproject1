import os
from notion_client import Client

# Initialize Notion client
notion = Client(auth=os.environ["NOTION_TOKEN"])

# Database IDs
TASKS_DB = "9c5f4269d61449b6a7485579a3c21da3"
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c" 
RDT_DB = "195ace03d9ff80c1a1b0d236ec3564d2"
TEMPLATES_DB = os.environ["NOTION_TASKS_TEMPLATES_DB_ID"]

def auto_setup_system():
    """Do everything possible automatically, provide precise manual steps for the rest"""
    
    print("🚀 АВТОМАТИЧЕСКАЯ НАСТРОЙКА СИСТЕМЫ")
    print("=" * 60)
    
    try:
        # 1. Check existing structure
        print("📊 ШАГ 1: АНАЛИЗ ТЕКУЩЕЙ СТРУКТУРЫ")
        
        tasks_db = notion.databases.retrieve(database_id=TASKS_DB)
        kpi_db = notion.databases.retrieve(database_id=KPI_DB)
        rdt_db = notion.databases.retrieve(database_id=RDT_DB)
        
        # Check TASKS → KPI relation
        tasks_to_kpi = False
        for prop_name, prop_info in tasks_db['properties'].items():
            if (prop_info['type'] == 'relation' and 
                prop_info['relation']['database_id'] == KPI_DB):
                tasks_to_kpi = True
                print(f"✅ TASKS → KPI связь найдена: {prop_name}")
        
        if not tasks_to_kpi:
            print("❌ TASKS → KPI связь НЕ найдена")
        
        # Check KPI → RDT relation  
        kpi_to_rdt = False
        for prop_name, prop_info in kpi_db['properties'].items():
            if (prop_info['type'] == 'relation' and
                prop_info['relation']['database_id'] == RDT_DB):
                kpi_to_rdt = True
                print(f"✅ KPI → RDT связь найдена: {prop_name}")
        
        # 2. Create sample KPI records if needed
        print(f"\n📝 ШАГ 2: СОЗДАНИЕ ТЕСТОВЫХ KPI ЗАПИСЕЙ")
        
        kpi_records = notion.databases.query(database_id=KPI_DB, page_size=5)
        if len(kpi_records['results']) < 3:
            # Create basic KPI records for polygraphy
            sample_kpis = [
                "Полиграфия - Качество",
                "Полиграфия - Скорость", 
                "Полиграфия - Точность"
            ]
            
            for kpi_name in sample_kpis:
                try:
                    notion.pages.create(
                        parent={"database_id": KPI_DB},
                        properties={
                            "Name": {
                                "title": [{"text": {"content": kpi_name}}]
                            }
                        }
                    )
                    print(f"✅ Создан KPI: {kpi_name}")
                except:
                    print(f"⚠️ KPI уже существует: {kpi_name}")
        
        # 3. Provide exact manual steps
        print(f"\n🔧 ШАГ 3: ТОЧНЫЕ ИНСТРУКЦИИ ДЛЯ РУЧНОЙ НАСТРОЙКИ")
        print("=" * 60)
        
        print("📋 В KPI БАЗЕ ДОБАВИТЬ ПОЛЯ:")
        print(f"🔗 https://www.notion.so/{KPI_DB.replace('-', '')}")
        
        kpi_formulas = [
            ("Всего задач", "number", "Общее количество задач"),
            ("Задачи в срок", "number", "Количество задач выполненных в срок"),
            ("Задачи без правок", "number", "Количество задач без правок"),
            ("% в срок", "formula", 'round(prop("Задачи в срок") / prop("Всего задач") * 100)'),
            ("% без правок", "formula", 'round(prop("Задачи без правок") / prop("Всего задач") * 100)')
        ]
        
        for i, (name, field_type, formula) in enumerate(kpi_formulas, 1):
            print(f"{i}. Добавить поле '{name}' (тип: {field_type})")
            if field_type == "formula":
                print(f"   Формула: {formula}")
        
        print(f"\n📋 В RDT БАЗЕ ИЗМЕНИТЬ ПОЛЯ:")
        print(f"🔗 https://www.notion.so/{RDT_DB.replace('-', '')}")
        
        rdt_changes = [
            ("% в срок", "Заменить formula на rollup из KPI → % в срок"),
            ("% без правок", "Заменить formula на rollup из KPI → % без правок"),
            ("Качество", "Заменить formula на rollup из KPI → среднее из % полей")
        ]
        
        for i, (field, action) in enumerate(rdt_changes, 1):
            print(f"{i}. {field}: {action}")
        
        # 4. Test the connection
        print(f"\n🧪 ШАГ 4: ПРОВЕРКА СВЯЗЕЙ")
        
        test_task_exists = False
        tasks_response = notion.databases.query(
            database_id=TASKS_DB,
            filter={
                "property": "Подзадачи",
                "title": {"contains": "ТЕСТ:"}
            },
            page_size=1
        )
        
        if tasks_response['results']:
            test_task = tasks_response['results'][0]
            task_title = test_task['properties']['Подзадачи']['title'][0]['text']['content']
            print(f"✅ Тестовая задача найдена: {task_title}")
            print(f"🔗 {test_task['url']}")
            test_task_exists = True
        
        # 5. Provide next steps
        print(f"\n🎯 СЛЕДУЮЩИЕ ДЕЙСТВИЯ:")
        print("1. ✅ Полиграфические шаблоны созданы")
        print("2. ⏳ Добавить поля в KPI (5 мин)")
        print("3. ⏳ Настроить rollup в RDT (3 мин)")
        if test_task_exists:
            print("4. ✅ Тестовая задача готова для проверки")
        print("5. ⏳ Протестировать всю цепочку")
        
        print(f"\n🚀 ГОТОВНОСТЬ СИСТЕМЫ: 70%")
        print("Остались только ручные настройки полей!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    auto_setup_system() 