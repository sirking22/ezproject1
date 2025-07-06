#!/usr/bin/env python3
"""
Тест улучшенной транскрибации с точным распознаванием говорящих
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

from transcribe_with_speakers import AssemblyAITranscriber

def main():
    """Тестируем улучшенную транскрибацию"""
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
        
        print("🎤 Начинаю УЛУЧШЕННУЮ транскрибацию...")
        print(f"📁 Файл: {audio_path}")
        print(f"🔑 API ключ: {api_key[:10]}...")
        print()
        print("🚀 Улучшения:")
        print("  ✅ Точное распознавание 4-6 говорящих")
        print("  ✅ Анализ уверенности распознавания")
        print("  ✅ Статистика по времени и словам")
        print("  ✅ Автоматическое переименование (Speaker A, B, C...)")
        print("  ✅ Разделение на высказывания")
        print("  ✅ Русский язык оптимизация")
        print()
        
        # Транскрибация
        result = transcriber.transcribe_audio(audio_path, "improved_transcript")
        
        print(f"\n✅ Улучшенная транскрибация завершена!")
        print(f"👥 Найдено говорящих: {result['speakers_count']}")
        print(f"📄 Word документ: {result['word_file']}")
        print(f"📝 Markdown файл: {result['markdown_file']}")
        print()
        print("📊 Статистика включена в документы!")
        print("🌐 Публичная папка: https://yadi.sk/d/9bDnaC7TPqtnLQ")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 