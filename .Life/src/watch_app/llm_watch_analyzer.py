#!/usr/bin/env python3
"""
Анализатор данных Xiaomi Watch S через локальную Llama 70B
Контекстный анализ биометрии и персональные рекомендации
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, UTC, timedelta
from dataclasses import dataclass, asdict
import aiohttp
from enum import Enum

from ..integrations.xiaomi_watch import XiaomiWatchAPI, BiometricData

logger = logging.getLogger(__name__)

class ContextType(Enum):
    MORNING = "morning"
    WORK = "work"
    EVENING = "evening"
    NIGHT = "night"
    STRESS = "stress"
    ACTIVITY = "activity"
    SLEEP = "sleep"

@dataclass
class BiometricContext:
    """Контекст биометрических данных для LLM"""
    context_type: ContextType
    biometrics: BiometricData
    time_of_day: str
    day_of_week: str
    stress_trend: str
    sleep_quality_trend: str
    activity_level_trend: str
    recommendations_needed: List[str]

@dataclass
class LLMInsight:
    """Инсайт от локальной LLM"""
    insight_type: str
    title: str
    description: str
    confidence: float
    actionable: bool
    action_items: List[str]
    context: Dict[str, Any]

class LLMWatchAnalyzer:
    """Анализатор данных часов через локальную LLM"""
    
    def __init__(self, local_llm_url: str = "http://localhost:8000"):
        self.watch_api = XiaomiWatchAPI()
        self.local_llm_url = local_llm_url
        self.biometric_history: List[BiometricData] = []
        self.insights_history: List[LLMInsight] = []
        
        # Настройки для анализа
        self.stress_threshold = 70.0
        self.low_activity_threshold = 3000
        self.poor_sleep_threshold = 60.0
        
    async def analyze_biometrics_with_llm(self, biometrics: BiometricData) -> LLMInsight:
        """Анализ биометрических данных через локальную LLM"""
        try:
            # Создаем контекст
            context = await self._create_biometric_context(biometrics)
            
            # Формируем промпт для LLM
            prompt = self._build_analysis_prompt(context)
            
            # Получаем анализ от локальной LLM
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.local_llm_url}/generate",
                    json={
                        "prompt": prompt,
                        "context": context.context_type.value,
                        "max_tokens": 800,
                        "temperature": 0.7
                    }
                ) as response:
                    result = await response.json()
                    llm_response = result["response"]
            
            # Парсим ответ LLM
            insight = await self._parse_llm_response(llm_response, context)
            
            # Сохраняем в историю
            self.insights_history.append(insight)
            self.biometric_history.append(biometrics)
            
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing biometrics with LLM: {e}")
            return self._create_fallback_insight(biometrics)
    
    async def _create_biometric_context(self, biometrics: BiometricData) -> BiometricContext:
        """Создает контекст для анализа биометрических данных"""
        now = datetime.now()
        
        # Определяем тип контекста
        hour = now.hour
        if 6 <= hour < 10:
            context_type = ContextType.MORNING
        elif 10 <= hour < 18:
            context_type = ContextType.WORK
        elif 18 <= hour < 22:
            context_type = ContextType.EVENING
        else:
            context_type = ContextType.NIGHT
        
        # Анализируем тренды
        stress_trend = await self._analyze_stress_trend()
        sleep_trend = await self._analyze_sleep_trend()
        activity_trend = await self._analyze_activity_trend()
        
        # Определяем потребности в рекомендациях
        recommendations_needed = []
        if biometrics.stress_level and biometrics.stress_level > self.stress_threshold:
            recommendations_needed.append("stress_management")
        if biometrics.steps and biometrics.steps < self.low_activity_threshold:
            recommendations_needed.append("activity_boost")
        if biometrics.sleep_quality and biometrics.sleep_quality < self.poor_sleep_threshold:
            recommendations_needed.append("sleep_improvement")
        
        return BiometricContext(
            context_type=context_type,
            biometrics=biometrics,
            time_of_day=f"{hour:02d}:00",
            day_of_week=now.strftime("%A"),
            stress_trend=stress_trend,
            sleep_quality_trend=sleep_trend,
            activity_level_trend=activity_trend,
            recommendations_needed=recommendations_needed
        )
    
    def _build_analysis_prompt(self, context: BiometricContext) -> str:
        """Строит промпт для анализа биометрических данных"""
        
        prompt_parts = [
            "Ты персональный AI-аналитик здоровья и продуктивности. Проанализируй биометрические данные и дай персональные рекомендации.",
            "",
            f"КОНТЕКСТ: {context.context_type.value.upper()}",
            f"Время: {context.time_of_day}, {context.day_of_week}",
            "",
            "БИОМЕТРИЧЕСКИЕ ДАННЫЕ:",
            f"- Пульс: {context.biometrics.heart_rate} уд/мин",
            f"- Качество сна: {context.biometrics.sleep_quality}%",
            f"- Продолжительность сна: {context.biometrics.sleep_duration} ч",
            f"- Уровень стресса: {context.biometrics.stress_level}%",
            f"- Шаги: {context.biometrics.steps}",
            f"- Калории: {context.biometrics.calories}",
            "",
            "ТРЕНДЫ:",
            f"- Стресс: {context.stress_trend}",
            f"- Сон: {context.sleep_quality_trend}",
            f"- Активность: {context.activity_level_trend}",
            "",
            "ПОТРЕБНОСТИ В РЕКОМЕНДАЦИЯХ:",
            ", ".join(context.recommendations_needed) if context.recommendations_needed else "общие рекомендации",
            "",
            "ПРОАНАЛИЗИРУЙ И ДАЙ РЕКОМЕНДАЦИИ В СЛЕДУЮЩЕМ ФОРМАТЕ:",
            "ИНСАЙТ: [тип инсайта]",
            "НАЗВАНИЕ: [краткое название]",
            "ОПИСАНИЕ: [подробное описание]",
            "УВЕРЕННОСТЬ: [0-100]",
            "ДЕЙСТВИЯ: [список конкретных действий]",
            "КОНТЕКСТ: [дополнительная информация]"
        ]
        
        return "\n".join(prompt_parts)
    
    async def _parse_llm_response(self, response: str, context: BiometricContext) -> LLMInsight:
        """Парсит ответ от LLM в структурированный инсайт"""
        try:
            lines = response.strip().split('\n')
            insight_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    insight_data[key.strip().lower()] = value.strip()
            
            # Извлекаем данные
            insight_type = insight_data.get('инсайт', 'general')
            title = insight_data.get('название', 'Анализ биометрии')
            description = insight_data.get('описание', response)
            confidence = float(insight_data.get('уверенность', 75))
            
            # Парсим действия
            actions_text = insight_data.get('действия', '')
            action_items = [action.strip() for action in actions_text.split(',') if action.strip()]
            
            return LLMInsight(
                insight_type=insight_type,
                title=title,
                description=description,
                confidence=confidence,
                actionable=len(action_items) > 0,
                action_items=action_items,
                context=asdict(context)
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return self._create_fallback_insight(context.biometrics)
    
    def _create_fallback_insight(self, biometrics: BiometricData) -> LLMInsight:
        """Создает fallback инсайт при ошибках"""
        return LLMInsight(
            insight_type="fallback",
            title="Базовый анализ",
            description="Анализ биометрических данных временно недоступен",
            confidence=50.0,
            actionable=False,
            action_items=[],
            context={}
        )
    
    async def _analyze_stress_trend(self) -> str:
        """Анализирует тренд стресса"""
        if len(self.biometric_history) < 3:
            return "insufficient_data"
        
        recent_stress = [b.stress_level for b in self.biometric_history[-3:] if b.stress_level]
        if len(recent_stress) < 2:
            return "insufficient_data"
        
        if recent_stress[-1] > recent_stress[0] + 10:
            return "increasing"
        elif recent_stress[-1] < recent_stress[0] - 10:
            return "decreasing"
        else:
            return "stable"
    
    async def _analyze_sleep_trend(self) -> str:
        """Анализирует тренд качества сна"""
        if len(self.biometric_history) < 3:
            return "insufficient_data"
        
        recent_sleep = [b.sleep_quality for b in self.biometric_history[-3:] if b.sleep_quality]
        if len(recent_sleep) < 2:
            return "insufficient_data"
        
        if recent_sleep[-1] > recent_sleep[0] + 10:
            return "improving"
        elif recent_sleep[-1] < recent_sleep[0] - 10:
            return "declining"
        else:
            return "stable"
    
    async def _analyze_activity_trend(self) -> str:
        """Анализирует тренд активности"""
        if len(self.biometric_history) < 3:
            return "insufficient_data"
        
        recent_steps = [b.steps for b in self.biometric_history[-3:] if b.steps]
        if len(recent_steps) < 2:
            return "insufficient_data"
        
        if recent_steps[-1] > recent_steps[0] + 1000:
            return "increasing"
        elif recent_steps[-1] < recent_steps[0] - 1000:
            return "decreasing"
        else:
            return "stable"
    
    async def get_smart_notification_with_llm(self) -> str:
        """Генерирует умное уведомление с помощью локальной LLM"""
        try:
            # Получаем текущие биометрические данные
            biometrics = await self.watch_api.get_current_biometrics()
            
            # Анализируем через LLM
            insight = await self.analyze_biometrics_with_llm(biometrics)
            
            # Формируем уведомление на основе инсайта
            if insight.actionable and insight.action_items:
                action_text = f"\n\nРекомендую: {insight.action_items[0]}"
            else:
                action_text = ""
            
            notification = f"{insight.title}\n\n{insight.description}{action_text}"
            
            return notification
            
        except Exception as e:
            logger.error(f"Error generating smart notification: {e}")
            return "Добрый день! Как дела?"
    
    async def handle_voice_command_with_context(self, voice_text: str) -> str:
        """Обрабатывает голосовую команду с контекстом биометрии"""
        try:
            # Получаем биометрические данные
            biometrics = await self.watch_api.get_current_biometrics()
            
            # Формируем промпт с контекстом
            prompt = f"""
            Ты персональный ассистент. Обработай голосовую команду с учетом биометрического контекста.
            
            КОМАНДА: {voice_text}
            
            БИОМЕТРИЧЕСКИЙ КОНТЕКСТ:
            - Пульс: {biometrics.heart_rate} уд/мин
            - Стресс: {biometrics.stress_level}%
            - Активность: {biometrics.steps} шагов
            - Время: {datetime.now().strftime('%H:%M')}
            
            Дай полезный и контекстный ответ на команду пользователя.
            """
            
            # Получаем ответ от локальной LLM
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.local_llm_url}/generate",
                    json={
                        "prompt": prompt,
                        "context": "voice_command",
                        "max_tokens": 400,
                        "temperature": 0.7
                    }
                ) as response:
                    result = await response.json()
                    return result["response"]
                    
        except Exception as e:
            logger.error(f"Error handling voice command: {e}")
            return f"Обработал команду: {voice_text}. Что-то пошло не так с анализом."
    
    async def get_weekly_insights(self) -> List[LLMInsight]:
        """Получает недельные инсайты на основе биометрических данных"""
        try:
            # Собираем данные за неделю
            weekly_data = self.biometric_history[-7:] if len(self.biometric_history) >= 7 else self.biometric_history
            
            if not weekly_data:
                return []
            
            # Создаем сводку недели
            avg_heart_rate = sum(b.heart_rate for b in weekly_data if b.heart_rate) / len([b for b in weekly_data if b.heart_rate])
            avg_stress = sum(b.stress_level for b in weekly_data if b.stress_level) / len([b for b in weekly_data if b.stress_level])
            total_steps = sum(b.steps for b in weekly_data if b.steps)
            
            # Формируем промпт для недельного анализа
            prompt = f"""
            Проанализируй недельные биометрические данные и дай персональные инсайты.
            
            НЕДЕЛЬНЫЕ ДАННЫЕ:
            - Средний пульс: {avg_heart_rate:.1f} уд/мин
            - Средний стресс: {avg_stress:.1f}%
            - Общие шаги: {total_steps}
            - Количество дней с данными: {len(weekly_data)}
            
            Дай 3-5 ключевых инсайта для улучшения здоровья и продуктивности.
            """
            
            # Получаем анализ от LLM
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.local_llm_url}/generate",
                    json={
                        "prompt": prompt,
                        "context": "weekly_analysis",
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                ) as response:
                    result = await response.json()
                    llm_response = result["response"]
            
            # Парсим недельные инсайты
            insights = await self._parse_weekly_insights(llm_response)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting weekly insights: {e}")
            return []
    
    async def _parse_weekly_insights(self, response: str) -> List[LLMInsight]:
        """Парсит недельные инсайты из ответа LLM"""
        try:
            insights = []
            sections = response.split('\n\n')
            
            for section in sections:
                if 'ИНСАЙТ:' in section:
                    lines = section.strip().split('\n')
                    insight_data = {}
                    
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            insight_data[key.strip().lower()] = value.strip()
                    
                    if insight_data:
                        insight = LLMInsight(
                            insight_type=insight_data.get('инсайт', 'weekly'),
                            title=insight_data.get('название', 'Недельный инсайт'),
                            description=insight_data.get('описание', section),
                            confidence=float(insight_data.get('уверенность', 80)),
                            actionable=True,
                            action_items=insight_data.get('действия', '').split(',') if insight_data.get('действия') else [],
                            context={'type': 'weekly_analysis'}
                        )
                        insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error parsing weekly insights: {e}")
            return []

# Глобальный экземпляр для использования в других модулях
llm_watch_analyzer = LLMWatchAnalyzer() 