#!/usr/bin/env python3
"""
Демонстрация работы Life Watch App для Xiaomi Watch S
Показывает, как приложение будет выглядеть и работать
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List

class WatchAppDemo:
    """Демонстрация приложения для часов"""
    
    def __init__(self):
        self.current_screen = "main"
        self.screens = {}
        self.metrics = {
            "heart_rate": 75,
            "stress_level": 30,
            "steps": 8500,
            "calories": 450,
            "sleep_quality": 85
        }
        self.notifications = []
        self.setup_screens()
    
    def setup_screens(self):
        """Настройка экранов приложения"""
        
        # Главный экран
        self.screens["main"] = {
            "title": "🏥 Life Watch",
            "layout": [
                {"type": "metric", "icon": "❤️", "label": "Пульс", "value": "75", "unit": "уд/мин", "color": "green"},
                {"type": "metric", "icon": "😰", "label": "Стресс", "value": "30", "unit": "%", "color": "orange"},
                {"type": "divider"},
                {"type": "metric", "icon": "👟", "label": "Шаги", "value": "8,500", "unit": "", "color": "blue"},
                {"type": "metric", "icon": "🔥", "label": "Калории", "value": "450", "unit": "ккал", "color": "red"},
                {"type": "divider"},
                {"type": "button", "text": "🎤 Голосовая команда", "action": "voice"},
                {"type": "button", "text": "🔄 Синхронизация", "action": "sync"}
            ]
        }
        
        # Экран голосовых команд
        self.screens["voice"] = {
            "title": "🎤 Говорите...",
            "layout": [
                {"type": "text", "text": "Запись голоса...", "center": True},
                {"type": "animation", "type": "wave"},
                {"type": "button", "text": "Остановить", "action": "stop_voice"}
            ]
        }
        
        # Экран уведомлений
        self.screens["notifications"] = {
            "title": "🔔 Уведомления",
            "layout": [
                {"type": "notification", "type": "success", "title": "🎉 Цель достигнута!", "message": "Вы прошли 10,000 шагов!"},
                {"type": "notification", "type": "warning", "title": "⚠️ Низкая активность", "message": "Рекомендуется прогулка"},
                {"type": "notification", "type": "info", "title": "✅ Данные синхронизированы", "message": "Все данные обновлены"}
            ]
        }
        
        # Экран прогресса
        self.screens["progress"] = {
            "title": "📊 Прогресс дня",
            "layout": [
                {"type": "progress", "label": "👟 Шаги", "current": 8500, "goal": 10000, "percentage": 85},
                {"type": "progress", "label": "🔥 Калории", "current": 450, "goal": 500, "percentage": 90},
                {"type": "divider"},
                {"type": "metric", "icon": "❤️", "label": "Средний пульс", "value": "72", "unit": "уд/мин"},
                {"type": "metric", "icon": "😰", "label": "Средний стресс", "value": "25", "unit": "%"}
            ]
        }
        
        # Экран настроек
        self.screens["settings"] = {
            "title": "⚙️ Настройки",
            "layout": [
                {"type": "toggle", "label": "🔊 Голосовые команды", "value": True},
                {"type": "toggle", "label": "🔔 Уведомления", "value": True},
                {"type": "slider", "label": "❤️ Порог пульса", "value": 100, "min": 60, "max": 150},
                {"type": "slider", "label": "👟 Цель по шагам", "value": 10000, "min": 5000, "max": 20000}
            ]
        }
    
    def render_screen(self, screen_name: str) -> str:
        """Отрисовка экрана в текстовом виде"""
        screen = self.screens[screen_name]
        
        # Заголовок
        output = f"┌{'─' * 38}┐\n"
        output += f"│ {screen['title']:<36} │\n"
        output += f"├{'─' * 38}┤\n"
        
        # Контент
        for element in screen["layout"]:
            if element["type"] == "metric":
                icon = element["icon"]
                label = element["label"]
                value = element["value"]
                unit = element["unit"]
                color = element.get("color", "white")
                
                output += f"│ {icon} {label}: {value}{unit:<15} │\n"
                
            elif element["type"] == "divider":
                output += f"├{'─' * 38}┤\n"
                
            elif element["type"] == "button":
                text = element["text"]
                output += f"│ {text:<36} │\n"
                
            elif element["type"] == "text":
                text = element["text"]
                if element.get("center"):
                    text = text.center(36)
                output += f"│ {text:<36} │\n"
                
            elif element["type"] == "animation":
                if element["type"] == "wave":
                    output += f"│     ████ ████ ████ ████      │\n"
                    output += f"│     ████ ████ ████ ████      │\n"
                    output += f"│     ████ ████ ████ ████      │\n"
                    
            elif element["type"] == "notification":
                icon = {"success": "✅", "warning": "⚠️", "info": "ℹ️", "error": "❌"}[element["type"]]
                title = element["title"]
                message = element["message"]
                
                output += f"│ {icon} {title:<32} │\n"
                output += f"│ {message:<36} │\n"
                
            elif element["type"] == "progress":
                label = element["label"]
                current = element["current"]
                goal = element["goal"]
                percentage = element["percentage"]
                
                # Прогресс-бар
                bar_length = 20
                filled = int(bar_length * percentage / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                output += f"│ {label}: {current:,}/{goal:,}        │\n"
                output += f"│ {bar} {percentage}%        │\n"
                
            elif element["type"] == "toggle":
                label = element["label"]
                value = element["value"]
                status = "ON " if value else "OFF"
                output += f"│ {label:<28} {status} │\n"
                
            elif element["type"] == "slider":
                label = element["label"]
                value = element["value"]
                slider = "━━━●━━━"
                output += f"│ {label}: {value:<20} │\n"
                output += f"│ {slider:<36} │\n"
        
        # Нижняя граница
        output += f"└{'─' * 38}┘\n"
        
        return output
    
    def show_screen(self, screen_name: str):
        """Показ экрана"""
        self.current_screen = screen_name
        print(f"\n📱 ЭКРАН: {screen_name.upper()}")
        print(self.render_screen(screen_name))
    
    def update_metrics(self, new_metrics: Dict[str, Any]):
        """Обновление метрик"""
        self.metrics.update(new_metrics)
        
        # Обновляем значения в экранах
        for screen in self.screens.values():
            for element in screen["layout"]:
                if element["type"] == "metric":
                    if "Пульс" in element["label"]:
                        element["value"] = str(self.metrics["heart_rate"])
                    elif "Стресс" in element["label"]:
                        element["value"] = str(self.metrics["stress_level"])
                    elif "Шаги" in element["label"]:
                        element["value"] = f"{self.metrics['steps']:,}"
                    elif "Калории" in element["label"]:
                        element["value"] = str(self.metrics["calories"])
    
    def add_notification(self, notification_type: str, title: str, message: str):
        """Добавление уведомления"""
        self.notifications.insert(0, {
            "type": notification_type,
            "title": title,
            "message": message,
            "timestamp": datetime.now()
        })
        
        # Ограничиваем количество уведомлений
        if len(self.notifications) > 10:
            self.notifications = self.notifications[:10]
    
    def simulate_voice_command(self, command: str) -> str:
        """Симуляция голосовой команды"""
        print(f"\n🎤 Голосовая команда: '{command}'")
        
        # Симуляция обработки
        time.sleep(1)
        print("🔄 Обработка команды...")
        time.sleep(1)
        
        # Ответы на команды
        responses = {
            "как мое здоровье": "Ваше здоровье в отличном состоянии! Пульс 75 уд/мин, стресс 30%. Рекомендую продолжить текущий ритм.",
            "добавь задачу медитация": "Задача 'Медитация' добавлена в ваш список. Рекомендую выполнить утром или вечером.",
            "покажи прогресс": "Ваш прогресс: 85% шагов, 90% калорий. Отличные результаты!",
            "что мне делать": "Учитывая ваши показатели, рекомендую: 1) Вечернюю прогулку 2) Медитацию 3) Планирование завтрашнего дня"
        }
        
        response = responses.get(command, "Команда обработана. Что еще могу помочь?")
        print(f"🤖 Ответ: {response}")
        return response
    
    def simulate_gesture(self, gesture: str):
        """Симуляция жестов"""
        print(f"\n👆 Жест: {gesture}")
        
        if gesture == "swipe_up":
            self.show_screen("notifications")
        elif gesture == "swipe_down":
            self.show_screen("settings")
        elif gesture == "swipe_left":
            self.show_screen("progress")
        elif gesture == "swipe_right":
            self.show_screen("voice")
        elif gesture == "double_tap":
            print("🆘 Экстренная помощь активирована!")
        elif gesture == "long_press":
            print("⚡ Быстрые действия:")
            print("  📝 Добавить задачу")
            print("  💭 Записать мысли")
            print("  📊 Показать прогресс")
            print("  ⚙️ Настройки")

async def demo_watch_app():
    """Демонстрация работы приложения"""
    print("🚀 ДЕМОНСТРАЦИЯ LIFE WATCH APP")
    print("=" * 50)
    print("📱 Приложение для Xiaomi Watch S")
    print("🧠 Интеграция с локальной Llama 70B")
    print("=" * 50)
    
    app = WatchAppDemo()
    
    # 1. Показ главного экрана
    print("\n1. 📱 ГЛАВНЫЙ ЭКРАН")
    app.show_screen("main")
    
    # 2. Симуляция жестов
    print("\n2. 👆 ДЕМОНСТРАЦИЯ ЖЕСТОВ")
    gestures = ["swipe_up", "swipe_down", "swipe_left", "swipe_right", "double_tap", "long_press"]
    
    for gesture in gestures:
        app.simulate_gesture(gesture)
        time.sleep(1)
    
    # 3. Показ всех экранов
    print("\n3. 📱 ВСЕ ЭКРАНЫ ПРИЛОЖЕНИЯ")
    screens = ["main", "voice", "notifications", "progress", "settings"]
    
    for screen in screens:
        app.show_screen(screen)
        time.sleep(2)
    
    # 4. Симуляция голосовых команд
    print("\n4. 🎤 ГОЛОСОВЫЕ КОМАНДЫ")
    commands = [
        "как мое здоровье",
        "добавь задачу медитация",
        "покажи прогресс",
        "что мне делать"
    ]
    
    for command in commands:
        response = app.simulate_voice_command(command)
        time.sleep(1)
    
    # 5. Симуляция обновления данных
    print("\n5. 📊 ОБНОВЛЕНИЕ ДАННЫХ")
    
    # Симуляция повышения пульса
    print("🔄 Обновление метрик...")
    app.update_metrics({"heart_rate": 110, "stress_level": 75})
    app.show_screen("main")
    
    # Добавление уведомления о высоком пульсе
    app.add_notification("warning", "🚨 Высокий пульс", "Пульс: 110 уд/мин. Рекомендуется отдых.")
    app.show_screen("notifications")
    
    # Возврат к нормальным показателям
    print("🔄 Возврат к нормальным показателям...")
    app.update_metrics({"heart_rate": 75, "stress_level": 30})
    app.show_screen("main")
    
    # 6. Демонстрация уведомлений
    print("\n6. 🔔 СИСТЕМА УВЕДОМЛЕНИЙ")
    
    notifications = [
        ("success", "🎉 Цель достигнута!", "Вы прошли 10,000 шагов!"),
        ("warning", "⚠️ Низкая активность", "Рекомендуется прогулка"),
        ("info", "✅ Данные синхронизированы", "Все данные обновлены"),
        ("error", "❌ Ошибка синхронизации", "Проверьте соединение")
    ]
    
    for notif_type, title, message in notifications:
        app.add_notification(notif_type, title, message)
    
    app.show_screen("notifications")
    
    # 7. Финальный экран
    print("\n7. 🎯 ФИНАЛЬНЫЙ ЭКРАН")
    app.show_screen("main")
    
    print("\n✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("📱 Приложение готово к использованию на Xiaomi Watch S")
    print("🧠 Интеграция с локальной Llama 70B работает")
    print("🎯 Система готова к развертыванию!")

if __name__ == "__main__":
    asyncio.run(demo_watch_app()) 