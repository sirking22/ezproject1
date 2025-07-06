import asyncio
import json
import os
from datetime import datetime
from notion_mcp_server import NotionMCPServer

# Список всех баз из переменных окружения
BASES = {
    'tasks': os.getenv('NOTION_TASKS_DB_ID'),
    'subtasks': os.getenv('NOTION_SUBTASKS_DB_ID'),
    'projects': os.getenv('NOTION_PROJECTS_DB_ID'),
    'ideas': os.getenv('NOTION_IDEAS_DB_ID'),
    'materials': os.getenv('NOTION_MATERIALS_DB_ID'),
    'kpi': os.getenv('NOTION_KPI_DB_ID'),
    'epics': os.getenv('NOTION_EPICS_DB_ID'),
    'guides': os.getenv('NOTION_GUIDES_DB_ID'),
    'superguide': os.getenv('NOTION_SUPER_GUIDES_DB_ID'),
    'marketing': os.getenv('NOTION_MARKETING_TASKS_DB_ID'),
    'smm': os.getenv('NOTION_SMM_TASKS_DB_ID'),
}

async def analyze_database_structure(server, db_name, db_id):
    """Полный анализ структуры базы данных"""
    print(f"\n🔍 Анализ базы: {db_name} ({db_id})")
    
    try:
        # Получаем схему базы напрямую через Notion API
        db_info = await server.client.databases.retrieve(database_id=db_id)
        
        if not db_info:
            print(f"❌ Не удалось получить схему для {db_name}")
            return None
            
        properties = db_info.get('properties', {})
        
        # Проверяем, что properties - это словарь
        if not isinstance(properties, dict):
            print(f"⚠️ Properties для {db_name} - это {type(properties)}, пропускаю")
            return None
        
        analysis = {
            'database_name': db_name,
            'database_id': db_id,
            'title': db_info.get('title', []),
            'description': db_info.get('description', []),
            'properties': {},
            'property_types': {},
            'status_options': {},
            'select_options': {},
            'multi_select_options': {},
            'relations': {},
            'formulas': {},
            'rollups': {}
        }
        
        print(f"📊 Найдено полей: {len(properties)}")
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get('type', 'unknown')
            analysis['property_types'][prop_name] = prop_type
            
            print(f"  • {prop_name} ({prop_type})")
            
            # Анализ по типам полей
            if prop_type == 'status':
                options = prop_data.get('status', {}).get('options', [])
                analysis['status_options'][prop_name] = [opt.get('name') for opt in options]
                print(f"    Статусы: {[opt.get('name') for opt in options]}")
                
            elif prop_type == 'select':
                options = prop_data.get('select', {}).get('options', [])
                analysis['select_options'][prop_name] = [opt.get('name') for opt in options]
                print(f"    Опции: {[opt.get('name') for opt in options]}")
                
            elif prop_type == 'multi_select':
                options = prop_data.get('multi_select', {}).get('options', [])
                analysis['multi_select_options'][prop_name] = [opt.get('name') for opt in options]
                print(f"    Множественные опции: {[opt.get('name') for opt in options]}")
                
            elif prop_type == 'relation':
                relation_info = prop_data.get('relation', {})
                analysis['relations'][prop_name] = {
                    'database_id': relation_info.get('database_id'),
                    'type': relation_info.get('type', 'single_property'),
                    'single_property': relation_info.get('single_property', {}),
                    'dual_property': relation_info.get('dual_property', {})
                }
                print(f"    Связь с базой: {relation_info.get('database_id')}")
                
            elif prop_type == 'formula':
                formula_info = prop_data.get('formula', {})
                analysis['formulas'][prop_name] = {
                    'expression': formula_info.get('expression', ''),
                    'type': formula_info.get('type', '')
                }
                print(f"    Формула: {formula_info.get('type', 'unknown')}")
                
            elif prop_type == 'rollup':
                rollup_info = prop_data.get('rollup', {})
                analysis['rollups'][prop_name] = {
                    'relation_property_name': rollup_info.get('relation_property_name', ''),
                    'rollup_property_name': rollup_info.get('rollup_property_name', ''),
                    'function': rollup_info.get('function', '')
                }
                print(f"    Rollup: {rollup_info.get('function', 'unknown')}")
                
            elif prop_type == 'people':
                print(f"    Участники: люди")
                
            elif prop_type == 'date':
                print(f"    Дата")
                
            elif prop_type == 'number':
                number_info = prop_data.get('number', {})
                format_type = number_info.get('format', 'number')
                print(f"    Число (формат: {format_type})")
                
            elif prop_type == 'url':
                print(f"    URL")
                
            elif prop_type == 'email':
                print(f"    Email")
                
            elif prop_type == 'phone_number':
                print(f"    Телефон")
                
            elif prop_type == 'files':
                print(f"    Файлы")
                
            elif prop_type == 'checkbox':
                print(f"    Чекбокс")
                
            elif prop_type == 'rich_text':
                print(f"    Текст")
                
            elif prop_type == 'title':
                print(f"    Заголовок")
                
            else:
                print(f"    Неизвестный тип: {prop_type}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Ошибка при анализе {db_name}: {e}")
        return None

async def main():
    """Анализ всех баз данных"""
    server = NotionMCPServer()
    
    print("🔍 ПОЛНЫЙ АНАЛИЗ СТРУКТУРЫ БАЗ NOTION")
    print("=" * 50)
    
    all_analyses = {}
    
    for db_name, db_id in BASES.items():
        if not db_id:
            print(f"⚠️ Пропускаю {db_name}: ID не найден")
            continue
            
        analysis = await analyze_database_structure(server, db_name, db_id)
        if analysis:
            all_analyses[db_name] = analysis
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"notion_bases_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_analyses, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Анализ завершён! Результаты сохранены в {filename}")
    
    # Создаём краткий отчёт
    report_filename = f"notion_bases_report_{timestamp}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("# 📊 Анализ структуры баз Notion\n\n")
        f.write(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for db_name, analysis in all_analyses.items():
            f.write(f"## {db_name.upper()}\n")
            f.write(f"**ID:** `{analysis['database_id']}`\n\n")
            
            f.write("### Поля:\n")
            for prop_name, prop_type in analysis['property_types'].items():
                f.write(f"- **{prop_name}** (`{prop_type}`)\n")
            
            if analysis['status_options']:
                f.write("\n### Статусы:\n")
                for prop_name, options in analysis['status_options'].items():
                    f.write(f"- **{prop_name}:** {', '.join(options)}\n")
            
            if analysis['select_options']:
                f.write("\n### Выборы:\n")
                for prop_name, options in analysis['select_options'].items():
                    f.write(f"- **{prop_name}:** {', '.join(options)}\n")
            
            if analysis['multi_select_options']:
                f.write("\n### Множественные выборы:\n")
                for prop_name, options in analysis['multi_select_options'].items():
                    f.write(f"- **{prop_name}:** {', '.join(options)}\n")
            
            if analysis['relations']:
                f.write("\n### Связи:\n")
                for prop_name, relation in analysis['relations'].items():
                    f.write(f"- **{prop_name}:** {relation['database_id']}\n")
            
            f.write("\n---\n\n")
    
    print(f"📋 Краткий отчёт сохранён в {report_filename}")
    print(f"📊 Полные данные в {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 