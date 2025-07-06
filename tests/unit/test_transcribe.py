#!/usr/bin/env python3
"""
Тест транскрибации аудио файла record.ogg
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

from transcribe_with_speakers import AssemblyAITranscriber

def main():
    """Тестируем транскрибацию"""
    try:
        # Проверяем API ключ
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            print("❌ ASSEMBLYAI_API_KEY не найден в переменных окружения")
            print("Проверьте .env файл")
            return
        
        # Инициализация транскрайбера
        transcriber = AssemblyAITranscriber()
        
        # Путь к файлу на Яндекс.Диске
        audio_path = "/audio_transcribe/record.ogg"
        
        print("🎤 Начинаю транскрибацию аудио файла...")
        print(f"📁 Файл: {audio_path}")
        print(f"🔑 API ключ: {api_key[:10]}...")
        print()
        
        # Транскрибация
        result = transcriber.transcribe_audio(audio_path, "record_transcript")
        
        print(f"\n✅ Транскрибация завершена успешно!")
        print(f"📄 Word документ: {result['word_file']}")
        print(f"📝 Markdown файл: {result['markdown_file']}")
        print(f"\n📋 Текст транскрипта:\n")
        print("-" * 50)
        print(result['text'])
        print("-" * 50)
        
        # Создаем публичную ссылку на папку с результатами
        print(f"\n🌐 Публичная ссылка на папку: https://yadi.sk/d/9bDnaC7TPqtnLQ")
        print("📝 Для редактирования в Google Docs:")
        print("1. Откройте https://docs.google.com")
        print("2. Создайте новый документ")
        print("3. Скопируйте содержимое .md файла")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 