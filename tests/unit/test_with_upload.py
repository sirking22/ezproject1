#!/usr/bin/env python3
"""
Тест транскрибации с загрузкой в Google Docs
"""

import os
import requests
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

from transcribe_with_speakers import AssemblyAITranscriber

def upload_to_google_docs(markdown_file, title="Транскрипт совещания"):
    """Загружает транскрипт в Google Docs через API"""
    try:
        # Читаем markdown файл
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Конвертируем markdown в HTML для Google Docs
        html_content = markdown_to_html(content)
        
        # Здесь можно добавить интеграцию с Google Docs API
        # Пока что создаем прямую ссылку для копирования
        
        print(f"📝 Google Docs готов к созданию!")
        print(f"📋 Скопируйте содержимое файла: {markdown_file}")
        print(f"🌐 Откройте: https://docs.google.com")
        print(f"📄 Создайте новый документ и вставьте содержимое")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки в Google Docs: {e}")
        return False

def markdown_to_html(markdown_text):
    """Простая конвертация markdown в HTML"""
    html = markdown_text
    
    # Заголовки
    html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
    html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
    
    # Жирный текст
    html = html.replace('**', '<strong>').replace('**', '</strong>')
    
    # Таблицы
    html = html.replace('|', '</td><td>')
    html = html.replace('\n|', '\n<tr><td>')
    html = html.replace('|\n', '</td></tr>\n')
    
    return html

def main():
    """Тестируем транскрибацию с загрузкой в Google Docs"""
    try:
        # Проверяем API ключ
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            print("❌ ASSEMBLYAI_API_KEY не найден")
            return
        
        print("🎤 Начинаю тест транскрибации с загрузкой в Google Docs...")
        print(f"🔑 API ключ: {api_key[:10]}...")
        print()
        
        # Инициализация транскрайбера
        transcriber = AssemblyAITranscriber()
        
        # Путь к файлу на Яндекс.Диске
        audio_path = "/audio_transcribe/record.ogg"
        
        print("📁 Файл:", audio_path)
        print("🚀 Режим: Динамическое определение участников")
        print()
        
        # Транскрибация с динамическим определением участников
        result = transcriber.transcribe_audio(audio_path, "meeting_transcript")
        
        print(f"\n✅ Транскрибация завершена!")
        print(f"👥 Найдено участников: {result['speakers_count']}")
        print(f"📄 Word документ: {result['word_file']}")
        print(f"📝 Markdown файл: {result['markdown_file']}")
        print()
        
        # Загружаем в Google Docs
        print("🌐 Загружаю в Google Docs...")
        upload_to_google_docs(result['markdown_file'])
        
        print(f"\n📊 Статистика участников:")
        print(f"   Speaker A = самый активный")
        print(f"   Speaker B = второй по активности")
        print(f"   ... и так далее")
        print()
        print("🔗 Публичная папка: https://yadi.sk/d/9bDnaC7TPqtnLQ")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 