#!/usr/bin/env python3
"""
Упрощенный LLM сервер для Windows
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

class SimpleLLMHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/health':
            self.send_health_response()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/generate':
            self.handle_generate_request()
        else:
            self.send_error(404, "Not Found")
    
    def handle_generate_request(self):
        """Обработка запросов генерации"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Парсим JSON
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Извлекаем параметры
            prompt = request_data.get('prompt', '')
            context = request_data.get('context', 'general')
            
            print(f"Получен запрос: {prompt[:50]}... (контекст: {context})")
            
            # Генерируем простой ответ
            response = self.generate_simple_response(prompt, context)
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                'response': response,
                'context': context,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
            print(f"Отправлен ответ: {response}")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def generate_simple_response(self, prompt, context):
        """Генерирует простой ответ"""
        prompt_lower = prompt.lower()
        
        # Определяем тип команды
        if any(word in prompt_lower for word in ['задача', 'task', 'todo']):
            if context == 'wear':
                return "⌚ Задача добавлена с часов"
            elif context == 'work':
                return "💼 Задача добавлена в рабочий список"
            elif context == 'morning':
                return "🌅 Утренняя задача добавлена"
            else:
                return "✅ Задача добавлена"
        
        elif any(word in prompt_lower for word in ['мысль', 'reflection', 'думать']):
            if context == 'wear':
                return "⌚ Мысль записана с часов"
            elif context == 'work':
                return "📊 Мысль записана в рабочий журнал"
            elif context == 'evening':
                return "🌙 Вечерняя мысль записана"
            else:
                return "💭 Мысль записана"
        
        elif any(word in prompt_lower for word in ['привычка', 'habit', 'трек']):
            if context == 'wear':
                return "⌚ Привычка отмечена с часов"
            elif context == 'work':
                return "🎯 Привычка отмечена в профессиональном трекере"
            else:
                return "🔄 Привычка отмечена"
        
        else:
            return "📝 Информация сохранена"
    
    def send_health_response(self):
        """Отправка статуса здоровья"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'server': 'Simple LLM Server v1.0',
            'platform': 'Windows'
        }
        
        self.wfile.write(json.dumps(health_data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Переопределяем логирование"""
        print(f"{datetime.now().strftime('%H:%M:%S')} - {format % args}")


def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    """Главная функция"""
    
    HOST = "0.0.0.0"
    PORT = 8000
    
    local_ip = get_local_ip()
    
    print("🚀============================================================")
    print("🧠 SIMPLE LLM SERVER - ЗАПУСК")
    print("==============================================================")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==============================================================")
    print("✅ Сервер готов к запуску")
    print(f"🌐 IP адрес: {local_ip}")
    print(f"🔗 URL: http://{local_ip}:{PORT}")
    print("")
    print("📋 ЭНДПОИНТЫ:")
    print("• GET  /health  - Проверка здоровья")
    print("• POST /generate - Генерация ответа")
    print("")
    print("🧪 ТЕСТ:")
    print(f"curl http://{local_ip}:{PORT}/health")
    print("")
    print("🛑 Для остановки нажми Ctrl+C")
    print("==============================================================")
    
    try:
        # Создаем и запускаем сервер
        server = HTTPServer((HOST, PORT), SimpleLLMHandler)
        
        print(f"✅ Сервер запущен на порту {PORT}")
        print(f"🌐 Доступен по адресу: http://{local_ip}:{PORT}")
        print("📱 Готов принимать запросы от Android и Wear OS")
        print("")
        
        # Запускаем сервер
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
        print("✅ Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        print("🔧 Проверьте:")
        print("   - Не занят ли порт 8000")
        print("   - Есть ли права администратора")
        print("   - Не блокирует ли файрвол")


if __name__ == "__main__":
    main() 