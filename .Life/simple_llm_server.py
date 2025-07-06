from flask import Flask, request, jsonify
import json
import time

app = Flask(__name__)

# Mock LLM responses
def mock_llm_response(prompt, context="home"):
    responses = {
        "home": "Это домашний контекст. Я помогу с личными задачами.",
        "work": "Это рабочий контекст. Готов помочь с проектами.",
        "health": "Анализирую ваши биометрические данные. Рекомендую больше движения.",
        "voice": "Понял ваш голосовой запрос. Обрабатываю...",
        "default": "Привет! Я ваш персональный AI-ассистент."
    }
    
    # Simulate processing time
    time.sleep(0.5)
    
    if "здоровье" in prompt.lower() or "биометрия" in prompt.lower():
        return responses["health"]
    elif "работа" in prompt.lower() or "проект" in prompt.lower():
        return responses["work"]
    elif "голос" in prompt.lower() or "команда" in prompt.lower():
        return responses["voice"]
    else:
        return responses.get(context, responses["default"])

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "server": "Local LLM Server",
        "version": "1.0.0"
    })

@app.route('/generate', methods=['POST'])
def generate_text():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        context = data.get('context', 'home')
        
        response = mock_llm_response(prompt, context)
        
        return jsonify({
            "response": response,
            "context": context,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/analyze_biometrics', methods=['POST'])
def analyze_biometrics():
    try:
        data = request.get_json()
        heart_rate = data.get('heart_rate', 70)
        steps = data.get('steps', 0)
        sleep_hours = data.get('sleep_hours', 7)
        
        # Simple analysis
        if heart_rate > 100:
            recommendation = "Сердцебиение повышенное. Рекомендую отдых."
        elif steps < 5000:
            recommendation = "Мало шагов. Попробуйте прогуляться."
        elif sleep_hours < 7:
            recommendation = "Недостаточно сна. Старайтесь спать 7-8 часов."
        else:
            recommendation = "Отличные показатели! Продолжайте в том же духе."
        
        return jsonify({
            "analysis": f"Пульс: {heart_rate}, Шаги: {steps}, Сон: {sleep_hours}ч",
            "recommendation": recommendation,
            "health_score": min(100, (heart_rate/120*50 + steps/10000*30 + sleep_hours/8*20))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/voice_command', methods=['POST'])
def voice_command():
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        # Process voice commands
        if "задача" in command.lower():
            response = "Создаю новую задачу в Notion..."
        elif "привычка" in command.lower():
            response = "Отмечаю привычку в трекере..."
        elif "погода" in command.lower():
            response = "Проверяю погоду в вашем городе..."
        elif "здоровье" in command.lower():
            response = "Анализирую ваши биометрические данные..."
        else:
            response = f"Обрабатываю команду: {command}"
        
        return jsonify({
            "response": response,
            "command": command,
            "processed": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    print("🚀 Запуск Local LLM Server...")
    print("📍 Сервер доступен на: http://localhost:8000")
    print("🔗 Health check: http://localhost:8000/health")
    print("📱 Готов к подключению приложений!")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=8000, debug=True) 