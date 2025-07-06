#!/usr/bin/env python3
"""
Создание публичной папки с возможностью редактирования на Яндекс.Диске
"""

import os
import requests
import yadisk
from datetime import datetime

def create_public_folder_with_edit():
    """Создает публичную папку с возможностью редактирования"""
    
    # Получаем токен
    token = os.getenv('YA_ACCESS_TOKEN')
    if not token:
        print("❌ YA_ACCESS_TOKEN не найден в переменных окружения")
        return
    
    try:
        # Инициализируем клиент Яндекс.Диска
        y = yadisk.YaDisk(token=token)
        
        # Создаем папку для совместной работы
        folder_name = f"Совместная_работа_{datetime.now().strftime('%Y%m%d_%H%M')}"
        folder_path = f"/{folder_name}"
        
        print(f"📁 Создаю папку: {folder_name}")
        y.mkdir(folder_path)
        
        # Публикуем папку
        print("🌐 Публикую папку...")
        publish_response = requests.put(
            'https://cloud-api.yandex.net/v1/disk/resources/publish',
            headers={'Authorization': f'OAuth {token}'},
            params={'path': folder_path}
        )
        publish_response.raise_for_status()
        
        # Получаем информацию о папке
        folder_info = y.get_meta(folder_path)
        public_url = folder_info.public_url if hasattr(folder_info, 'public_url') else None
        
        if public_url:
            print(f"✅ Публичная ссылка создана!")
            print(f"🔗 URL: {public_url}")
            print(f"📁 Путь: {folder_path}")
            
            # Создаем README файл с инструкциями
            readme_content = f"""# Папка для совместной работы

## 📋 Инструкции

### Для добавления файлов:
1. Перейдите по ссылке: {public_url}
2. Нажмите "Загрузить файлы" или перетащите файлы в браузер
3. Файлы автоматически станут доступны всем участникам

### Для редактирования:
- Все файлы в этой папке доступны для просмотра и скачивания
- Для редактирования загрузите файл к себе, отредактируйте и загрузите обратно

### Типы файлов:
- 📄 Документы (Word, PDF, Excel)
- 🎤 Аудио файлы для транскрибации
- 🎥 Видео файлы
- 📸 Изображения

### Транскрибация аудио:
1. Загрузите аудио файл в эту папку
2. Используйте команду `/transcribe_yadisk` в боте
3. Получите транскрипт с разделением по ролям

---
Создано: {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
            
            # Сохраняем README
            readme_path = f"{folder_path}/README.md"
            y.upload_string(readme_content, readme_path, overwrite=True)
            
            print(f"📝 Создан README.md с инструкциями")
            print(f"\n🎯 Готово! Теперь можно:")
            print(f"1. Делиться ссылкой: {public_url}")
            print(f"2. Загружать файлы через веб-интерфейс")
            print(f"3. Использовать бота для обработки файлов")
            
            return {
                "folder_path": folder_path,
                "public_url": public_url,
                "folder_name": folder_name
            }
        else:
            print("❌ Не удалось получить публичную ссылку")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def list_public_folders():
    """Показывает список публичных папок"""
    
    token = os.getenv('YA_ACCESS_TOKEN')
    if not token:
        print("❌ YA_ACCESS_TOKEN не найден")
        return
    
    try:
        y = yadisk.YaDisk(token=token)
        
        # Получаем список папок в корне
        items = y.listdir('/')
        public_folders = []
        
        for item in items:
            if item.type == 'dir' and item.public_url:
                public_folders.append({
                    'name': item.name,
                    'path': item.path,
                    'public_url': item.public_url,
                    'created': item.created
                })
        
        if public_folders:
            print("📁 Публичные папки:")
            for folder in public_folders:
                print(f"\n📂 {folder['name']}")
                print(f"   🔗 {folder['public_url']}")
                print(f"   📅 {folder['created']}")
        else:
            print("📁 Публичных папок не найдено")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Основная функция"""
    print("🚀 Создание публичной папки для совместной работы")
    print("=" * 50)
    
    # Показываем существующие папки
    print("\n📋 Существующие публичные папки:")
    list_public_folders()
    
    print("\n" + "=" * 50)
    
    # Создаем новую папку
    result = create_public_folder_with_edit()
    
    if result:
        print(f"\n🎉 Папка '{result['folder_name']}' успешно создана!")
        print(f"🔗 Публичная ссылка: {result['public_url']}")
        
        # Сохраняем информацию в файл
        with open('public_folders.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {result['folder_name']}\n")
            f.write(f"URL: {result['public_url']}\n")
            f.write(f"Path: {result['folder_path']}\n")
            f.write("-" * 50 + "\n")

if __name__ == "__main__":
    main() 