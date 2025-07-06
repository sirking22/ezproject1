#!/usr/bin/env python3
"""
Локальный LLM сервер для персональной AI-экосистемы
Использует Llama 70B квантованную для обработки запросов с контекстным переключением
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, UTC
from dataclasses import dataclass
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    logging.warning("llama-cpp-python не установлен. Используется заглушка.")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextType(Enum):
    WORK = "work"
    HOME = "home"
    GENERAL = "general"

class ModelType(Enum):
    FAST = "fast"      # Llama 7B для быстрых ответов
    DEFAULT = "default"  # Llama 70B для стандартных задач
    ADVANCED = "advanced"  # Llama 70B с расширенным контекстом

@dataclass
class ContextConfig:
    system_prompt: str
    max_tokens: int
    temperature: float
    top_p: float
    specializations: List[str]

class GenerateRequest(BaseModel):
    prompt: str
    context: ContextType = ContextType.HOME
    model_type: ModelType = ModelType.DEFAULT
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class GenerateResponse(BaseModel):
    response: str
    context_used: str
    model_used: str
    tokens_used: int
    processing_time: float
    confidence_score: float

class LocalLLMServer:
    """
    Локальный LLM сервер с контекстным переключением
    """
    
    def __init__(self):
        self.app = FastAPI(title="Personal AI Ecosystem LLM Server", version="1.0.0")
        self.models: Dict[ModelType, Any] = {}
        self.context_configs: Dict[ContextType, ContextConfig] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Инициализация
        self._setup_cors()
        self._setup_routes()
        self._init_context_configs()
        self._init_models()
        
        logger.info("Локальный LLM сервер инициализирован")

    def _setup_cors(self):
        """Настройка CORS"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Настройка маршрутов API"""
        
        @self.app.post("/generate", response_model=GenerateResponse)
        async def generate_text(request: GenerateRequest):
            return await self.generate_response(request)
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "models_loaded": len(self.models)}
        
        @self.app.get("/contexts")
        async def get_contexts():
            return {
                context.value: {
                    "system_prompt": config.system_prompt,
                    "specializations": config.specializations
                }
                for context, config in self.context_configs.items()
            }
        
        @self.app.post("/session/{session_id}/context")
        async def set_session_context(session_id: str, context: ContextType):
            if session_id not in self.sessions:
                self.sessions[session_id] = {}
            self.sessions[session_id]["context"] = context
            return {"session_id": session_id, "context": context.value}
        
        @self.app.get("/session/{session_id}")
        async def get_session_info(session_id: str):
            return self.sessions.get(session_id, {})

    def _init_context_configs(self):
        """Инициализация конфигураций контекстов"""
        
        self.context_configs = {
            ContextType.WORK: ContextConfig(
                system_prompt="""Ты персональный AI-ассистент для рабочих задач. Твоя специализация:
- Управление проектами и задачами
- Анализ данных и создание отчетов
- Оптимизация рабочих процессов
- Техническое планирование и архитектура
- Коммуникация с командой

Ты помогаешь пользователю быть более продуктивным и эффективным в работе. 
Отвечай профессионально, структурированно и с фокусом на результат.""",
                max_tokens=2048,
                temperature=0.7,
                top_p=0.9,
                specializations=["project_management", "data_analysis", "process_optimization", "technical_planning"]
            ),
            
            ContextType.HOME: ContextConfig(
                system_prompt="""Ты персональный AI-ассистент для личного развития и домашних задач. Твоя специализация:
- Управление привычками и ритуалами
- Личные рефлексии и самоанализ
- Планирование личных целей
- Творческие проекты и хобби
- Эмоциональное благополучие

Ты помогаешь пользователю развиваться как личность и поддерживать баланс в жизни.
Отвечай с эмпатией, поддерживай и вдохновляй.""",
                max_tokens=2048,
                temperature=0.8,
                top_p=0.9,
                specializations=["habit_tracking", "personal_reflection", "goal_planning", "creative_projects", "wellness"]
            ),
            
            ContextType.GENERAL: ContextConfig(
                system_prompt="""Ты универсальный AI-ассистент для общих задач. Твоя специализация:
- Общие вопросы и консультации
- Обучение и объяснение концепций
- Творческое письмо и генерация идей
- Анализ и синтез информации
- Помощь в принятии решений

Ты адаптируешься под потребности пользователя и помогаешь в различных областях.
Отвечай разносторонне, информативно и полезно.""",
                max_tokens=2048,
                temperature=0.7,
                top_p=0.9,
                specializations=["general_knowledge", "learning", "creative_writing", "analysis", "decision_making"]
            )
        }

    def _init_models(self):
        """Инициализация моделей"""
        if not LLAMA_AVAILABLE:
            logger.warning("Используется заглушка для LLM (llama-cpp-python не установлен)")
            self._init_mock_models()
            return
        
        try:
            # Инициализация моделей (пути нужно настроить под вашу систему)
            model_paths = {
                ModelType.FAST: "models/llama-2-7b-chat.Q4_K_M.gguf",
                ModelType.DEFAULT: "models/llama-2-70b-chat.Q4_K_M.gguf",
                ModelType.ADVANCED: "models/llama-2-70b-chat.Q4_K_M.gguf"
            }
            
            for model_type, path in model_paths.items():
                try:
                    self.models[model_type] = Llama(
                        model_path=path,
                        n_ctx=4096,
                        n_threads=8,
                        n_gpu_layers=0  # Настройте под вашу GPU
                    )
                    logger.info(f"Модель {model_type.value} загружена: {path}")
                except Exception as e:
                    logger.error(f"Ошибка загрузки модели {model_type.value}: {e}")
                    # Создаем заглушку
                    self.models[model_type] = self._create_mock_model(model_type)
                    
        except Exception as e:
            logger.error(f"Ошибка инициализации моделей: {e}")
            self._init_mock_models()

    def _init_mock_models(self):
        """Инициализация заглушек моделей для тестирования"""
        for model_type in ModelType:
            self.models[model_type] = self._create_mock_model(model_type)

    def _create_mock_model(self, model_type: ModelType):
        """Создает заглушку модели для тестирования"""
        class MockModel:
            def __init__(self, model_type):
                self.model_type = model_type
            
            def __call__(self, prompt, **kwargs):
                # Генерируем реалистичный ответ в зависимости от контекста
                if "рабочий" in prompt.lower() or "проект" in prompt.lower():
                    response = f"[MOCK {self.model_type.value}] Рабочий ответ: {prompt[:100]}..."
                elif "личный" in prompt.lower() or "привычка" in prompt.lower():
                    response = f"[MOCK {self.model_type.value}] Личный ответ: {prompt[:100]}..."
                else:
                    response = f"[MOCK {self.model_type.value}] Общий ответ: {prompt[:100]}..."
                
                return {"choices": [{"text": response}]}
        
        return MockModel(model_type)

    async def generate_response(self, request: GenerateRequest) -> GenerateResponse:
        """Генерирует ответ с учетом контекста"""
        start_time = datetime.now(UTC)
        
        try:
            # Получаем конфигурацию контекста
            context_config = self.context_configs[request.context]
            
            # Получаем модель
            model = self.models.get(request.model_type)
            if not model:
                raise HTTPException(status_code=400, detail=f"Модель {request.model_type.value} не найдена")
            
            # Формируем полный промпт
            full_prompt = self._build_prompt(request.prompt, context_config, request)
            
            # Генерируем ответ
            response_data = model(
                full_prompt,
                max_tokens=request.max_tokens or context_config.max_tokens,
                temperature=request.temperature or context_config.temperature,
                top_p=context_config.top_p,
                stop=["</s>", "Human:", "Assistant:"]
            )
            
            # Извлекаем ответ
            if hasattr(response_data, 'choices') and response_data.choices:
                response_text = response_data.choices[0].text.strip()
            else:
                response_text = str(response_data)
            
            # Вычисляем время обработки
            processing_time = (datetime.now(UTC) - start_time).total_seconds()
            
            # Оцениваем уверенность (простая эвристика)
            confidence_score = self._calculate_confidence(response_text, request.context)
            
            # Обновляем сессию
            if request.session_id:
                self._update_session(request.session_id, request.context, request.prompt, response_text)
            
            return GenerateResponse(
                response=response_text,
                context_used=request.context.value,
                model_used=request.model_type.value,
                tokens_used=len(response_text.split()),  # Приблизительно
                processing_time=processing_time,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")

    def _build_prompt(self, user_prompt: str, context_config: ContextConfig, request: GenerateRequest) -> str:
        """Строит полный промпт с учетом контекста и истории"""
        
        # Базовый промпт
        prompt_parts = [
            f"<s>[INST] {context_config.system_prompt} [/INST]",
        ]
        
        # Добавляем историю сессии
        if request.session_id and request.session_id in self.sessions:
            session = self.sessions[request.session_id]
            if "history" in session:
                for entry in session["history"][-3:]:  # Последние 3 сообщения
                    prompt_parts.append(f"Human: {entry['user']}")
                    prompt_parts.append(f"Assistant: {entry['assistant']}")
        
        # Добавляем текущий запрос
        prompt_parts.append(f"Human: {user_prompt}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)

    def _calculate_confidence(self, response: str, context: ContextType) -> float:
        """Вычисляет оценку уверенности в ответе"""
        # Простая эвристика на основе длины и структуры ответа
        if not response or len(response) < 10:
            return 0.1
        
        # Базовый скор
        confidence = 0.5
        
        # Бонусы за качество
        if len(response) > 50:
            confidence += 0.2
        if any(word in response.lower() for word in ["потому что", "например", "во-первых", "во-вторых"]):
            confidence += 0.1
        if response.count(".") > 2:
            confidence += 0.1
        if context == ContextType.WORK and any(word in response.lower() for word in ["проект", "задача", "план", "результат"]):
            confidence += 0.1
        if context == ContextType.HOME and any(word in response.lower() for word in ["привычка", "рефлексия", "цель", "развитие"]):
            confidence += 0.1
        
        return min(confidence, 1.0)

    def _update_session(self, session_id: str, context: ContextType, user_prompt: str, assistant_response: str):
        """Обновляет историю сессии"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {"history": [], "context": context}
        
        self.sessions[session_id]["history"].append({
            "user": user_prompt,
            "assistant": assistant_response,
            "timestamp": datetime.now(UTC).isoformat(),
            "context": context.value
        })
        
        # Ограничиваем историю
        if len(self.sessions[session_id]["history"]) > 10:
            self.sessions[session_id]["history"] = self.sessions[session_id]["history"][-10:]

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Запускает сервер"""
        logger.info(f"Запуск локального LLM сервера на {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

# Глобальный экземпляр сервера
llm_server = LocalLLMServer()

if __name__ == "__main__":
    llm_server.run() 