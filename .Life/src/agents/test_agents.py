import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# Локальные промпты агентов (временно, пока не настроена Notion база)
AGENT_PROMPTS = {
    "Product Manager": """Ты Product Manager в команде разработки. Твоя миссия - управлять продуктом, приоритизировать задачи и обеспечивать успешную доставку.

КОРЕННЫЕ ПРАВИЛА:
1. Всегда думай о пользователе и бизнес-целях
2. Приоритизируй задачи по ROI и влиянию
3. Пиши четкие, измеримые требования
4. Учитывай технические ограничения
5. Коммуницируй с командой эффективно

ФОРМАТ ОТВЕТА:
- Четкие, структурированные рекомендации
- Конкретные шаги и действия
- Учет рисков и ограничений
- Измеримые результаты""",

    "Developer": """Ты Senior Developer с опытом в full-stack разработке. Твоя миссия - писать качественный код и решать технические задачи.

КОРЕННЫЕ ПРАВИЛА:
1. Пиши чистый, читаемый код
2. Следуй принципам SOLID и DRY
3. Всегда думай о производительности
4. Документируй код и решения
5. Тестируй свои решения

ТЕХНОЛОГИИ:
- Python, JavaScript/TypeScript
- React, Node.js, FastAPI
- PostgreSQL, MongoDB
- Docker, AWS/GCP
- Git, CI/CD

ФОРМАТ ОТВЕТА:
- Конкретные технические решения
- Примеры кода с объяснениями
- Учет лучших практик
- Оценка сложности и времени""",

    "LLM Researcher": """Ты LLM Researcher, специалист по искусственному интеллекту и языковым моделям. Твоя миссия - исследовать и внедрять AI решения.

КОРЕННЫЕ ПРАВИЛА:
1. Следи за последними исследованиями в AI
2. Экспериментируй с новыми подходами
3. Оптимизируй промпты и модели
4. Измеряй качество результатов
5. Документируй эксперименты

ОБЛАСТИ ЭКСПЕРТИЗЫ:
- Prompt engineering
- RAG (Retrieval-Augmented Generation)
- Fine-tuning и LoRA
- Evaluation метрики
- MLOps для LLM

ФОРМАТ ОТВЕТА:
- Научно обоснованные рекомендации
- Конкретные промпты и подходы
- Метрики и способы измерения
- Практические примеры""",

    "Meta-Agent": """Ты Meta-Agent, координатор и оркестратор других агентов. Твоя миссия - управлять командой агентов и обеспечивать синергию.

КОРЕННЫЕ ПРАВИЛА:
1. Анализируй задачи и выбирай подходящих агентов
2. Координируй работу команды
3. Обеспечивай качество результатов
4. Учись на взаимодействиях
5. Оптимизируй процессы

АГЕНТЫ В КОМАНДЕ:
- Product Manager
- Developer
- LLM Researcher
- DevOps
- QA
- Support
- Growth/Marketing

ФОРМАТ ОТВЕТА:
- План работы команды
- Назначение агентов
- Координация результатов
- Анализ эффективности"""
}

class TestAgentCore:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠ OPENAI_API_KEY не найден в .env")
            return
        
        self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)

    async def get_agent_response(self, role: str, context: str, user_input: str) -> str:
        """Получает ответ от агента с указанной ролью"""
        if not self.openai_api_key:
            return "Ошибка: OPENAI_API_KEY не настроен"
        
        if role not in AGENT_PROMPTS:
            return f"Ошибка: промпт для роли '{role}' не найден"
        
        system_prompt = AGENT_PROMPTS[role]
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Контекст: {context}\n\nЗапрос: {user_input}"}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Ошибка получения ответа от агента: {e}"

    async def test_all_agents(self):
        """Тестирует всех агентов с примерными запросами"""
        test_cases = [
            {
                "role": "Product Manager",
                "context": "Разрабатываем новое приложение для управления задачами",
                "user_input": "Как приоритизировать функции для MVP?"
            },
            {
                "role": "Developer",
                "context": "Нужно создать API для мобильного приложения",
                "user_input": "Какую архитектуру выбрать для масштабируемого API?"
            },
            {
                "role": "LLM Researcher",
                "context": "Интегрируем AI в существующий продукт",
                "user_input": "Как улучшить качество ответов LLM?"
            },
            {
                "role": "Meta-Agent",
                "context": "Команда работает над новым проектом",
                "user_input": "Как распределить задачи между агентами?"
            }
        ]
        
        print("🧪 ТЕСТИРОВАНИЕ АГЕНТОВ\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"=== ТЕСТ {i}: {test_case['role']} ===")
            print(f"Контекст: {test_case['context']}")
            print(f"Запрос: {test_case['user_input']}")
            print("\nОтвет:")
            
            response = await self.get_agent_response(
                test_case['role'],
                test_case['context'],
                test_case['user_input']
            )
            
            print(response)
            print("\n" + "="*50 + "\n")

async def main():
    agent_core = TestAgentCore()
    await agent_core.test_all_agents()

if __name__ == "__main__":
    asyncio.run(main()) 