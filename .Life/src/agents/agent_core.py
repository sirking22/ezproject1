import os
import asyncio
import json
import time
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from notion_client import AsyncClient
import httpx

# Импортируем мониторинг
try:
    from src.utils.performance_monitor import performance_monitor, cache_manager
except ImportError:
    # Fallback если мониторинг недоступен
    performance_monitor = None
    cache_manager = None

load_dotenv()

class AgentCore:
    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.notion_client = AsyncClient(auth=self.notion_token)
        
        # Notion базы
        self.dbs = {
            "rituals": os.getenv("NOTION_DATABASE_ID_RITUALS"),
            "habits": os.getenv("NOTION_DATABASE_ID_HABITS"),
            "reflection": os.getenv("NOTION_DATABASE_ID_REFLECTION"),
            "guides": os.getenv("NOTION_DATABASE_ID_GUIDES"),
            "actions": os.getenv("NOTION_DATABASE_ID_ACTIONS"),
            "terms": os.getenv("NOTION_DATABASE_ID_TERMS"),
            "materials": os.getenv("NOTION_DATABASE_ID_MATERIALS"),
            "agent_prompts": os.getenv("NOTION_DATABASE_ID_AGENT_PROMPTS"),
        }
        
        # Поля для каждой базы
        self.db_fields = {
            "rituals": ("Название", "Категория"),
            "habits": ("Привычка", None),
            "reflection": ("Дата", "Тип"),
            "guides": ("Name", None),
            "actions": ("Задача", "Категория"),
            "terms": ("Термин", "Категория"),
            "materials": ("Название", "Категория"),
            "agent_prompts": ("Name", "Роль"),
        }
        
        # Кэш промптов
        self.prompts_cache = {}
        self.last_prompts_update = None
        
        # Модели для разных типов задач
        self.models = {
            "default": "openai/gpt-3.5-turbo",  # Бесплатная модель
            "advanced": "anthropic/claude-3.5-sonnet",  # Продвинутая
            "fast": "meta-llama/llama-3.1-8b-instruct",  # Быстрая
            "creative": "google/gemini-pro",  # Креативная
            "coding": "meta-llama/codellama-34b-instruct",  # Для кода
        }

    def _generate_cache_key(self, role: str, context: str, user_input: str, model_type: str) -> str:
        """Генерирует ключ кэша для запроса"""
        content = f"{role}:{context}:{user_input}:{model_type}"
        return hashlib.md5(content.encode()).hexdigest()

    async def load_prompts_from_notion(self, force_refresh: bool = False) -> Dict[str, str]:
        """Загружает промпты агентов из Notion базы с кэшированием"""
        cache_key = "notion_prompts"
        
        # Проверяем кэш
        if cache_manager and not force_refresh:
            cached_prompts = cache_manager.get(cache_key)
            if cached_prompts:
                if performance_monitor:
                    performance_monitor.cache_hits += 1
                return cached_prompts
        
        if performance_monitor:
            performance_monitor.cache_misses += 1
        
        try:
            response = await self.notion_client.databases.query(
                database_id=self.dbs["agent_prompts"]
            )
            
            prompts = {}
            for page in response["results"]:
                props = page["properties"]
                role = props.get("Роль", {}).get("select", {}).get("name", "unknown")
                name = props.get("Name", {}).get("title", [{}])[0].get("plain_text", "")
                prompt_text = props.get("Промпт", {}).get("rich_text", [{}])[0].get("plain_text", "")
                
                if role and prompt_text:
                    prompts[role] = prompt_text
            
            self.prompts_cache = prompts
            self.last_prompts_update = datetime.now()
            
            # Сохраняем в кэш
            if cache_manager:
                cache_manager.set(cache_key, prompts)
            
            print(f"Загружено {len(prompts)} промптов агентов")
            return prompts
            
        except Exception as e:
            print(f"Ошибка загрузки промптов: {e}")
            return {}

    async def get_agent_response(self, role: str, context: str, user_input: str, model_type: str = "default") -> str:
        """Получает ответ от агента с мониторингом и кэшированием"""
        start_time = time.time()
        cache_key = self._generate_cache_key(role, context, user_input, model_type)
        
        # Проверяем кэш ответов
        if cache_manager:
            cached_response = cache_manager.get(cache_key)
            if cached_response:
                if performance_monitor:
                    performance_monitor.cache_hits += 1
                    performance_monitor.add_metric(
                        operation="agent_response_cached",
                        duration=time.time() - start_time,
                        model_used="cached",
                        tokens_used=0,
                        cost=0.0,
                        success=True
                    )
                return cached_response
        
        if performance_monitor:
            performance_monitor.cache_misses += 1
        
        prompts = await self.load_prompts_from_notion()
        
        if role not in prompts:
            error_msg = f"Ошибка: промпт для роли '{role}' не найден"
            if performance_monitor:
                performance_monitor.add_metric(
                    operation="agent_response",
                    duration=time.time() - start_time,
                    model_used="unknown",
                    tokens_used=0,
                    cost=0.0,
                    success=False,
                    error=error_msg
                )
            return error_msg
        
        system_prompt = prompts[role]
        
        # Выбираем модель в зависимости от типа задачи
        model = self.models.get(model_type, self.models["default"])
        
        try:
            # Используем OpenRouter API
            if self.openrouter_api_key:
                response = await self._call_openrouter_api(system_prompt, context, user_input, model)
            # Fallback на OpenAI
            elif self.openai_api_key:
                response = await self._call_openai_api(system_prompt, context, user_input)
            else:
                response = "Ошибка: не настроены API ключи для LLM"
            
            duration = time.time() - start_time
            
            # Сохраняем в кэш
            if cache_manager and response and not response.startswith("Ошибка"):
                cache_manager.set(cache_key, response)
            
            # Логируем метрику
            if performance_monitor:
                # Примерная оценка токенов и стоимости
                estimated_tokens = len(response.split()) * 1.3  # Примерная оценка
                estimated_cost = estimated_tokens * 0.000002  # Примерная стоимость для GPT-3.5
                
                performance_monitor.add_metric(
                    operation="agent_response",
                    duration=duration,
                    model_used=model,
                    tokens_used=int(estimated_tokens),
                    cost=estimated_cost,
                    success=not response.startswith("Ошибка")
                )
            
            return response
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Ошибка получения ответа от агента: {e}"
            
            if performance_monitor:
                performance_monitor.add_metric(
                    operation="agent_response",
                    duration=duration,
                    model_used=model,
                    tokens_used=0,
                    cost=0.0,
                    success=False,
                    error=str(e)
                )
            
            return error_msg

    async def _call_openrouter_api(self, system_prompt: str, context: str, user_input: str, model: str) -> str:
        """Вызывает OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/notion-telegram-llm",
            "X-Title": "Notion-Telegram-LLM Integration"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Контекст: {context}\n\nЗапрос: {user_input}"}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _call_openai_api(self, system_prompt: str, context: str, user_input: str) -> str:
        """Вызывает OpenAI API (fallback)"""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.openai_api_key)
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Контекст: {context}\n\nЗапрос: {user_input}"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content

    async def get_optimal_model_for_task(self, role: str, task_complexity: str = "medium") -> str:
        """Выбирает оптимальную модель для задачи"""
        model_mapping = {
            "Product Manager": "advanced" if task_complexity == "high" else "default",
            "Developer": "coding" if "code" in task_complexity else "advanced",
            "LLM Researcher": "advanced",
            "DevOps": "default",
            "QA": "default",
            "Support": "fast",
            "Growth/Marketing": "creative",
            "Meta-Agent": "advanced"
        }
        
        return model_mapping.get(role, "default")

    async def create_notion_record(self, db_name: str, title: str, category: str = None, 
                                 additional_props: Dict = None) -> bool:
        """Создаёт запись в указанной Notion базе"""
        try:
            db_id = self.dbs[db_name]
            title_field = self.db_fields[db_name][0]
            category_field = self.db_fields[db_name][1]
            
            properties = {
                title_field: {"title": [{"text": {"content": title}}]}
            }
            
            if category_field and category:
                properties[category_field] = {"select": {"name": category}}
            
            if additional_props:
                properties.update(additional_props)
            
            await self.notion_client.pages.create(
                parent={"database_id": db_id},
                properties=properties
            )
            
            return True
            
        except Exception as e:
            print(f"Ошибка создания записи в {db_name}: {e}")
            return False

    async def get_notion_records(self, db_name: str, filter_params: Dict = None) -> List[Dict]:
        """Получает записи из Notion базы с фильтрацией"""
        try:
            db_id = self.dbs[db_name]
            
            query_params = {"database_id": db_id}
            if filter_params:
                query_params["filter"] = filter_params
            
            response = await self.notion_client.databases.query(**query_params)
            return response["results"]
            
        except Exception as e:
            print(f"Ошибка получения записей из {db_name}: {e}")
            return []

    async def update_notion_record(self, page_id: str, properties: Dict) -> bool:
        """Обновляет запись в Notion"""
        try:
            await self.notion_client.pages.update(
                page_id=page_id,
                properties=properties
            )
            return True
            
        except Exception as e:
            print(f"Ошибка обновления записи: {e}")
            return False

    async def log_agent_interaction(self, role: str, user_input: str, response: str, 
                                  success: bool = True, model_used: str = None) -> None:
        """Логирует взаимодействие с агентом"""
        try:
            log_entry = {
                "Роль": {"select": {"name": role}},
                "Запрос": {"rich_text": [{"text": {"content": user_input[:100]}}]},
                "Ответ": {"rich_text": [{"text": {"content": response[:500]}}]},
                "Успех": {"checkbox": success},
                "Дата": {"date": {"start": datetime.now().isoformat()}},
                "Модель": {"rich_text": [{"text": {"content": model_used or "unknown"}}]} if model_used else {}
            }
            
            await self.create_notion_record("agent_prompts", f"Лог {role}", 
                                          additional_props=log_entry)
            
        except Exception as e:
            print(f"Ошибка логирования: {e}")

    async def get_performance_report(self) -> Dict[str, Any]:
        """Получает отчёт о производительности"""
        if performance_monitor:
            return performance_monitor.get_performance_stats()
        return {"error": "Мониторинг недоступен"}

    async def print_performance_report(self, days: int = 7):
        """Выводит отчёт о производительности"""
        if performance_monitor:
            performance_monitor.print_performance_report(days)
        else:
            print("❌ Мониторинг производительности недоступен")

# Глобальный экземпляр для использования в других модулях
agent_core = AgentCore()

# Пример использования
if __name__ == "__main__":
    asyncio.run(agent_core.process_all_tasks(limit=3)) 