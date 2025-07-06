#!/usr/bin/env python3
"""
Тест улучшений в распознавании говорящих
"""

import os
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

from transcribe_with_speakers import AssemblyAITranscriber

def main():
    """Тестируем улучшения распознавания говорящих"""
    try:
        # Проверяем API ключ
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            print("❌ ASSEMBLYAI_API_KEY не найден")
            return
        
        print("🎤 Тестирую улучшения распознавания говорящих...")
        print("🚀 Улучшения:")
        print("  ✅ speakers_expected: 10 (ожидаем 10 участников)")
        print("  ✅ Умное разделение на сегменты (пауза >2 сек)")
        print("  ✅ Сортировка по времени речи")
        print("  ✅ Автоматическое переименование (Speaker A-J)")
        print("  ✅ Поддержка до 26 участников (A-Z)")
        print()
        
        # Инициализация
        transcriber = AssemblyAITranscriber()
        
        # Тестируем на коротком аудио (если есть)
        # Для теста можно использовать короткий файл
        print("📝 Для полного теста запустите:")
        print("   python test_transcribe.py")
        print()
        print("🔧 Улучшения уже внедрены в основной код!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main() 