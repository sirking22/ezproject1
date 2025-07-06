import http.server
import socketserver
import json
import time
from urllib.parse import urlparse, parse_qs

class SimpleLLMHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "server": "Ultra Simple LLM Server",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')
    
    def do_POST(self):
        if self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                prompt = data.get('prompt', '')
                context = data.get('context', 'home')
                
                # Mock response
                response_text = f"Обработал запрос: {prompt} (контекст: {context})"
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "response": response_text,
                    "context": context,
                    "timestamp": time.time()
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif self.path == '/analyze_biometrics':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                heart_rate = data.get('heart_rate', 70)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "analysis": f"Пульс: {heart_rate}",
                    "recommendation": "Все в порядке!",
                    "health_score": 85
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    PORT = 8000
    
    print("🚀 Запуск Ultra Simple LLM Server...")
    print(f"📍 Сервер доступен на: http://localhost:{PORT}")
    print("🔗 Health check: http://localhost:8000/health")
    print("📱 Готов к подключению приложений!")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    with socketserver.TCPServer(("", PORT), SimpleLLMHandler) as httpd:
        print(f"✅ Сервер запущен на порту {PORT}")
        httpd.serve_forever() 