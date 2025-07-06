#!/usr/bin/env python3
"""
DeepSeek LLM System 2025 - Трехуровневая система на DeepSeek моделях
Оптимизированная для массовой обработки с минимальными затратами
"""

import os
import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import uuid

# Импортируем мониторинг затрат
from cost_monitor_deepseek import track_cost, cost_monitor

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Типы задач для автоматического распределения по уровням"""
    FILTER = "filter"           # Фильтрация записей
    MARKUP = "markup"           # Простая разметка
    SCORE = "score"             # Оценка важности
    CODE = "code"               # Генерация кода
    ANALYZE = "analyze"         # Анализ данных
    REASONING = "reasoning"     # Сложные рассуждения
    COMPLEX = "complex"         # Комплексные задачи

@dataclass
class ModelConfig:
    """Конфигурация модели"""
    name: str
    api_name: str
    input_price: float      # За 1K токенов
    output_price: float     # За 1K токенов
    discount_input: float   # Скидочная цена (UTC 16:30-00:30)
    discount_output: float  # Скидочная цена
    max_tokens: int
    context_length: int
    description: str

@dataclass
class ProcessingStats:
    """Статистика обработки"""
    requests_count: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    tier1_requests: int = 0
    tier2_requests: int = 0
    tier3_requests: int = 0
    errors_count: int = 0
    start_time: datetime = None

class DeepSeekSystem:
    """Трехуровневая система на DeepSeek моделях"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY не найден в переменных окружения")
        
        self.base_url = "https://hubai.loe.gg/v1/chat/completions"
        self.stats = ProcessingStats(start_time=datetime.now())
        
        # Конфигурация моделей DeepSeek
        self.models = {
            "tier1": ModelConfig(
                name="DeepSeek Chat (Фильтрация)",
                api_name="deepseek-chat",
                input_price=0.27,      # $0.27/1M стандартная цена
                output_price=1.10,     # $1.10/1M стандартная цена
                discount_input=0.135,  # $0.135/1M скидочная цена (50% OFF)
                discount_output=0.55,  # $0.55/1M скидочная цена (50% OFF)
                max_tokens=4000,
                context_length=64000,
                description="Простая фильтрация и разметка"
            ),
            "tier2": ModelConfig(
                name="DeepSeek Chat (Кодинг)",
                api_name="deepseek-chat",
                input_price=0.27,
                output_price=1.10,
                discount_input=0.135,
                discount_output=0.55,
                max_tokens=8000,
                context_length=64000,
                description="Генерация кода и анализ данных"
            ),
            "tier3": ModelConfig(
                name="DeepSeek R1 (Рассуждения)",
                api_name="deepseek-reasoner",
                input_price=0.55,      # $0.55/1M стандартная цена
                output_price=2.19,     # $2.19/1M стандартная цена
                discount_input=0.135,  # $0.135/1M скидочная цена (75% OFF)
                discount_output=0.55,  # $0.55/1M скидочная цена (75% OFF)
                max_tokens=32000,
                context_length=64000,
                description="Сложные рассуждения и анализ"
            )
        }
        
        # Маппинг типов задач на уровни
        self.task_routing = {
            TaskType.FILTER: "tier1",
            TaskType.MARKUP: "tier1", 
            TaskType.SCORE: "tier1",
            TaskType.CODE: "tier2",
            TaskType.ANALYZE: "tier2",
            TaskType.REASONING: "tier3",
            TaskType.COMPLEX: "tier3"
        }
    
    def is_discount_time(self) -> bool:
        """Проверка скидочного времени (UTC 16:30-00:30)"""
        from datetime import datetime, timezone
        now_utc = datetime.now(timezone.utc)
        hour = now_utc.hour
        minute = now_utc.minute
        
        # Скидочное время: 16:30-00:30 UTC
        if hour > 16 or (hour == 16 and minute >= 30):
            return True
        if hour < 0 or (hour == 0 and minute < 30):
            return True
        return False
    
    def get_model_price(self, tier: str, input_tokens: int, output_tokens: int) -> float:
        """Расчет стоимости запроса с учетом скидочного времени"""
        model = self.models[tier]
        is_discount = self.is_discount_time()
        
        if is_discount:
            input_price = model.discount_input
            output_price = model.discount_output
        else:
            input_price = model.input_price
            output_price = model.output_price
        
        # Цены указаны за 1M токенов, переводим в цену за токен
        cost = (input_tokens * input_price / 1000000) + (output_tokens * output_price / 1000000)
        return cost
    
    async def make_request(self, tier: str, messages: List[Dict], max_tokens: int = None) -> Tuple[str, int, int, float]:
        """Выполнение запроса к DeepSeek API"""
        model = self.models[tier]
        
        if max_tokens is None:
            max_tokens = model.max_tokens
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model.api_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        # Генерируем уникальный ID запроса
        request_id = str(uuid.uuid4())
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        content = data["choices"][0]["message"]["content"]
                        usage = data["usage"]
                        input_tokens = usage["prompt_tokens"]
                        output_tokens = usage["completion_tokens"]
                        
                        cost = self.get_model_price(tier, input_tokens, output_tokens)
                        
                        # Отслеживаем затраты
                        track_cost(
                            model=model.api_name,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            cost=cost,
                            request_id=request_id,
                            success=True
                        )
                        
                        # Обновляем статистику
                        self.stats.requests_count += 1
                        self.stats.total_input_tokens += input_tokens
                        self.stats.total_output_tokens += output_tokens
                        self.stats.total_cost += cost
                        
                        if tier == "tier1":
                            self.stats.tier1_requests += 1
                        elif tier == "tier2":
                            self.stats.tier2_requests += 1
                        elif tier == "tier3":
                            self.stats.tier3_requests += 1
                        
                        return content, input_tokens, output_tokens, cost
                    else:
                        error_text = await response.text()
                        logger.error(f"API Error {response.status}: {error_text}")
                        self.stats.errors_count += 1
                        
                        # Отслеживаем неудачный запрос
                        track_cost(
                            model=model.api_name,
                            input_tokens=0,
                            output_tokens=0,
                            cost=0.0,
                            request_id=request_id,
                            success=False,
                            error=f"HTTP {response.status}: {error_text}"
                        )
                        
                        raise Exception(f"API Error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"Request failed: {e}")
            self.stats.errors_count += 1
            
            # Отслеживаем ошибку подключения
            track_cost(
                model=model.api_name,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                request_id=request_id,
                success=False,
                error=str(e)
            )
            
            raise
    
    async def process_task(self, task_type: TaskType, content: str, additional_context: str = "") -> Dict[str, Any]:
        """Обработка задачи с автоматическим выбором уровня"""
        tier = self.task_routing[task_type]
        
        # Специализированные промпты для разных типов задач
        prompts = {
            TaskType.FILTER: self._get_filter_prompt(),
            TaskType.MARKUP: self._get_markup_prompt(),
            TaskType.SCORE: self._get_score_prompt(),
            TaskType.CODE: self._get_code_prompt(),
            TaskType.ANALYZE: self._get_analyze_prompt(),
            TaskType.REASONING: self._get_reasoning_prompt(),
            TaskType.COMPLEX: self._get_complex_prompt()
        }
        
        system_prompt = prompts[task_type]
        user_content = f"{content}\n\n{additional_context}".strip()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        try:
            result, input_tokens, output_tokens, cost = await self.make_request(tier, messages)
            
            return {
                "success": True,
                "result": result,
                "tier": tier,
                "model": self.models[tier].name,
                "task_type": task_type.value,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "is_discount": self.is_discount_time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tier": tier,
                "task_type": task_type.value
            }
    
    def _get_filter_prompt(self) -> str:
        return """Ты эксперт по фильтрации контента. Твоя задача - быстро определить релевантность и важность записи.

Отвечай ТОЛЬКО в формате JSON:
{
    "relevant": true/false,
    "importance": 1-10,
    "category": "категория",
    "reason": "краткое обоснование"
}"""
    
    def _get_markup_prompt(self) -> str:
        return """Ты эксперт по разметке контента. Создавай краткие, точные метаданные.

Отвечай ТОЛЬКО в формате JSON:
{
    "title": "краткое название",
    "description": "описание в 1-2 предложения", 
    "tags": ["тег1", "тег2", "тег3"],
    "type": "тип контента"
}"""
    
    def _get_score_prompt(self) -> str:
        return """Ты эксперт по оценке важности контента. Оценивай объективно и быстро.

Критерии оценки:
- Уникальность информации
- Практическая ценность
- Актуальность
- Потенциал для развития

Отвечай ТОЛЬКО в формате JSON:
{
    "score": 1-10,
    "reasoning": "краткое обоснование оценки",
    "priority": "low/medium/high"
}"""
    
    def _get_code_prompt(self) -> str:
        return """Ты опытный программист. Пиши чистый, эффективный код с комментариями.

Требования:
- Следуй лучшим практикам
- Добавляй необходимые комментарии
- Обрабатывай ошибки
- Оптимизируй производительность

Отвечай кодом и краткими пояснениями."""
    
    def _get_analyze_prompt(self) -> str:
        return """Ты аналитик данных. Проводи глубокий анализ с практическими выводами.

Структура анализа:
1. Ключевые находки
2. Паттерны и тренды  
3. Практические рекомендации
4. Риски и возможности

Будь конкретным и actionable."""
    
    def _get_reasoning_prompt(self) -> str:
        return """Ты эксперт по сложным рассуждениям. Используй цепочку логических выводов.

Подход:
1. Разбей проблему на части
2. Проанализируй каждую часть
3. Найди связи и закономерности
4. Сделай обоснованные выводы
5. Предложи решения

Думай пошагово и обосновывай каждый вывод."""
    
    def _get_complex_prompt(self) -> str:
        return """Ты эксперт по комплексным задачам. Используй все доступные возможности рассуждений.

Методология:
1. Системный анализ проблемы
2. Многофакторное рассмотрение
3. Креативное решение проблем
4. Прогнозирование последствий
5. Оптимальная стратегия

Предоставь полное, структурированное решение."""
    
    # Удобные методы для основных задач
    async def filter_records(self, records: List[str]) -> List[Dict]:
        """Фильтрация списка записей"""
        results = []
        for record in records:
            result = await self.process_task(TaskType.FILTER, record)
            results.append(result)
        return results
    
    async def score_importance(self, contents: List[str]) -> List[Dict]:
        """Оценка важности контента"""
        results = []
        for content in contents:
            result = await self.process_task(TaskType.SCORE, content)
            results.append(result)
        return results
    
    async def generate_code(self, requirements: str) -> Dict:
        """Генерация кода по требованиям"""
        return await self.process_task(TaskType.CODE, requirements)
    
    async def analyze_content(self, content: str, context: str = "") -> Dict:
        """Анализ контента"""
        return await self.process_task(TaskType.ANALYZE, content, context)
    
    async def complex_reasoning(self, problem: str, context: str = "") -> Dict:
        """Сложные рассуждения"""
        return await self.process_task(TaskType.REASONING, problem, context)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики работы"""
        runtime = datetime.now() - self.stats.start_time
        
        return {
            "runtime_minutes": runtime.total_seconds() / 60,
            "total_requests": self.stats.requests_count,
            "successful_requests": self.stats.requests_count - self.stats.errors_count,
            "error_rate": self.stats.errors_count / max(1, self.stats.requests_count) * 100,
            "tier_distribution": {
                "tier1": self.stats.tier1_requests,
                "tier2": self.stats.tier2_requests, 
                "tier3": self.stats.tier3_requests
            },
            "token_usage": {
                "input_tokens": self.stats.total_input_tokens,
                "output_tokens": self.stats.total_output_tokens,
                "total_tokens": self.stats.total_input_tokens + self.stats.total_output_tokens
            },
            "cost_analysis": {
                "total_cost": round(self.stats.total_cost, 4),
                "average_cost_per_request": round(self.stats.total_cost / max(1, self.stats.requests_count), 4),
                "cost_per_1k_tokens": round(self.stats.total_cost / max(1, (self.stats.total_input_tokens + self.stats.total_output_tokens) / 1000), 4)
            },
            "discount_active": self.is_discount_time()
        }
    
    def print_stats(self):
        """Вывод статистики в консоль"""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("📊 СТАТИСТИКА DEEPSEEK СИСТЕМЫ 2025")
        print("="*60)
        
        print(f"⏱️  Время работы: {stats['runtime_minutes']:.1f} минут")
        print(f"📝 Всего запросов: {stats['total_requests']}")
        print(f"✅ Успешных: {stats['successful_requests']}")
        print(f"❌ Ошибок: {stats['error_rate']:.1f}%")
        
        print(f"\n🎯 Распределение по уровням:")
        print(f"   Tier 1 (Фильтрация): {stats['tier_distribution']['tier1']}")
        print(f"   Tier 2 (Кодинг): {stats['tier_distribution']['tier2']}")
        print(f"   Tier 3 (Рассуждения): {stats['tier_distribution']['tier3']}")
        
        print(f"\n🔤 Использование токенов:")
        print(f"   Входящие: {stats['token_usage']['input_tokens']:,}")
        print(f"   Исходящие: {stats['token_usage']['output_tokens']:,}")
        print(f"   Всего: {stats['token_usage']['total_tokens']:,}")
        
        print(f"\n💰 Стоимость:")
        print(f"   Общая стоимость: ${stats['cost_analysis']['total_cost']}")
        print(f"   Средняя за запрос: ${stats['cost_analysis']['average_cost_per_request']}")
        print(f"   За 1K токенов: ${stats['cost_analysis']['cost_per_1k_tokens']}")
        print(f"   Скидка активна: {'✅ Да' if stats['discount_active'] else '❌ Нет'}")
        
        # Сравнение с альтернативами
        gpt4_cost = stats['token_usage']['total_tokens'] * 0.03 / 1000
        savings = ((gpt4_cost - stats['cost_analysis']['total_cost']) / gpt4_cost * 100) if gpt4_cost > 0 else 0
        
        print(f"\n💡 Сравнение с GPT-4:")
        print(f"   GPT-4 стоимость: ${gpt4_cost:.4f}")
        print(f"   Экономия: {savings:.1f}%")
        
        # Сводка затрат из монитора
        print(f"\n" + "="*60)
        cost_monitor.print_summary()
        
        # ASCII график дневных затрат
        print(f"\n📊 Дневные затраты: {cost_monitor.get_daily_chart()}")
        
        print("="*60)

# Пример использования и тестирование
async def main():
    """Демонстрация работы системы"""
    print("🚀 Инициализация DeepSeek System 2025...")
    
    # Инициализация (требуется DEEPSEEK_API_KEY в .env)
    try:
        ds = DeepSeekSystem()
        print("✅ Система инициализирована успешно")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        print("💡 Убедитесь, что DEEPSEEK_API_KEY указан в переменных окружения")
        return
    
    print(f"\n⏰ Скидочное время активно: {'✅ Да' if ds.is_discount_time() else '❌ Нет'}")
    
    # Тестовые данные
    test_records = [
        "Идея для стартапа: приложение для заказа еды с ИИ-рекомендациями",
        "Заметка о погоде: сегодня дождь, взял зонт",
        "Важная встреча с инвестором завтра в 15:00"
    ]
    
    print("\n" + "="*50)
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("="*50)
    
    # Тест 1: Фильтрация записей
    print("\n1️⃣ Тестирование фильтрации записей...")
    try:
        filter_results = await ds.filter_records(test_records)
        for i, result in enumerate(filter_results):
            if result['success']:
                print(f"   ✅ Запись {i+1}: {result['tier']} - ${result['cost']:.4f}")
            else:
                print(f"   ❌ Запись {i+1}: {result['error']}")
    except Exception as e:
        print(f"   ❌ Ошибка фильтрации: {e}")
    
    # Тест 2: Генерация кода
    print("\n2️⃣ Тестирование генерации кода...")
    try:
        code_result = await ds.generate_code("Создай функцию для сортировки списка словарей по ключу")
        if code_result['success']:
            print(f"   ✅ Код сгенерирован: {code_result['tier']} - ${code_result['cost']:.4f}")
        else:
            print(f"   ❌ Ошибка генерации: {code_result['error']}")
    except Exception as e:
        print(f"   ❌ Ошибка генерации кода: {e}")
    
    # Тест 3: Сложные рассуждения
    print("\n3️⃣ Тестирование сложных рассуждений...")
    try:
        reasoning_result = await ds.complex_reasoning(
            "Как оптимизировать процесс массового импорта 2500+ записей в Notion?",
            "Контекст: есть система на Python, ограничения API, нужна высокая скорость"
        )
        if reasoning_result['success']:
            print(f"   ✅ Анализ выполнен: {reasoning_result['tier']} - ${reasoning_result['cost']:.4f}")
        else:
            print(f"   ❌ Ошибка анализа: {reasoning_result['error']}")
    except Exception as e:
        print(f"   ❌ Ошибка рассуждений: {e}")
    
    # Показ статистики
    ds.print_stats()
    
    print("\n🎯 Система готова к массовой обработке!")
    print("💡 Для обработки 2528 записей потребуется примерно $1-5")

if __name__ == "__main__":
    asyncio.run(main())