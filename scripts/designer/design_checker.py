#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 AI ПРОВЕРКА ДИЗАЙН-МАКЕТОВ
Автоматический анализ качества дизайна с помощью AI
"""

import os
import logging
from typing import Dict, List, Any
import httpx
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-DzPhbaSCgP7_YPxOuPvMOA')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://hubai.loe.gg/v1')

class DesignChecker:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.base_url = DEEPSEEK_BASE_URL
        self.total_tokens_used = 0
    
    async def analyze_design(self, image_url: str, context: str = "") -> Dict[str, Any]:
        """Анализ дизайн-макета с помощью AI"""
        
        try:
            # Короткий промпт для анализа (100 токенов)
            prompt = f"""
            Анализ дизайн-макета: {image_url}
            Контекст: {context}
            
            Оцени по шкале 1-10:
            - Композиция и баланс
            - Цветовая схема  
            - Типографика
            - Современность
            - Функциональность
            
            Верни JSON: {{"composition": 8, "colors": 7, "typography": 9, "modernity": 8, "functionality": 7, "overall": 8, "issues": ["проблема1", "проблема2"], "suggestions": ["совет1", "совет2"]}}
            """
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "max_tokens": 300
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Подсчет токенов
                    usage = result.get('usage', {})
                    total_tokens = usage.get('total_tokens', 0)
                    self.total_tokens_used += total_tokens
                    
                    logger.info(f"💰 Токены на анализ дизайна: {total_tokens} | Всего: {self.total_tokens_used}")
                    
                    # Парсим JSON
                    try:
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start != -1 and end != 0:
                            analysis = json.loads(content[start:end])
                            return analysis
                    except json.JSONDecodeError:
                        pass
                    
                    # Fallback
                    return self._default_analysis()
                else:
                    logger.error(f"Ошибка API: {response.status_code}")
                    return self._default_analysis()
                    
        except Exception as e:
            logger.error(f"Ошибка анализа дизайна: {e}")
            return self._default_analysis()
    
    def _default_analysis(self) -> Dict[str, Any]:
        """Анализ по умолчанию"""
        return {
            "composition": 5,
            "colors": 5,
            "typography": 5,
            "modernity": 5,
            "functionality": 5,
            "overall": 5,
            "issues": ["Не удалось проанализировать"],
            "suggestions": ["Проверьте качество изображения"]
        }
    
    async def batch_analyze(self, designs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Пакетный анализ нескольких макетов"""
        results = []
        
        for design in designs:
            logger.info(f"🔍 Анализирую: {design.get('name', 'Без названия')}")
            analysis = await self.analyze_design(
                design.get('url', ''),
                design.get('context', '')
            )
            analysis['design_name'] = design.get('name', 'Без названия')
            results.append(analysis)
        
        return results
    
    def generate_report(self, analyses: List[Dict[str, Any]]) -> str:
        """Генерация отчета по анализу"""
        if not analyses:
            return "❌ Нет данных для анализа"
        
        report = f"""
# 🎨 ОТЧЕТ ПО АНАЛИЗУ ДИЗАЙН-МАКЕТОВ
**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Всего макетов:** {len(analyses)}
**Токенов использовано:** {self.total_tokens_used}

## 📊 СРЕДНИЕ ОЦЕНКИ
"""
        
        # Средние оценки
        avg_scores = {}
        for key in ['composition', 'colors', 'typography', 'modernity', 'functionality', 'overall']:
            scores = [a.get(key, 0) for a in analyses if a.get(key)]
            if scores:
                avg_scores[key] = sum(scores) / len(scores)
        
        for key, value in avg_scores.items():
            report += f"- **{key.title()}:** {value:.1f}/10\n"
        
        report += "\n## 🎯 ДЕТАЛЬНЫЙ АНАЛИЗ\n"
        
        for analysis in analyses:
            name = analysis.get('design_name', 'Без названия')
            overall = analysis.get('overall', 0)
            
            report += f"\n### {name} (Оценка: {overall}/10)\n"
            report += f"- Композиция: {analysis.get('composition', 0)}/10\n"
            report += f"- Цвета: {analysis.get('colors', 0)}/10\n"
            report += f"- Типографика: {analysis.get('typography', 0)}/10\n"
            report += f"- Современность: {analysis.get('modernity', 0)}/10\n"
            report += f"- Функциональность: {analysis.get('functionality', 0)}/10\n"
            
            issues = analysis.get('issues', [])
            if issues:
                report += f"- **Проблемы:** {', '.join(issues)}\n"
            
            suggestions = analysis.get('suggestions', [])
            if suggestions:
                report += f"- **Рекомендации:** {', '.join(suggestions)}\n"
        
        return report

# Пример использования
async def main():
    checker = DesignChecker()
    
    # Тестовые макеты
    designs = [
        {
            "name": "Главная страница сайта",
            "url": "https://example.com/design1.jpg",
            "context": "Лендинг для IT-компании"
        },
        {
            "name": "Мобильное приложение",
            "url": "https://example.com/design2.jpg", 
            "context": "UI для финтех приложения"
        }
    ]
    
    # Анализ
    analyses = await checker.batch_analyze(designs)
    
    # Отчет
    report = checker.generate_report(analyses)
    print(report)
    
    # Сохраняем в файл
    with open(f"design_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 