import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Тестовые модели OpenRouter
TEST_MODELS = {
    "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    "Llama 3.1 8B": "meta-llama/llama-3.1-8b-instruct",
    "Gemini Pro": "google/gemini-pro",
    "Mistral 7B": "mistralai/mistral-7b-instruct",
}

async def test_openrouter_model(model_name: str, model_id: str, test_prompt: str):
    """Тестирует конкретную модель OpenRouter"""
    print(f"\n🧪 Тестирование модели: {model_name}")
    print(f"ID модели: {model_id}")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/notion-telegram-llm",
        "X-Title": "Notion-Telegram-LLM Integration"
    }
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко и по делу."},
            {"role": "user", "content": test_prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Получаем информацию о стоимости
            usage = result.get("usage", {})
            cost_info = ""
            if "total_tokens" in usage:
                cost_info = f" (токенов: {usage['total_tokens']})"
            
            print(f"✅ Ответ: {content}")
            print(f"📊 Статистика: {cost_info}")
            
            return True, content, usage
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False, str(e), {}

async def test_all_models():
    """Тестирует все доступные модели"""
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY не найден в .env")
        return
    
    print("🚀 Тестирование OpenRouter API")
    print("=" * 50)
    
    test_prompt = "Привет! Как дела? Расскажи кратко о себе."
    
    results = {}
    
    for model_name, model_id in TEST_MODELS.items():
        success, response, usage = await test_openrouter_model(model_name, model_id, test_prompt)
        results[model_name] = {
            "success": success,
            "response": response,
            "usage": usage
        }
        
        # Небольшая пауза между запросами
        await asyncio.sleep(1)
    
    # Выводим итоговую статистику
    print("\n" + "=" * 50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 50)
    
    successful_models = 0
    total_tokens = 0
    
    for model_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        tokens = result["usage"].get("total_tokens", 0)
        total_tokens += tokens
        
        if result["success"]:
            successful_models += 1
        
        print(f"{status} {model_name}: {tokens} токенов")
    
    print(f"\n🎯 Успешно протестировано: {successful_models}/{len(TEST_MODELS)} моделей")
    print(f"📈 Общее количество токенов: {total_tokens}")
    
    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("- GPT-3.5 Turbo: для общих задач (быстро и дёшево)")
    print("- Claude 3.5 Sonnet: для сложных аналитических задач")
    print("- Llama 3.1: для быстрых ответов")
    print("- Gemini Pro: для креативных задач")
    print("- Mistral 7B: для баланса качества и скорости")

async def test_cost_optimization():
    """Тестирует оптимизацию стоимости"""
    print("\n💰 ТЕСТИРОВАНИЕ ОПТИМИЗАЦИИ СТОИМОСТИ")
    print("=" * 50)
    
    # Тестируем разные настройки для одной модели
    model_id = "openai/gpt-3.5-turbo"
    
    test_configs = [
        {"max_tokens": 50, "temperature": 0.3, "name": "Краткий ответ"},
        {"max_tokens": 100, "temperature": 0.7, "name": "Стандартный ответ"},
        {"max_tokens": 200, "temperature": 1.0, "name": "Развёрнутый ответ"},
    ]
    
    test_prompt = "Объясни, что такое API, в одном предложении."
    
    for config in test_configs:
        print(f"\n🧪 {config['name']}")
        print(f"Настройки: max_tokens={config['max_tokens']}, temperature={config['temperature']}")
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/notion-telegram-llm",
            "X-Title": "Notion-Telegram-LLM Integration"
        }
        
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": "Отвечай кратко и по делу."},
                {"role": "user", "content": test_prompt}
            ],
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                print(f"✅ Ответ: {content}")
                print(f"📊 Токенов: {usage.get('total_tokens', 0)}")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")

async def main():
    """Главная функция"""
    await test_all_models()
    await test_cost_optimization()

if __name__ == "__main__":
    asyncio.run(main()) 