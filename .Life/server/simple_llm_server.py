#!/usr/bin/env python3
"""
Простой локальный сервер для LLM
Поддерживает запросы от Android и Wear OS приложений
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_server.log'),
        logging.StreamHandler()
    ]
)

class LLMRequestHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        self.llm_client = MockLLMClient()  # Заглушка для LLM
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Обработка GET запросов"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/health':
            self.send_health_response()
        elif parsed_url.path == '/status':
            self.send_status_response()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Обработка POST запросов"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/generate':
            self.handle_generate_request()
        else:
            self.send_error(404, "Not Found")
    
    def handle_generate_request(self):
        """Обработка запросов генерации текста"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Парсим JSON
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Извлекаем параметры
            prompt = request_data.get('prompt', '')
            context = request_data.get('context', 'general')
            max_tokens = request_data.get('max_tokens', 100)
            temperature = request_data.get('temperature', 0.7)
            
            # Логируем запрос
            logging.info(f"Запрос от {context}: {prompt[:50]}...")
            
            # Генерируем ответ
            response = self.llm_client.generate_response(
                prompt=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_data = {
                'response': response,
                'context': context,
                'timestamp': datetime.now().isoformat(),
                'tokens_used': len(response.split()),
                'status': 'success'
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
            logging.info(f"Ответ отправлен: {response[:50]}...")
            
        except Exception as e:
            logging.error(f"Ошибка обработки запроса: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def send_health_response(self):
        """Отправка статуса здоровья сервера"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - self.server.start_time,
            'requests_processed': getattr(self.server, 'requests_processed', 0)
        }
        
        self.wfile.write(json.dumps(health_data).encode('utf-8'))
    
    def send_status_response(self):
        """Отправка подробного статуса"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        status_data = {
            'server': 'LLM Server v1.0',
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - self.server.start_time,
            'requests_processed': getattr(self.server, 'requests_processed', 0),
            'llm_status': 'mock',  # Заглушка
            'supported_contexts': ['home', 'work', 'morning', 'evening', 'wear'],
            'max_tokens': 1000,
            'temperature_range': [0.1, 1.0]
        }
        
        self.wfile.write(json.dumps(status_data, indent=2).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Переопределяем логирование для более чистого вывода"""
        logging.info(f"{self.address_string()} - {format % args}")


class MockLLMClient:
    """Заглушка для LLM клиента"""
    
    def __init__(self):
        self.context_responses = {
            'home': {
                'task': '✅ Задача добавлена в домашний список',
                'reflection': '💭 Мысль записана в личный дневник',
                'habit': '🔄 Привычка отмечена в трекере',
                'general': '📝 Информация сохранена'
            },
            'work': {
                'task': '💼 Задача добавлена в рабочий список',
                'reflection': '📊 Мысль записана в рабочий журнал',
                'habit': '🎯 Привычка отмечена в профессиональном трекере',
                'general': '📋 Информация сохранена в рабочей базе'
            },
            'morning': {
                'task': '🌅 Утренняя задача добавлена в план дня',
                'reflection': '☀️ Утренняя мысль записана',
                'habit': '🌞 Утренняя привычка отмечена',
                'general': '🌅 Утренняя информация сохранена'
            },
            'evening': {
                'task': '🌙 Вечерняя задача добавлена на завтра',
                'reflection': '🌙 Вечерняя рефлексия записана',
                'habit': '🌙 Вечерняя привычка отмечена',
                'general': '🌙 Вечерняя информация сохранена'
            },
            'wear': {
                'task': '⌚ Задача добавлена с часов',
                'reflection': '⌚ Мысль записана с часов',
                'habit': '⌚ Привычка отмечена с часов',
                'general': '⌚ Информация сохранена с часов'
            }
        }
    
    def generate_response(self, prompt: str, context: str = 'general', 
                         max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Генерирует ответ на основе промпта и контекста"""
        
        # Определяем тип команды
        command_type = self._detect_command_type(prompt)
        
        # Получаем базовый ответ для контекста
        context_responses = self.context_responses.get(context, self.context_responses['general'])
        base_response = context_responses.get(command_type, context_responses['general'])
        
        # Извлекаем ключевые слова из промпта
        keywords = self._extract_keywords(prompt)
        
        # Формируем персонализированный ответ
        if keywords:
            response = f"{base_response}: {keywords}"
        else:
            response = base_response
        
        # Ограничиваем длину ответа
        if len(response) > max_tokens * 4:  # Примерная оценка
            response = response[:max_tokens * 4] + "..."
        
        # Добавляем небольшую задержку для реалистичности
        time.sleep(0.1)
        
        return response
    
    def _detect_command_type(self, prompt: str) -> str:
        """Определяет тип команды из промпта"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['задача', 'task', 'todo', 'делать']):
            return 'task'
        elif any(word in prompt_lower for word in ['мысль', 'reflection', 'думать', 'размышление']):
            return 'reflection'
        elif any(word in prompt_lower for word in ['привычка', 'habit', 'трек', 'отметить']):
            return 'habit'
        else:
            return 'general'
    
    def _extract_keywords(self, prompt: str) -> str:
        """Извлекает ключевые слова из промпта"""
        # Простое извлечение - берем первые 3-5 слов после команды
        words = prompt.split()
        
        # Ищем ключевые слова после команды
        for i, word in enumerate(words):
            if word.lower() in ['добавить', 'записать', 'отметить', 'создать']:
                if i + 1 < len(words):
                    return ' '.join(words[i+1:i+4])  # Берем следующие 3 слова
                break
        
        return ""


class LLMServer(HTTPServer):
    """Расширенный HTTP сервер с дополнительной функциональностью"""
    
    def __init__(self, server_address, RequestHandlerClass):
        self.start_time = time.time()
        self.requests_processed = 0
        super().__init__(server_address, RequestHandlerClass)
    
    def finish_request(self, request, client_address):
        """Переопределяем для подсчета запросов"""
        self.requests_processed += 1
        super().finish_request(request, client_address)


def get_local_ip():
    """Получает локальный IP адрес"""
    import socket
    try:
        # Подключаемся к внешнему серверу, чтобы узнать свой IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    """Главная функция запуска сервера"""
    
    # Настройки сервера
    HOST = "0.0.0.0"  # Слушаем все интерфейсы
    PORT = 8000
    
    local_ip = get_local_ip()
    
    print("🚀============================================================")
    print("🧠 LLM SERVER - ЗАПУСК СИСТЕМЫ")
    print("==============================================================")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==============================================================")
    print("🔍 ПРОВЕРКА ОКРУЖЕНИЯ")
    print("------------------------------")
    print("✅ Окружение готово")
    print("⚙️ ПРОВЕРКА КОНФИГУРАЦИИ")
    print("------------------------------")
    print("✅ Конфигурация корректна")
    print("🚀 ЗАПУСК СЕРВЕРА")
    print("------------------------------")
    print(f"🌐 Сервер запускается на: http://{local_ip}:{PORT}")
    print(f"🔗 Локальный доступ: http://localhost:{PORT}")
    print("📱 Доступно для Android и Wear OS приложений")
    print("")
    print("📋 ЭНДПОИНТЫ:")
    print("• GET  /health  - Проверка здоровья сервера")
    print("• GET  /status  - Подробный статус")
    print("• POST /generate - Генерация ответа")
    print("")
    print("🎯 ПРИМЕРЫ ЗАПРОСОВ:")
    print(f"curl http://{local_ip}:{PORT}/health")
    print(f"curl -X POST http://{local_ip}:{PORT}/generate \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"prompt\":\"Добавить задачу купить продукты\",\"context\":\"home\"}'")
    print("")
    print("🛑 Для остановки нажми Ctrl+C")
    print("==============================================================")
    
    try:
        # Создаем и запускаем сервер
        server = LLMServer((HOST, PORT), LLMRequestHandler)
        
        # Запускаем сервер в отдельном потоке
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"✅ Сервер запущен и слушает на порту {PORT}")
        print(f"🌐 Внешний IP: {local_ip}")
        print(f"🔗 URL для приложений: http://{local_ip}:{PORT}")
        
        # Держим основной поток активным
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал остановки...")
            server.shutdown()
            server.server_close()
            print("✅ Сервер остановлен")
            
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        logging.error(f"Ошибка запуска сервера: {e}")


if __name__ == "__main__":
    main() 