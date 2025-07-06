"""
Автоматическое обновление схем баз данных на основе обнаруженных изменений
"""

import json
import re
from typing import Dict, List, Any
from pathlib import Path

def load_changes() -> List[Dict[str, Any]]:
    """Загрузить обнаруженные изменения"""
    changes_file = "schema_changes.json"
    if not Path(changes_file).exists():
        print("❌ Файл schema_changes.json не найден")
        return []
    
    with open(changes_file, "r", encoding="utf-8") as f:
        return json.load(f)

def update_schema_file(changes: List[Dict[str, Any]]):
    """Обновить файл notion_database_schemas.py"""
    schema_file = "notion_database_schemas.py"
    
    if not Path(schema_file).exists():
        print("❌ Файл notion_database_schemas.py не найден")
        return False
    
    # Загрузить текущий файл
    with open(schema_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Группировать изменения по базе данных
    changes_by_db = {}
    for change in changes:
        db_name = change["database_name"]
        if db_name not in changes_by_db:
            changes_by_db[db_name] = []
        changes_by_db[db_name].append(change)
    
    # Обновить каждую схему
    for db_name, db_changes in changes_by_db.items():
        print(f"🔄 Обновление схемы {db_name}...")
        
        # Найти блок схемы в файле
        pattern = rf'"{db_name}": DatabaseSchema\([^)]+\)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print(f"⚠️ Схема {db_name} не найдена в файле")
            continue
        
        schema_block = match.group(0)
        updated_block = schema_block
        
        # Применить изменения
        for change in db_changes:
            change_type = change["change_type"]
            property_name = change["property_name"]
            new_value = change["new_value"]
            
            if change_type == "new_status":
                updated_block = add_status_option(updated_block, property_name, new_value)
            elif change_type == "new_select_option":
                updated_block = add_select_option(updated_block, property_name, new_value)
            elif change_type == "new_multi_select_option":
                updated_block = add_multi_select_option(updated_block, property_name, new_value)
            elif change_type == "new_property":
                updated_block = add_property(updated_block, property_name, new_value)
        
        # Заменить блок в файле
        content = content.replace(schema_block, updated_block)
    
    # Сохранить обновлённый файл
    with open(schema_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Файл notion_database_schemas.py обновлён")
    return True

def add_status_option(schema_block: str, property_name: str, new_value: str) -> str:
    """Добавить новый статус в схему"""
    # Найти блок status_options
    pattern = rf'status_options=\{{[^}}]*"Статус":\s*\[[^\]]*\]'
    match = re.search(pattern, schema_block, re.DOTALL)
    
    if match:
        # Добавить новый статус в список
        status_block = match.group(0)
        if new_value not in status_block:
            # Найти закрывающую скобку списка
            list_end = status_block.rfind("]")
            if list_end != -1:
                updated_status = status_block[:list_end] + f', "{new_value}"' + status_block[list_end:]
                return schema_block.replace(status_block, updated_status)
    
    return schema_block

def add_select_option(schema_block: str, property_name: str, new_value: str) -> str:
    """Добавить новую опцию выбора в схему"""
    # Найти блок select_options
    pattern = rf'select_options=\{{[^}}]*"{re.escape(property_name)}":\s*\[[^\]]*\]'
    match = re.search(pattern, schema_block, re.DOTALL)
    
    if match:
        # Добавить новую опцию в список
        select_block = match.group(0)
        if new_value not in select_block:
            # Найти закрывающую скобку списка
            list_end = select_block.rfind("]")
            if list_end != -1:
                updated_select = select_block[:list_end] + f', "{new_value}"' + select_block[list_end:]
                return schema_block.replace(select_block, updated_select)
    
    return schema_block

def add_multi_select_option(schema_block: str, property_name: str, new_value: str) -> str:
    """Добавить новый тег в схему"""
    # Найти блок multi_select_options
    pattern = rf'multi_select_options=\{{[^}}]*"{re.escape(property_name)}":\s*\[[^\]]*\]'
    match = re.search(pattern, schema_block, re.DOTALL)
    
    if match:
        # Добавить новый тег в список
        multi_block = match.group(0)
        if new_value not in multi_block:
            # Найти закрывающую скобку списка
            list_end = multi_block.rfind("]")
            if list_end != -1:
                updated_multi = multi_block[:list_end] + f', "{new_value}"' + multi_block[list_end:]
                return schema_block.replace(multi_block, updated_multi)
    
    return schema_block

def add_property(schema_block: str, property_name: str, property_type: str) -> str:
    """Добавить новое свойство в схему"""
    # Найти блок properties
    pattern = r'properties=\{[^}]*\}'
    match = re.search(pattern, schema_block, re.DOTALL)
    
    if match:
        properties_block = match.group(0)
        if property_name not in properties_block:
            # Добавить новое свойство
            property_entry = f'"{property_name}": {{"type": "{property_type}"}}'
            
            # Найти закрывающую скобку properties
            brace_end = properties_block.rfind("}")
            if brace_end != -1:
                updated_properties = properties_block[:brace_end] + f', {property_entry}' + properties_block[brace_end:]
                return schema_block.replace(properties_block, updated_properties)
    
    return schema_block

def create_migration_script(changes: List[Dict[str, Any]]):
    """Создать скрипт миграции для ручного применения"""
    migration_lines = [
        "# Скрипт миграции схем",
        "# Запуск: python migrate_schemas.py",
        "",
        "from notion_database_schemas import DATABASE_SCHEMAS",
        "import json",
        "",
        "def apply_migrations():",
        "    \"\"\"Применить миграции к схемам\"\"\"",
        ""
    ]
    
    # Группировать изменения
    changes_by_db = {}
    for change in changes:
        db_name = change["database_name"]
        if db_name not in changes_by_db:
            changes_by_db[db_name] = []
        changes_by_db[db_name].append(change)
    
    for db_name, db_changes in changes_by_db.items():
        migration_lines.append(f"    # Миграции для {db_name}")
        
        for change in db_changes:
            change_type = change["change_type"]
            property_name = change["property_name"]
            new_value = change["new_value"]
            
            if change_type == "new_status":
                migration_lines.append(
                    f"    # DATABASE_SCHEMAS['{db_name}'].status_options['{property_name}'].append('{new_value}')"
                )
            elif change_type == "new_select_option":
                migration_lines.append(
                    f"    # DATABASE_SCHEMAS['{db_name}'].select_options['{property_name}'].append('{new_value}')"
                )
            elif change_type == "new_multi_select_option":
                migration_lines.append(
                    f"    # DATABASE_SCHEMAS['{db_name}'].multi_select_options['{property_name}'].append('{new_value}')"
                )
            elif change_type == "new_property":
                migration_lines.append(
                    f"    # DATABASE_SCHEMAS['{db_name}'].properties['{property_name}'] = {{'type': '{new_value}'}}"
                )
        
        migration_lines.append("")
    
    migration_lines.extend([
        "    print('✅ Миграции применены')",
        "",
        "if __name__ == '__main__':",
        "    apply_migrations()"
    ])
    
    with open("migrate_schemas.py", "w", encoding="utf-8") as f:
        f.write("\n".join(migration_lines))
    
    print("✅ Скрипт миграции создан: migrate_schemas.py")

def validate_updates():
    """Проверить корректность обновлений"""
    print("🧪 Проверка обновлений...")
    
    try:
        # Импортировать обновлённые схемы
        from notion_database_schemas import get_all_schemas
        
        schemas = get_all_schemas()
        print(f"✅ Загружено {len(schemas)} схем")
        
        # Проверить каждую схему
        for db_name, schema in schemas.items():
            if not schema.database_id:
                print(f"❌ Ошибка в схеме {db_name}: отсутствует database_id")
                return False
            
            if not schema.name:
                print(f"❌ Ошибка в схеме {db_name}: отсутствует name")
                return False
        
        print("✅ Все схемы корректны")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        return False

def main():
    """Главная функция"""
    print("🔄 АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ СХЕМ")
    print("=" * 50)
    
    # Загрузить изменения
    changes = load_changes()
    
    if not changes:
        print("ℹ️ Изменений для применения нет")
        return
    
    print(f"📝 Найдено {len(changes)} изменений для применения")
    
    # Создать резервную копию
    import shutil
    shutil.copy("notion_database_schemas.py", "notion_database_schemas.py.backup")
    print("✅ Создана резервная копия")
    
    # Обновить файл схем
    if update_schema_file(changes):
        # Создать скрипт миграции
        create_migration_script(changes)
        
        # Проверить обновления
        if validate_updates():
            print("\n🎉 Обновления применены успешно!")
            print("\n📋 Следующие шаги:")
            print("1. Запустите тесты: python test_schemas_integration.py")
            print("2. Проверьте CI: python setup_ci.py check")
            print("3. Закоммитьте изменения")
            print("4. Удалите schema_changes.json после проверки")
        else:
            print("\n❌ Ошибка валидации обновлений")
            print("Восстановите из резервной копии: notion_database_schemas.py.backup")
    else:
        print("\n❌ Ошибка обновления файла схем")

if __name__ == "__main__":
    main() 