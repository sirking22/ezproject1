"""
Модуль локальной LLM интеграции для персональной AI-экосистемы
"""

from .local_server import LocalLLMServer, llm_server
from .client import LocalLLMClient

__all__ = ["LocalLLMServer", "llm_server", "LocalLLMClient"] 