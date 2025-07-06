"""
Тестирование системы мониторинга схем
"""

import os
import json
from datetime import datetime
from notion_schema_monitor import NotionSchemaMonitor
from auto_update_schemas import load_changes, validate_updates

def test_monitoring_system():
    """Тестирование системы мониторинга"""
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ МОНИТОРИНГА СХЕМ")
    print("=" * 50)
    
    # 1. Тест мониторинга
    print("\n1️⃣ Тест мониторинга изменений...")
    monitor = NotionSchemaMonitor()
    
    try:
        changes = monitor.detect_changes()
        print(f"✅ Мониторинг работает: обнаружено {len(changes)} изменений")
        
        if changes:
            print("📝 Обнаруженные изменения:")
            for change in changes:
                print(f"  - {change.database_name}: {change.change_type} - {change.property_name} = {change.new_value}")
        else:
            print("ℹ️ Изменений не обнаружено")
            
    except Exception as e:
        print(f"❌ Ошибка мониторинга: {e}")
        return False
    
    # 2. Тест загрузки изменений
    print("\n2️⃣ Тест загрузки изменений...")
    try:
        changes = load_changes()
        print(f"✅ Загрузка работает: {len(changes)} изменений загружено")
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return False
    
    # 3. Тест валидации
    print("\n3️⃣ Тест валидации схем...")
    try:
        is_valid = validate_updates()
        if is_valid:
            print("✅ Валидация прошла успешно")
        else:
            print("❌ Ошибка валидации")
            return False
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        return False
    
    # 4. Тест создания тестовых изменений
    print("\n4️⃣ Тест создания тестовых изменений...")
    test_changes = [
        {
            "database_name": "tasks",
            "change_type": "new_status",
            "property_name": "Статус",
            "new_value": "Тестовый статус",
            "timestamp": datetime.now().isoformat()
        },
        {
            "database_name": "ideas",
            "change_type": "new_multi_select_option",
            "property_name": "Теги",
            "new_value": "Тестовый тег",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    try:
        with open("test_schema_changes.json", "w", encoding="utf-8") as f:
            json.dump(test_changes, f, indent=2, ensure_ascii=False)
        print("✅ Тестовые изменения созданы")
    except Exception as e:
        print(f"❌ Ошибка создания тестовых изменений: {e}")
        return False
    
    # 5. Тест резервного копирования
    print("\n5️⃣ Тест резервного копирования...")
    try:
        monitor.create_backup()
        print("✅ Резервное копирование работает")
    except Exception as e:
        print(f"❌ Ошибка резервного копирования: {e}")
        return False
    
    # 6. Очистка тестовых файлов
    print("\n6️⃣ Очистка тестовых файлов...")
    try:
        if os.path.exists("test_schema_changes.json"):
            os.remove("test_schema_changes.json")
        print("✅ Тестовые файлы удалены")
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")
    
    print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    return True

def test_manual_update():
    """Тест ручного обновления схем"""
    print("\n🔧 ТЕСТ РУЧНОГО ОБНОВЛЕНИЯ")
    print("=" * 30)
    
    # Создать тестовые изменения
    test_changes = [
        {
            "database_name": "tasks",
            "change_type": "new_status",
            "property_name": "Статус",
            "new_value": "Ручной тест"
        }
    ]
    
    with open("schema_changes.json", "w", encoding="utf-8") as f:
        json.dump(test_changes, f, indent=2, ensure_ascii=False)
    
    print("📝 Создан файл schema_changes.json с тестовыми изменениями")
    print("💡 Запустите: python auto_update_schemas.py")
    print("💡 После тестирования удалите schema_changes.json")

def show_monitoring_status():
    """Показать статус системы мониторинга"""
    print("\n📊 СТАТУС СИСТЕМЫ МОНИТОРИНГА")
    print("=" * 40)
    
    files_to_check = [
        "notion_schema_monitor.py",
        "auto_update_schemas.py",
        "notion_database_schemas.py",
        "test_schemas_integration.py"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - НЕ НАЙДЕН")
    
    # Проверить CI файлы
    ci_files = [
        ".github/workflows/schema-monitoring.yml",
        ".github/workflows/schema-validation.yml"
    ]
    
    print("\n🔧 CI/CD файлы:")
    for file in ci_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - НЕ НАЙДЕН")

def main():
    """Главная функция"""
    print("🚀 ТЕСТИРОВАНИЕ СИСТЕМЫ МОНИТОРИНГА СХЕМ")
    print("=" * 60)
    
    # Показать статус
    show_monitoring_status()
    
    # Запустить тесты
    if test_monitoring_system():
        print("\n🎯 СИСТЕМА ГОТОВА К РАБОТЕ")
        print("\n📋 Команды для использования:")
        print("1. Мониторинг: python notion_schema_monitor.py")
        print("2. Обновление: python auto_update_schemas.py")
        print("3. Тестирование: python test_schemas_integration.py")
        print("4. CI проверка: python setup_ci.py check")
        
        # Предложить тест ручного обновления
        response = input("\n🧪 Запустить тест ручного обновления? (y/n): ")
        if response.lower() == 'y':
            test_manual_update()
    else:
        print("\n❌ СИСТЕМА НЕ ГОТОВА")
        print("Проверьте ошибки выше и исправьте их")

if __name__ == "__main__":
    main() 