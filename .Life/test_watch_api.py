#!/usr/bin/env python3
"""
📱 ТЕСТИРОВАНИЕ API ЧАСОВ
Имитация запросов от Xiaomi Watch S
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

class WatchAPITester:
    """Тестер API для часов"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def test_health(self) -> bool:
        """Тест здоровья сервера"""
        print("🏥 Тестирование здоровья сервера...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Сервер работает")
                return True
            else:
                print(f"❌ Ошибка здоровья: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
    
    def test_voice_command(self, command: str, expected_action: str = None) -> Dict[str, Any]:
        """Тест голосовой команды"""
        print(f"🎤 Тестирование команды: '{command}'")
        
        payload = {
            "query": command,
            "context": "test",
            "timestamp": int(time.time()),
            "user_id": "test_user",
            "device": "xiaomi_watch_s"
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/watch/voice",
                json=payload,
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Ответ получен за {response_time:.2f}с")
                print(f"   Ответ: {data.get('response', 'N/A')[:50]}...")
                print(f"   Действие: {data.get('action', 'N/A')}")
                
                # Проверяем ожидаемое действие
                if expected_action and data.get('action') != expected_action:
                    print(f"⚠️  Ожидалось действие: {expected_action}")
                
                return {
                    "success": True,
                    "response_time": response_time,
                    "response": data,
                    "command": command
                }
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "command": command
                }
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def test_task_creation(self) -> Dict[str, Any]:
        """Тест создания задачи"""
        commands = [
            "добавь задачу протестировать часы",
            "создай задачу купить продукты",
            "задача: позвонить маме",
            "добавить задачу подготовить презентацию"
        ]
        
        results = []
        for command in commands:
            result = self.test_voice_command(command, "create_task")
            results.append(result)
            time.sleep(1)  # Пауза между запросами
        
        return {
            "test_type": "task_creation",
            "results": results,
            "success_count": sum(1 for r in results if r.get("success"))
        }
    
    def test_reflection_creation(self) -> Dict[str, Any]:
        """Тест создания рефлексии"""
        commands = [
            "добавь рефлексию сегодня был продуктивный день",
            "запиши мысли о проекте",
            "рефлексия: нужно больше отдыхать",
            "добавить рефлексию хорошо поработал"
        ]
        
        results = []
        for command in commands:
            result = self.test_voice_command(command, "create_reflection")
            results.append(result)
            time.sleep(1)
        
        return {
            "test_type": "reflection_creation",
            "results": results,
            "success_count": sum(1 for r in results if r.get("success"))
        }
    
    def test_habit_tracking(self) -> Dict[str, Any]:
        """Тест отслеживания привычек"""
        commands = [
            "отметить привычку медитация",
            "привычка: сделал зарядку",
            "записать привычку чтение",
            "привычка медитация выполнена"
        ]
        
        results = []
        for command in commands:
            result = self.test_voice_command(command, "track_habit")
            results.append(result)
            time.sleep(1)
        
        return {
            "test_type": "habit_tracking",
            "results": results,
            "success_count": sum(1 for r in results if r.get("success"))
        }
    
    def test_general_commands(self) -> Dict[str, Any]:
        """Тест общих команд"""
        commands = [
            "как дела",
            "что делать дальше",
            "покажи статистику",
            "помощь",
            "спасибо"
        ]
        
        results = []
        for command in commands:
            result = self.test_voice_command(command)
            results.append(result)
            time.sleep(1)
        
        return {
            "test_type": "general_commands",
            "results": results,
            "success_count": sum(1 for r in results if r.get("success"))
        }
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Тест обработки ошибок"""
        print("🚨 Тестирование обработки ошибок...")
        
        # Тест с пустой командой
        result1 = self.test_voice_command("")
        
        # Тест с очень длинной командой
        long_command = "очень длинная команда " * 50
        result2 = self.test_voice_command(long_command)
        
        # Тест с необычными символами
        result3 = self.test_voice_command("команда с символами: @#$%^&*()")
        
        results = [result1, result2, result3]
        
        return {
            "test_type": "error_handling",
            "results": results,
            "success_count": sum(1 for r in results if r.get("success"))
        }
    
    def test_performance(self) -> Dict[str, Any]:
        """Тест производительности"""
        print("⚡ Тестирование производительности...")
        
        commands = [
            "тест производительности 1",
            "тест производительности 2",
            "тест производительности 3",
            "тест производительности 4",
            "тест производительности 5"
        ]
        
        response_times = []
        results = []
        
        for command in commands:
            result = self.test_voice_command(command)
            results.append(result)
            
            if result.get("success"):
                response_times.append(result.get("response_time", 0))
            
            time.sleep(0.5)  # Короткая пауза
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "test_type": "performance",
            "results": results,
            "avg_response_time": avg_response_time,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0
        }
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Запуск полного набора тестов"""
        print("🧪" + "="*60)
        print("🎯 ПОЛНОЕ ТЕСТИРОВАНИЕ API ЧАСОВ")
        print("="*62)
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*62)
        
        # Проверяем здоровье сервера
        if not self.test_health():
            print("❌ Сервер недоступен. Запустите: python start_quick_voice_assistant.py")
            return {"error": "Server unavailable"}
        
        print("\n🚀 Запуск тестов...")
        
        # Запускаем все тесты
        tests = [
            self.test_task_creation(),
            self.test_reflection_creation(),
            self.test_habit_tracking(),
            self.test_general_commands(),
            self.test_error_handling(),
            self.test_performance()
        ]
        
        # Анализируем результаты
        total_tests = 0
        successful_tests = 0
        
        print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print("="*50)
        
        for test in tests:
            test_type = test.get("test_type", "unknown")
            success_count = test.get("success_count", 0)
            total_count = len(test.get("results", []))
            
            total_tests += total_count
            successful_tests += success_count
            
            status = "✅" if success_count == total_count else "⚠️" if success_count > 0 else "❌"
            print(f"{status} {test_type}: {success_count}/{total_count}")
            
            # Дополнительная информация для производительности
            if test_type == "performance":
                avg_time = test.get("avg_response_time", 0)
                print(f"   Среднее время ответа: {avg_time:.2f}с")
        
        # Общая статистика
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего тестов: {total_tests}")
        print(f"   Успешных: {successful_tests}")
        print(f"   Процент успеха: {success_rate:.1f}%")
        
        # Оценка
        if success_rate >= 90:
            grade = "A+ (Отлично)"
        elif success_rate >= 80:
            grade = "A (Хорошо)"
        elif success_rate >= 70:
            grade = "B (Удовлетворительно)"
        elif success_rate >= 60:
            grade = "C (Требует доработки)"
        else:
            grade = "D (Критические проблемы)"
        
        print(f"   Оценка: {grade}")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        if success_rate >= 90:
            print("   ✅ Система готова к использованию на часах!")
        elif success_rate >= 70:
            print("   ⚠️  Есть проблемы, но система в целом работает")
        else:
            print("   ❌ Требуется серьезная доработка")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "grade": grade,
            "tests": tests
        }

def main():
    """Основная функция"""
    tester = WatchAPITester()
    results = tester.run_full_test_suite()
    
    if "error" not in results:
        print(f"\n🎯 СИСТЕМА ГОТОВА К ТЕСТИРОВАНИЮ НА ЧАСАХ!")
        print("📱 Установи приложение на Xiaomi Watch S и протестируй реальные команды")

if __name__ == "__main__":
    main() 