#!/usr/bin/env python3
"""
Клиент для локального LLM сервера
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, UTC
from dataclasses import dataclass

from .local_server import ContextType, ModelType, GenerateRequest, GenerateResponse

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    text: str
    context: str
    model: str
    tokens: int
    processing_time: float
    confidence: float
    metadata: Dict[str, Any]

class LocalLLMClient:
    """
    Клиент для взаимодействия с локальным LLM сервером
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.default_context = ContextType.HOME
        self.default_model = ModelType.DEFAULT
        
        logger.info(f"LLM клиент инициализирован: {base_url}")

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        if self.session:
            await self.session.close()

    async def generate(self, prompt: str, context: ContextType = None, 
                      model_type: ModelType = None, session_id: str = None,
                      user_id: str = None, **kwargs) -> LLMResponse:
        """
        Генерирует ответ через локальный LLM сервер
        """
        if not self.session:
            raise RuntimeError("Клиент не инициализирован. Используйте async with LocalLLMClient()")
        
        context = context or self.default_context
        model_type = model_type or self.default_model
        
        request_data = GenerateRequest(
            prompt=prompt,
            context=context,
            model_type=model_type,
            session_id=session_id,
            user_id=user_id,
            **kwargs
        )
        
        try:
            async with self.session.post(
                f"{self.base_url}/generate",
                json=request_data.dict()
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"LLM сервер вернул ошибку {response.status}: {error_text}")
                
                data = await response.json()
                return LLMResponse(
                    text=data["response"],
                    context=data["context_used"],
                    model=data["model_used"],
                    tokens=data["tokens_used"],
                    processing_time=data["processing_time"],
                    confidence=data["confidence_score"],
                    metadata={
                        "session_id": session_id,
                        "user_id": user_id,
                        "timestamp": datetime.now(UTC).isoformat()
                    }
                )
                
        except Exception as e:
            logger.error(f"Ошибка запроса к LLM серверу: {e}")
            raise

    async def generate_work_context(self, prompt: str, **kwargs) -> LLMResponse:
        """Генерирует ответ в рабочем контексте"""
        return await self.generate(prompt, context=ContextType.WORK, **kwargs)

    async def generate_home_context(self, prompt: str, **kwargs) -> LLMResponse:
        """Генерирует ответ в домашнем контексте"""
        return await self.generate(prompt, context=ContextType.HOME, **kwargs)

    async def generate_general_context(self, prompt: str, **kwargs) -> LLMResponse:
        """Генерирует ответ в общем контексте"""
        return await self.generate(prompt, context=ContextType.GENERAL, **kwargs)

    async def set_session_context(self, session_id: str, context: ContextType) -> bool:
        """Устанавливает контекст для сессии"""
        if not self.session:
            return False
        
        try:
            async with self.session.post(
                f"{self.base_url}/session/{session_id}/context",
                json={"context": context.value}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Ошибка установки контекста сессии: {e}")
            return False

    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Получает информацию о сессии"""
        if not self.session:
            return {}
        
        try:
            async with self.session.get(f"{self.base_url}/session/{session_id}") as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            logger.error(f"Ошибка получения информации о сессии: {e}")
            return {}

    async def health_check(self) -> bool:
        """Проверяет здоровье LLM сервера"""
        if not self.session:
            return False
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья сервера: {e}")
            return False

    async def get_contexts(self) -> Dict[str, Any]:
        """Получает информацию о доступных контекстах"""
        if not self.session:
            return {}
        
        try:
            async with self.session.get(f"{self.base_url}/contexts") as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as e:
            logger.error(f"Ошибка получения контекстов: {e}")
            return {}

# Утилитарные функции для быстрого использования

async def quick_generate(prompt: str, context: str = "home", **kwargs) -> str:
    """
    Быстрая генерация ответа без создания клиента
    """
    async with LocalLLMClient() as client:
        context_enum = ContextType(context)
        response = await client.generate(prompt, context=context_enum, **kwargs)
        return response.text

async def quick_work_generate(prompt: str, **kwargs) -> str:
    """Быстрая генерация в рабочем контексте"""
    return await quick_generate(prompt, context="work", **kwargs)

async def quick_home_generate(prompt: str, **kwargs) -> str:
    """Быстрая генерация в домашнем контексте"""
    return await quick_generate(prompt, context="home", **kwargs) 