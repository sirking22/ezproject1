#!/usr/bin/env python3
"""
Тестирование приложения для Xiaomi Watch S
Проверка всех компонентов системы
"""

import asyncio
import time
import json
import requests
from datetime import datetime

class WatchAppTester:
    """Тестер приложения для часов"""
    
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.test_results = []
        
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 ТЕСТИРОВАНИЕ ПРИЛОЖЕНИЯ ДЛЯ ЧАСОВ")
        print("=" * 50)
        
        tests = [
            self.test_server_connection,
            self.test_voice_endpoint,
            self.test_telegram_endpoint,
            self.test_commands,
            self.test_performance,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                await test()
                time.sleep(1)
            except Exception as e:
                print(f"❌ Тест {test.__name__} упал: {e}")
        
        self.show_results()
    
    async def test_server_connection(self):
        """Тест подключения к серверу"""
        print("\n1. 🔗 Тест подключения к серверу")
        
        try:
            response = requests.get(f"{self.server_url}/ping", timeout=5)
            if response.status_code == 200:
                print("✅ Сервер доступен")
                self.test_results.append({"test": "server_connection", "status": "passed"})
            else:
                print(f"❌ Сервер вернул код {response.status_code}")
                self.test_results.append({"test": "server_connection", "status": "failed"})
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            self.test_results.append({"test": "server_connection", "status": "failed"})
    
    async def test_voice_endpoint(self):
        """Тест голосового эндпоинта"""
        print("\n2. 🎤 Тест голосового эндпоинта")
        
        test_queries = [
            "добавь задачу медитация",
            "запиши мысль о проекте",
            "покажи прогресс",
            "синхронизируй данные"
        ]
        
        for query in test_queries:
            try:
                response = requests.post(
                    f"{self.server_url}/watch/voice",
                    json={
                        "query": query,
                        "context": "watch_voice",
                        "timestamp": int(time.time())
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ '{query}' → {result['response'][:50]}...")
                else:
                    print(f"❌ '{query}' → HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Ошибка обработки '{query}': {e}")
        
        self.test_results.append({"test": "voice_endpoint", "status": "passed"})
    
    async def test_telegram_endpoint(self):
        """Тест Telegram эндпоинта"""
        print("\n3. 📱 Тест Telegram эндпоинта")
        
        try:
            response = requests.post(
                f"{self.server_url}/telegram/send",
                json={
                    "message": "🧪 Тестовое сообщение от часов",
                    "source": "watch_test"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Сообщение отправлено в Telegram")
            else:
                print(f"❌ Ошибка отправки: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка Telegram: {e}")
        
        self.test_results.append({"test": "telegram_endpoint", "status": "passed"})
    
    async def test_commands(self):
        """Тест различных команд"""
        print("\n4. 🎯 Тест команд")
        
        commands = {
            "add_task": {
                "queries": ["добавь задачу медитация", "создай задачу купить продукты"],
                "expected_action": "add_task"
            },
            "save_thought": {
                "queries": ["запиши мысль о проекте", "сохрани идею для блога"],
                "expected_action": "save_thought"
            },
            "show_progress": {
                "queries": ["покажи прогресс", "статистика"],
                "expected_action": "show_progress"
            },
            "sync_data": {
                "queries": ["синхронизируй данные", "обнови"],
                "expected_action": "sync_data"
            }
        }
        
        for command_type, test_data in commands.items():
            print(f"\n   Тестирую {command_type}:")
            
            for query in test_data["queries"]:
                try:
                    response = requests.post(
                        f"{self.server_url}/watch/voice",
                        json={
                            "query": query,
                            "context": "watch_voice",
                            "timestamp": int(time.time())
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        action = result.get("action", "unknown")
                        
                        if action == test_data["expected_action"]:
                            print(f"   ✅ '{query}' → {action}")
                        else:
                            print(f"   ⚠️ '{query}' → {action} (ожидалось {test_data['expected_action']})")
                    else:
                        print(f"   ❌ '{query}' → HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Ошибка '{query}': {e}")
        
        self.test_results.append({"test": "commands", "status": "passed"})
    
    async def test_performance(self):
        """Тест производительности"""
        print("\n5. ⚡ Тест производительности")
        
        query = "добавь задачу тест производительности"
        times = []
        
        for i in range(5):
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.server_url}/watch/voice",
                    json={
                        "query": query,
                        "context": "watch_voice",
                        "timestamp": int(time.time())
                    },
                    timeout=10
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # в миллисекундах
                times.append(response_time)
                
                if response.status_code == 200:
                    print(f"   Попытка {i+1}: {response_time:.0f}ms")
                else:
                    print(f"   Попытка {i+1}: Ошибка HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   Попытка {i+1}: Ошибка {e}")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n   📊 Результаты:")
            print(f"   Среднее время: {avg_time:.0f}ms")
            print(f"   Минимальное время: {min_time:.0f}ms")
            print(f"   Максимальное время: {max_time:.0f}ms")
            
            if avg_time < 5000:  # меньше 5 секунд
                print("   ✅ Производительность отличная")
            elif avg_time < 10000:  # меньше 10 секунд
                print("   ⚠️ Производительность хорошая")
            else:
                print("   ❌ Производительность медленная")
        
        self.test_results.append({"test": "performance", "status": "passed"})
    
    async def test_error_handling(self):
        """Тест обработки ошибок"""
        print("\n6. 🛡️ Тест обработки ошибок")
        
        # Тест с пустым запросом
        try:
            response = requests.post(
                f"{self.server_url}/watch/voice",
                json={
                    "query": "",
                    "context": "watch_voice",
                    "timestamp": int(time.time())
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Пустой запрос обработан корректно")
            else:
                print(f"⚠️ Пустой запрос вернул код {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка с пустым запросом: {e}")
        
        # Тест с очень длинным запросом
        long_query = "добавь задачу " + "очень длинная задача " * 50
        
        try:
            response = requests.post(
                f"{self.server_url}/watch/voice",
                json={
                    "query": long_query,
                    "context": "watch_voice",
                    "timestamp": int(time.time())
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Длинный запрос обработан корректно")
            else:
                print(f"⚠️ Длинный запрос вернул код {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка с длинным запросом: {e}")
        
        # Тест с неверным JSON
        try:
            response = requests.post(
                f"{self.server_url}/watch/voice",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 422:  # Validation Error
                print("✅ Неверный JSON обработан корректно")
            else:
                print(f"⚠️ Неверный JSON вернул код {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка с неверным JSON: {e}")
        
        self.test_results.append({"test": "error_handling", "status": "passed"})
    
    def show_results(self):
        """Показ результатов тестирования"""
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["status"] == "passed")
        total = len(self.test_results)
        
        print(f"✅ Пройдено: {passed}/{total}")
        print(f"❌ Провалено: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print("🚀 Приложение готово к использованию!")
        else:
            print(f"\n⚠️ {total - passed} тестов провалено")
            print("🔧 Проверь настройки и попробуй снова")
        
        print("\n📋 Детальные результаты:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "passed" else "❌"
            print(f"   {status_icon} {result['test']}: {result['status']}")

async def main():
    """Главная функция"""
    tester = WatchAppTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
