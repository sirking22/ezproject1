#!/usr/bin/env python3
"""
Демонстрация упрощенного голосового интерфейса
Максимально быстрый доступ к LLM и базе данных
"""

import asyncio
import time
from datetime import datetime

class QuickVoiceDemo:
    """Демонстрация быстрого голосового доступа"""
    
    def __init__(self):
        self.current_state = "ready"
        self.last_query = None
        self.query_history = []
        
    def show_screen(self, state, message=""):
        """Показ экрана часов"""
        screens = {
            "ready": f"""
┌─────────────────────────┐
│     🎤 Готов            │
│                         │
│   Подними руку          │
│   и говори              │
│                         │
│   [●] [Меню]            │
└─────────────────────────┘""",
            
            "recording": f"""
┌─────────────────────────┐
│     🔴 Запись           │
│                         │
│   ████ ████ ████        │
│   ████ ████ ████        │
│                         │
│   [●] [Стоп]            │
└─────────────────────────┘""",
            
            "processing": f"""
┌─────────────────────────┐
│     🔄 Обработка        │
│                         │
│   Анализирую...         │
│                         │
│   [●] [Отмена]          │
└─────────────────────────┘""",
            
            "response": f"""
┌─────────────────────────┐
│     ✅ Готово           │
│                         │
│   {message:<23} │
│                         │
│   [Повтор] [Новое]      │
└─────────────────────────┘"""
        }
        
        print(f"\n📱 СОСТОЯНИЕ: {state.upper()}")
        print(screens.get(state, "Неизвестное состояние"))
    
    def simulate_wake_up(self):
        """Симуляция пробуждения экрана"""
        print("\n🔄 ПРОБУЖДЕНИЕ ЭКРАНА")
        print("👆 Поднимаешь руку → экран включается")
        
        self.current_state = "ready"
        self.show_screen("ready")
        
        # Автоматическая активация через 1 секунду
        print("⏱️ Через 1 секунду автоматически готов к записи...")
        time.sleep(1)
        
        return self.start_recording()
    
    def start_recording(self):
        """Начало записи"""
        print("\n🎤 НАЧАЛО ЗАПИСИ")
        self.current_state = "recording"
        self.show_screen("recording")
        
        # Симуляция записи
        print("🎙️ Запись голоса...")
        time.sleep(2)
        
        # Моковые команды
        commands = [
            "добавь задачу медитация",
            "запиши мысль о проекте",
            "покажи прогресс",
            "создай привычку чтение",
            "как мое здоровье",
            "что мне делать сегодня"
        ]
        
        command = commands[len(self.query_history) % len(commands)]
        print(f"📝 Распознано: '{command}'")
        
        return self.process_query(command)
    
    def process_query(self, query):
        """Обработка запроса"""
        print(f"\n🧠 ОБРАБОТКА: '{query}'")
        
        self.current_state = "processing"
        self.show_screen("processing")
        
        # Сохраняем в историю
        self.query_history.append({
            "query": query,
            "timestamp": datetime.now()
        })
        self.last_query = query
        
        # Симуляция обработки LLM
        print("🔄 Отправка в LLM...")
        time.sleep(1)
        print("🧠 Анализ контекста...")
        time.sleep(1)
        print("📊 Поиск в базе данных...")
        time.sleep(1)
        
        # Получаем ответ
        response = self.get_llm_response(query)
        
        return self.show_response(response)
    
    def get_llm_response(self, query):
        """Получение ответа от LLM"""
        responses = {
            "добавь задачу медитация": {
                "short": "Задача добавлена",
                "full": "Задача 'Медитация' добавлена в ваш список. Рекомендую выполнить утром или вечером для лучшего эффекта.",
                "action": "add_task",
                "data": {"task": "Медитация", "category": "wellness"}
            },
            "запиши мысль о проекте": {
                "short": "Мысль сохранена",
                "full": "Мысль о проекте сохранена в reflections. Рекомендую вернуться к ней через неделю для оценки.",
                "action": "save_thought",
                "data": {"content": "мысль о проекте", "type": "reflection"}
            },
            "покажи прогресс": {
                "short": "Прогресс готов",
                "full": "Ваш прогресс: 85% шагов, 90% калорий, 7/10 привычек выполнено. Отличные результаты!",
                "action": "show_progress",
                "data": {"steps": 85, "calories": 90, "habits": 7}
            },
            "создай привычку чтение": {
                "short": "Привычка создана",
                "full": "Привычка 'Чтение' создана. Рекомендую 30 минут в день перед сном.",
                "action": "create_habit",
                "data": {"habit": "Чтение", "duration": "30 минут"}
            },
            "как мое здоровье": {
                "short": "Здоровье отличное",
                "full": "Ваше здоровье в отличном состоянии! Пульс 75 уд/мин, стресс 30%. Рекомендую продолжить текущий ритм.",
                "action": "health_check",
                "data": {"heart_rate": 75, "stress": 30}
            },
            "что мне делать сегодня": {
                "short": "Рекомендации готовы",
                "full": "Учитывая ваши показатели, рекомендую: 1) Вечернюю прогулку 2) Медитацию 3) Планирование завтрашнего дня",
                "action": "recommendations",
                "data": {"activities": ["прогулка", "медитация", "планирование"]}
            }
        }
        
        return responses.get(query, {
            "short": "Обработано",
            "full": "Запрос обработан. Что еще могу помочь?",
            "action": "general",
            "data": {}
        })
    
    def show_response(self, response):
        """Показ ответа"""
        print(f"\n✅ ОТВЕТ: {response['short']}")
        
        self.current_state = "response"
        self.show_screen("response", response['short'])
        
        # Показываем полный ответ
        print(f"\n🤖 ПОЛНЫЙ ОТВЕТ:")
        print(f"   {response['full']}")
        
        # Показываем действие
        if response['action'] != 'general':
            print(f"\n⚡ ВЫПОЛНЕНО ДЕЙСТВИЕ: {response['action']}")
            print(f"   Данные: {response['data']}")
        
        # Отправка в Telegram
        print(f"\n📱 ОТПРАВЛЕНО В TELEGRAM:")
        print(f"   {response['full']}")
        
        return response
    
    def repeat_last_query(self):
        """Повтор последнего запроса"""
        if self.last_query:
            print(f"\n🔄 ПОВТОР: '{self.last_query}'")
            return self.process_query(self.last_query)
        else:
            print("\n❌ Нет последнего запроса")
            return None
    
    def show_quick_menu(self):
        """Показ быстрого меню"""
        print("\n⚡ БЫСТРОЕ МЕНЮ:")
        print("  🎤 - Новая запись")
        print("  🔄 - Повторить последнее")
        print("  📊 - Показать прогресс")
        print("  ⚙️ - Настройки")
        print("  📝 - История запросов")
    
    def show_history(self):
        """Показ истории запросов"""
        print(f"\n📝 ИСТОРИЯ ЗАПРОСОВ ({len(self.query_history)}):")
        for i, item in enumerate(self.query_history[-5:], 1):
            time_str = item['timestamp'].strftime("%H:%M")
            print(f"  {i}. [{time_str}] {item['query']}")
    
    def simulate_full_workflow(self):
        """Симуляция полного рабочего процесса"""
        print("🚀 ДЕМОНСТРАЦИЯ БЫСТРОГО ГОЛОСОВОГО ДОСТУПА")
        print("=" * 50)
        print("🎯 Цель: максимально быстрый доступ к LLM и базе данных")
        print("=" * 50)
        
        # Симуляция нескольких запросов
        workflows = [
            "Пробуждение экрана → запись → обработка → ответ",
            "Жест активации → запись → обработка → ответ", 
            "Ключевое слово → запись → обработка → ответ"
        ]
        
        for i, workflow in enumerate(workflows, 1):
            print(f"\n{i}. 🔄 {workflow}")
            print("-" * 40)
            
            if i == 1:
                # Автоматическая активация
                self.simulate_wake_up()
            elif i == 2:
                # Жест активации
                print("\n👆 Жест активации (встряхивание)")
                self.start_recording()
            else:
                # Ключевое слово
                print("\n🎤 Ключевое слово 'ассистент'")
                self.start_recording()
            
            time.sleep(2)
        
        # Показ меню и истории
        print("\n" + "=" * 50)
        print("📱 ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ")
        print("=" * 50)
        
        self.show_quick_menu()
        self.show_history()
        
        # Повтор последнего запроса
        print("\n🔄 ДЕМОНСТРАЦИЯ ПОВТОРА:")
        self.repeat_last_query()
        
        print("\n✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print("🎤 Система готова к использованию!")
        print("⚡ Максимально быстрый доступ к LLM и базе данных!")

async def main():
    """Главная функция"""
    demo = QuickVoiceDemo()
    demo.simulate_full_workflow()

if __name__ == "__main__":
    asyncio.run(main()) 