import os
import asyncio
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class OpenRouterMonitor:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        
    async def get_usage_stats(self):
        """Получает статистику использования"""
        if not self.api_key:
            print("❌ OPENROUTER_API_KEY не найден")
            return None
            
        url = f"{self.base_url}/auth/key"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                return data
                
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return None
    
    async def get_model_pricing(self):
        """Получает информацию о ценах моделей"""
        url = f"{self.base_url}/models"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                return data.get("data", [])
                
        except Exception as e:
            print(f"❌ Ошибка получения цен: {e}")
            return []
    
    def format_usage_stats(self, stats):
        """Форматирует статистику использования"""
        if not stats:
            return "Статистика недоступна"
        
        print("\n📊 СТАТИСТИКА ИСПОЛЬЗОВАНИЯ OPENROUTER")
        print("=" * 50)
        
        # Основная информация
        if "data" in stats:
            data = stats["data"]
            
            print(f"🔑 Ключ: {data.get('name', 'Неизвестно')}")
            print(f"📅 Создан: {data.get('created_at', 'Неизвестно')}")
            print(f"💰 Баланс: ${data.get('credits', 0):.4f}")
            
            # Статистика по дням
            if "usage" in data:
                usage = data["usage"]
                print(f"\n📈 Использование за последние 7 дней:")
                
                # Проверяем, что usage это список
                if isinstance(usage, list):
                    for day_usage in usage:
                        date = day_usage.get("date", "Неизвестно")
                        tokens = day_usage.get("tokens", 0)
                        cost = day_usage.get("cost", 0)
                        
                        print(f"  {date}: {tokens:,} токенов (${cost:.4f})")
                else:
                    print(f"  Использование: {usage}")
        
        return stats
    
    def format_model_pricing(self, models):
        """Форматирует информацию о ценах моделей"""
        if not models:
            return "Цены недоступны"
        
        print("\n💰 ЦЕНЫ НА МОДЕЛИ")
        print("=" * 50)
        
        # Группируем модели по провайдерам
        providers = {}
        for model in models:
            provider = model.get("provider", {}).get("name", "Неизвестно")
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)
        
        for provider, provider_models in providers.items():
            print(f"\n🏢 {provider}:")
            
            for model in provider_models[:3]:  # Показываем первые 3 модели
                name = model.get("name", "Неизвестно")
                pricing = model.get("pricing", {})
                
                input_price = pricing.get("prompt", "N/A")
                output_price = pricing.get("completion", "N/A")
                
                print(f"  📝 {name}")
                print(f"    Ввод: ${input_price}/1K токенов")
                print(f"    Вывод: ${output_price}/1K токенов")
        
        return models
    
    async def estimate_cost(self, model_id: str, input_tokens: int, output_tokens: int):
        """Оценивает стоимость запроса"""
        models = await self.get_model_pricing()
        
        for model in models:
            if model.get("id") == model_id:
                pricing = model.get("pricing", {})
                input_price = float(pricing.get("prompt", 0))
                output_price = float(pricing.get("completion", 0))
                
                input_cost = (input_tokens / 1000) * input_price
                output_cost = (output_tokens / 1000) * output_price
                total_cost = input_cost + output_cost
                
                print(f"\n💰 ОЦЕНКА СТОИМОСТИ")
                print("=" * 30)
                print(f"Модель: {model_id}")
                print(f"Входные токены: {input_tokens:,}")
                print(f"Выходные токены: {output_tokens:,}")
                print(f"Стоимость ввода: ${input_cost:.6f}")
                print(f"Стоимость вывода: ${output_cost:.6f}")
                print(f"Общая стоимость: ${total_cost:.6f}")
                
                return total_cost
        
        print(f"❌ Модель {model_id} не найдена")
        return None
    
    async def get_recommendations(self):
        """Получает рекомендации по оптимизации"""
        stats = await self.get_usage_stats()
        models = await self.get_model_pricing()
        
        print("\n💡 РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ")
        print("=" * 50)
        
        # Анализируем использование
        if stats and "data" in stats:
            data = stats["data"]
            credits = data.get("credits", 0)
            
            if credits < 0.01:
                print("⚠️  Баланс критически низкий! Пополните счёт.")
            elif credits < 0.1:
                print("⚠️  Баланс заканчивается. Рассмотрите пополнение.")
            else:
                print(f"✅ Баланс в порядке: ${credits:.4f}")
        
        # Рекомендации по моделям
        print("\n🎯 РЕКОМЕНДАЦИИ ПО МОДЕЛЯМ:")
        print("- GPT-3.5 Turbo: для общих задач (быстро и дёшево)")
        print("- Claude 3.5 Sonnet: для сложных аналитических задач")
        print("- Llama 3.1: для быстрых ответов")
        print("- Mistral 7B: для баланса качества и скорости")
        
        print("\n💡 СОВЕТЫ ПО ЭКОНОМИИ:")
        print("- Используйте max_tokens для ограничения длины ответов")
        print("- Применяйте temperature=0.3 для более предсказуемых ответов")
        print("- Кэшируйте похожие запросы")
        print("- Используйте более дешёвые модели для простых задач")
    
    async def run_full_report(self):
        """Запускает полный отчёт"""
        print("🔍 ОТЧЁТ ПО OPENROUTER API")
        print("=" * 60)
        
        # Получаем статистику
        stats = await self.get_usage_stats()
        self.format_usage_stats(stats)
        
        # Получаем цены
        models = await self.get_model_pricing()
        self.format_model_pricing(models)
        
        # Рекомендации
        await self.get_recommendations()
        
        # Пример оценки стоимости
        print("\n" + "=" * 60)
        await self.estimate_cost("openai/gpt-3.5-turbo", 100, 200)

async def main():
    """Главная функция"""
    monitor = OpenRouterMonitor()
    await monitor.run_full_report()

if __name__ == "__main__":
    asyncio.run(main()) 