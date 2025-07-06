#!/usr/bin/env python3
"""
Простой тестовый сервер
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class TestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'message': 'Сервер работает!'
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path == '/generate':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'response': '✅ Тестовый ответ от сервера',
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

def main():
    print("🚀 Запуск тестового сервера...")
    print("🌐 Адрес: http://localhost:8080")
    print("🛑 Для остановки нажми Ctrl+C")
    
    try:
        server = HTTPServer(('localhost', 8080), TestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Сервер остановлен")

if __name__ == "__main__":
    main() 