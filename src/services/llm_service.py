"""Unified LLM service for AI-powered operations."""
import logging
import json
import aiohttp
from typing import Optional, Dict, Any, List, Sequence
from abc import ABC, abstractmethod
from aiohttp import ClientError
from pydantic import BaseSettings

from ..config import settings, Settings, OPENAI_API_KEY, DEEPSEEK_API_KEY
from .base_service import BaseService

logger = logging.getLogger(__name__)

class LLMError(Exception):
    """Base exception for LLM services."""
    pass

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from the LLM."""
        pass

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""
    
    def __init__(self) -> None:
        """Initialize OpenAI provider."""
        self.api_key = OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API key not found")

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API."""
        try:
            if not self.api_key:
                return "OpenAI API key not configured"
                
            # Using aiohttp for async requests
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 150)
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        return f"OpenAI API error: {response.status}"
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return f"Error generating response: {str(e)}"

class DeepseekProvider(BaseLLMProvider):
    """Deepseek API provider."""
    
    def __init__(self) -> None:
        """Initialize Deepseek provider."""
        self.settings: Settings = settings
        self.api_key = DEEPSEEK_API_KEY
        self.model = getattr(self.settings, 'DEEPSEEK_MODEL', 'deepseek-chat')
        self.api_url = getattr(self.settings, 'DEEPSEEK_API_URL', 'https://hubai.loe.gg/v1')
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            logger.warning("Deepseek API key not found")

    async def initialize(self) -> None:
        """Initialize HTTP session."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
            
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.session:
            await self.session.close()
            self.session = None

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Deepseek API."""
        try:
            await self.initialize()
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            url = f"{self.api_url}/chat/completions"
            
            async with self.session.post(url, json=data) as response:
                response.raise_for_status()
                result = await response.json()
                return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Deepseek API error: {e}", exc_info=True)
            return f"Error generating response: {str(e)}"
            
class LocalLLMProvider(BaseLLMProvider):
    """Local LLM provider (Ollama, etc.)."""
    
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        """Initialize local LLM provider."""
        self.base_url = base_url
        self.model = "llama2"  # Default model
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> None:
        """Initialize HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.session:
            await self.session.close()
            self.session = None

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using local LLM."""
        try:
            await self.initialize()
            
            data = {
                "model": kwargs.get("model", self.model),
                "prompt": prompt,
                "stream": False
            }
            
            url = f"{self.base_url}/api/generate"
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    return f"Local LLM error: {response.status}"
            
        except Exception as e:
            logger.error(f"Local LLM error: {e}", exc_info=True)
            return f"Error generating response: {str(e)}"

class LLMService(BaseService):
    """Unified service for handling LLM operations."""
    
    def __init__(self) -> None:
        """Initialize LLM service."""
        super().__init__()
        self.providers: Dict[str, BaseLLMProvider] = {
            "openai": OpenAIProvider(),
            "deepseek": DeepseekProvider(),
            "local": LocalLLMProvider()
        }
        self.default_provider = "openai"

    def set_default_provider(self, provider: str) -> None:
        """Set default LLM provider."""
        if provider in self.providers:
            self.default_provider = provider
        else:
            logger.error(f"Provider {provider} not found")

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        provider: str = None
    ) -> str:
        """Generate text based on prompt."""
        provider_name = provider or self.default_provider
        return await self.providers[provider_name].generate_response(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

    async def analyze_text(
        self,
        text: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze text and return structured data."""
        prompt = f"""Analyze the following text and provide structured analysis.
Type: {analysis_type}
Text: {text}

Please provide analysis in the following JSON format:
{{
    "sentiment": "positive/negative/neutral",
    "key_points": ["point1", "point2", ...],
    "entities": ["entity1", "entity2", ...],
    "topics": ["topic1", "topic2", ...],
    "summary": "brief summary"
}}"""
        
        try:
            response = await self.generate_text(prompt)
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return {
                "sentiment": "neutral",
                "key_points": [],
                "entities": [],
                "topics": [],
                "summary": "Analysis failed"
            }

    async def extract_topics(
        self,
        text: str,
        max_topics: int = 5
    ) -> List[str]:
        """Extract main topics from text."""
        prompt = f"""Extract up to {max_topics} main topics from the following text.
Text: {text}

Please provide topics in JSON array format:
["topic1", "topic2", ...]"""
        
        try:
            response = await self.generate_text(prompt)
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse topics response: {e}")
            return []
            
    async def generate_summary(
        self,
        text: str,
        max_length: int = 200
    ) -> str:
        """Generate a concise summary of text."""
        prompt = f"""Generate a concise summary of the following text in {max_length} characters or less.
Text: {text}"""
        
        return await self.generate_text(prompt)

    async def generate_suggestions(
        self,
        context: str,
        num_suggestions: int = 3
    ) -> List[str]:
        """Generate suggestions based on context."""
        prompt = f"""Based on the following context, generate {num_suggestions} suggestions.
Context: {context}

Please provide suggestions in JSON array format:
["suggestion1", "suggestion2", ...]"""
        
        try:
            response = await self.generate_text(prompt)
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse suggestions response: {e}")
            return []
            
    async def get_task_suggestions(self, task_description: str) -> Dict[str, Any]:
        """Get AI suggestions for task properties."""
        prompt = f"""
        Based on this task description, suggest:
        1. A clear title (max 60 chars)
        2. Priority level (High/Medium/Low)
        3. Estimated time to complete (in hours)
        4. Any potential subtasks
        
        Task description: {task_description}
        
        Format your response as:
        Title: [title]
        Priority: [priority]
        Estimate: [hours]
        Subtasks: [comma-separated list]
        """
        
        response = await self.generate_text(
            prompt,
            temperature=0.7,
            max_tokens=200
        )
        
        # Parse response into structured format
        suggestions: Dict[str, Any] = {
            "title": "",
            "priority": "Medium",
            "estimate": 1.0,
            "subtasks": []
        }
        
        try:
            for line in response.split("\n"):
                if line.startswith("Title:"):
                    suggestions["title"] = line.replace("Title:", "").strip()
                elif line.startswith("Priority:"):
                    suggestions["priority"] = line.replace("Priority:", "").strip()
                elif line.startswith("Estimate:"):
                    estimate_str = line.replace("Estimate:", "").strip()
                    suggestions["estimate"] = float(estimate_str.split()[0])
                elif line.startswith("Subtasks:"):
                    subtasks = line.replace("Subtasks:", "").strip()
                    suggestions["subtasks"] = [s.strip() for s in subtasks.split(",")]
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}", exc_info=True)
            
        return suggestions

    async def improve_task_description(self, description: str) -> str:
        """Improve task description using AI."""
        prompt = f"""
        Improve this task description to be more clear, actionable, and structured:
        
        {description}
        
        Make it:
        1. Clear and concise
        2. Action-oriented
        3. Include acceptance criteria if applicable
        4. Well-formatted with bullet points if needed
        """
        
        return await self.generate_text(
            prompt,
            temperature=0.7,
            max_tokens=250
        )

    async def analyze_task_completion(self, task_description: str, completion_notes: str) -> str:
        """Analyze task completion and provide feedback."""
        prompt = f"""
        Analyze this task completion and provide brief feedback:
        
        Original task: {task_description}
        Completion notes: {completion_notes}
        
        Consider:
        1. Was the task completed according to requirements?
        2. Any notable achievements?
        3. Any areas for improvement?
        4. Suggestions for similar tasks in future?
        """
        
        return await self.generate_text(
            prompt,
            temperature=0.7,
            max_tokens=200
        )

    async def cleanup(self) -> None:
        """Cleanup all provider resources."""
        for provider in self.providers.values():
            if hasattr(provider, 'cleanup'):
                await provider.cleanup() 