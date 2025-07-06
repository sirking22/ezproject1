#!/usr/bin/env python3
"""
Скрипт тестирования Quick Voice Assistant
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List

# Конфигурация тестирования
TEST_CONFIG = {
    "server_url": "http://localhost:8000",
    "timeout": 10,
    "retry_attempts": 3
}

# Тестовые команды
TEST_COMMANDS = [
    {
        "query": "добавь задачу медитация",
        "expected_action": "create_task",
        "description": "Создание задачи"
    },
    {
        "query": "запиши мысль о продуктивности",
        "expected_action": "save_reflection",
        "description": "Сохранение рефлексии"
    },
    {
        "query": "создай привычку читать книги",
        "expected_action": "create_habit",
        "description": "Создание привычки"
    },
    {
        "query": "покажи прогресс",
        "expected_action": "get_progress",
        "description": "Просмотр прогресса"
    },
    {
        "query": "как мое здоровье",
        "expected_action": "health_analysis",
        "description": "Проверка здоровья"
    }
]

class SystemTester:
    """Класс для тестирования системы"""
    
    def __init__(self):
        self.server_url = TEST_CONFIG["server_url"]
        self.timeout = TEST_CONFIG["timeout"]
        self.results = []
        
    def print_header(self):
        """Вывод заголовка тестирования"""
        print("🧪" + "="*50)
        print("🚀 ТЕСТИРОВАНИЕ QUICK VOICE ASSISTANT")
        print("="*52)
        print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Сервер: {self.server_url}")
        print("="*52)
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """Вывод результата теста"""
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{status} | {test_name}")
        if details:
            print(f"   📝 {details}")
        print()
    
    def test_server_availability(self) -> bool:
        """Тест доступности сервера"""
        try:
            response = requests.get(f"{self.server_url}/ping", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.print_result("Доступность сервера", True)
                    return True
        except Exception as e:
            self.print_result("Доступность сервера", False, f"Ошибка: {e}")
            return False
    
    def test_health_endpoint(self) -> bool:
        """Тест эндпоинта здоровья"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                components = data.get("components", {})
                
                details = []
                if components.get("llm"):
                    details.append("LLM: ✅")
                else:
                    details.append("LLM: ❌")
                
                if components.get("notion"):
                    details.append("Notion: ✅")
                else:
                    details.append("Notion: ❌")
                
                if components.get("telegram"):
                    details.append("Telegram: ✅")
                else:
                    details.append("Telegram: ❌")
                
                self.print_result("Статус здоровья", True, " | ".join(details))
                return True
        except Exception as e:
            self.print_result("Статус здоровья", False, f"Ошибка: {e}")
            return False
    
    def test_voice_command(self, command: Dict[str, Any]) -> bool:
        """Тест голосовой команды"""
        try:
            payload = {
                "query": command["query"],
                "context": "test",
                "timestamp": int(time.time()),
                "user_id": "test_user"
            }
            
            response = requests.post(
                f"{self.server_url}/watch/voice",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Проверка структуры ответа
                if all(key in data for key in ["response", "timestamp"]):
                    details = f"Ответ: {data['response'][:50]}..."
                    if data.get("action"):
                        details += f" | Действие: {data['action']}"
                    
                    self.print_result(
                        command["description"], 
                        True, 
                        details
                    )
                    return True
                else:
                    self.print_result(
                        command["description"], 
                        False, 
                        "Неверная структура ответа"
                    )
                    return False
            else:
                self.print_result(
                    command["description"], 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.print_result(
                command["description"], 
                False, 
                f"Ошибка: {e}"
            )
            return False
    
    def test_telegram_integration(self) -> bool:
        """Тест интеграции с Telegram"""
        try:
            payload = {
                "message": "🧪 Тестовое сообщение от Quick Voice Assistant",
                "source": "system_test"
            }
            
            response = requests.post(
                f"{self.server_url}/telegram/send",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["sent", "failed"]:
                    details = f"Статус: {data['status']}"
                    self.print_result("Интеграция Telegram", True, details)
                    return True
                else:
                    self.print_result(
                        "Интеграция Telegram", 
                        False, 
                        "Неверный статус ответа"
                    )
                    return False
            else:
                self.print_result(
                    "Интеграция Telegram", 
                    False, 
                    f"HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.print_result(
                "Интеграция Telegram", 
                False, 
                f"Ошибка: {e}"
            )
            return False
    
    def test_metrics_endpoint(self) -> bool:
        """Тест эндпоинта метрик"""
        try:
            response = requests.get(f"{self.server_url}/metrics", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if "uptime" in data:
                    details = f"Uptime: {data['uptime']}s"
                    self.print_result("Метрики", True, details)
                    return True
                else:
                    self.print_result("Метрики", False, "Отсутствуют метрики")
                    return False
            else:
                self.print_result("Метрики", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Метрики", False, f"Ошибка: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        self.print_header()
        
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "details": []
        }
        
        # Тест 1: Доступность сервера
        test_results["total_tests"] += 1
        if self.test_server_availability():
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
            print("❌ Сервер недоступен. Запустите сервер: ./start_server.sh")
            return test_results
        
        # Тест 2: Статус здоровья
        test_results["total_tests"] += 1
        if self.test_health_endpoint():
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
        
        # Тест 3: Голосовые команды
        for command in TEST_COMMANDS:
            test_results["total_tests"] += 1
            if self.test_voice_command(command):
                test_results["passed_tests"] += 1
            else:
                test_results["failed_tests"] += 1
        
        # Тест 4: Интеграция Telegram
        test_results["total_tests"] += 1
        if self.test_telegram_integration():
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
        
        # Тест 5: Метрики
        test_results["total_tests"] += 1
        if self.test_metrics_endpoint():
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
        
        return test_results
    
    def print_summary(self, results: Dict[str, Any]):
        """Вывод итогового отчета"""
        print("📊" + "="*50)
        print("📋 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
        print("="*52)
        
        total = results["total_tests"]
        passed = results["passed_tests"]
        failed = results["failed_tests"]
        
        print(f"📈 Всего тестов: {total}")
        print(f"✅ Пройдено: {passed}")
        print(f"❌ Провалено: {failed}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📊 Успешность: {success_rate:.1f}%")
        
        print("="*52)
        
        if failed == 0:
            print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("🚀 Система готова к использованию")
        else:
            print("⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
            print("🔧 Проверьте конфигурацию и логи")
        
        print("="*52)

def main():
    """Основная функция"""
    tester = SystemTester()
    
    try:
        results = tester.run_all_tests()
        tester.print_summary(results)
        
        # Сохранение результатов в файл
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Результаты сохранены в test_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    main() 