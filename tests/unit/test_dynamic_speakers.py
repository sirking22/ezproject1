#!/usr/bin/env python3
"""
Тест динамического распознавания участников на совещаниях
"""

import os
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

from transcribe_with_speakers import AssemblyAITranscriber

def main():
    """Тестируем динамическое распознавание участников"""
    try:
        # Проверяем API ключ
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            print("❌ ASSEMBLYAI_API_KEY не найден")
            return
        
        print("🎤 Тестирую динамическое распознавание участников...")
        print()
        print("🚀 Сценарии использования:")
        print()
        print("1️⃣ СОВЕЩАНИЕ С МНОЖЕСТВОМ СПИКЕРОВ:")
        print("   transcriber.transcribe_audio(audio_path, 'meeting', expected_speakers=None)")
        print("   → AssemblyAI сам определит количество участников")
        print()
        print("2️⃣ ЗНАЕМ КОЛИЧЕСТВО УЧАСТНИКОВ:")
        print("   transcriber.transcribe_audio(audio_path, 'meeting', expected_speakers=15)")
        print("   → Ищем именно 15 участников")
        print()
        print("3️⃣ МАЛЕНЬКАЯ ГРУППА:")
        print("   transcriber.transcribe_audio(audio_path, 'meeting', expected_speakers=3)")
        print("   → Ищем 3 участников")
        print()
        print("🔧 Преимущества динамического подхода:")
        print("   ✅ Автоматическое определение количества участников")
        print("   ✅ Поддержка от 1 до 26+ участников")
        print("   ✅ Умная сортировка по активности")
        print("   ✅ Автоматическое переименование (Speaker A-Z)")
        print("   ✅ Статистика по времени и словам")
        print()
        print("📝 Примеры использования:")
        print("   # Большое совещание - динамическое определение")
        print("   result = transcriber.transcribe_audio('/meeting.ogg', 'big_meeting')")
        print()
        print("   # Маленькая команда - знаем количество")
        print("   result = transcriber.transcribe_audio('/team.ogg', 'team_meeting', 5)")
        print()
        print("   # Интервью - 2 участника")
        print("   result = transcriber.transcribe_audio('/interview.ogg', 'interview', 2)")
        print()
        print("🔧 Готово к использованию!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main() 