"""
Система улучшения детерминированных правил на основе собранных данных
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class RuleImprovement:
    """Улучшение правила"""
    rule_name: str
    old_pattern: str
    new_pattern: str
    reason: str
    confidence: float
    test_cases: List[str]

@dataclass
class PerformanceMetric:
    """Метрика производительности правила"""
    rule_name: str
    success_rate: float
    average_time_ms: float
    error_patterns: List[Dict[str, str]]
    improvement_suggestions: List[str]

class DeterministicRuleImprover:
    """Система улучшения детерминированных правил"""
    
    def __init__(self):
        self.improvements = []
        self.performance_metrics = []
        self.test_results = {"results": []}
        self.current_rules = {
            "title_cleaning": {
                "patterns": [
                    (r'^📱\s*', ''),
                    (r'^https://.*?\s', ''),
                    (r'\s+', ' '),
                    (r'^\s+|\s+$', '')
                ],
                "description": "Очистка названий от эмодзи, ссылок и лишних пробелов"
            },
            "auto_tagging": {
                "domains": {
                    "instagram.com": "Social Media",
                    "youtube.com": "Video Platform",
                    "facebook.com": "Social Media",
                    "vk.com": "Social Media",
                    "t.me": "Telegram"
                },
                "keywords": {
                    "дизайн": "Design",
                    "design": "Design",
                    "figma": "Design",
                    "ui": "Design",
                    "ux": "Design",
                    "видео": "Video",
                    "video": "Video",
                    "youtube": "Video",
                    "монтаж": "Video",
                    "фото": "Photo",
                    "photo": "Photo",
                    "изображение": "Photo",
                    "image": "Photo"
                },
                "description": "Автоматическое тегирование по доменам и ключевым словам"
            },
            "classification": {
                "rules": [
                    ("len(text) < 3", "Garbage"),
                    ("len(text) > 100", "Long Content"),
                    ("contains_digits", "Data Entry"),
                    ("contains_emoji", "Social Content"),
                    ("starts_with_http", "Link"),
                    ("default", "Regular Content")
                ],
                "description": "Классификация контента по типу"
            }
        }
    
    def load_test_results(self, filename: str = "deterministic_test_results.json"):
        """Загружает результаты тестирования"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.test_results = data
            print(f"✅ Загружено {len(data.get('results', []))} результатов тестирования")
            
        except FileNotFoundError:
            print(f"❌ Файл {filename} не найден")
            self.test_results = {"results": []}
        except Exception as e:
            print(f"❌ Ошибка загрузки результатов: {e}")
            self.test_results = {"results": []}
    
    def analyze_performance(self) -> List[PerformanceMetric]:
        """Анализирует производительность правил"""
        if not self.test_results.get("results"):
            print("⚠️ Нет результатов для анализа")
            return []
        
        # Группируем результаты по правилам
        rule_results = {}
        for result in self.test_results["results"]:
            rule_name = result["rule_name"]
            if rule_name not in rule_results:
                rule_results[rule_name] = []
            rule_results[rule_name].append(result)
        
        metrics = []
        
        for rule_name, results in rule_results.items():
            # Вычисляем метрики
            total_tests = len(results)
            successful_tests = len([r for r in results if r["success"]])
            success_rate = successful_tests / total_tests if total_tests > 0 else 0
            
            # Среднее время
            times = [r["processing_time_ms"] for r in results if r["success"]]
            average_time = sum(times) / len(times) if times else 0
            
            # Паттерны ошибок
            errors = [r for r in results if not r["success"]]
            error_patterns = []
            for error in errors:
                error_patterns.append({
                    "input": error["input_text"][:50],
                    "error": error.get("error_message", "Unknown error")
                })
            
            # Предложения по улучшению
            improvements = self.generate_improvement_suggestions(rule_name, results)
            
            metric = PerformanceMetric(
                rule_name=rule_name,
                success_rate=success_rate,
                average_time_ms=average_time,
                error_patterns=error_patterns,
                improvement_suggestions=improvements
            )
            
            metrics.append(metric)
        
        self.performance_metrics = metrics
        return metrics
    
    def generate_improvement_suggestions(self, rule_name: str, results: List[Dict]) -> List[str]:
        """Генерирует предложения по улучшению правил"""
        suggestions = []
        
        if rule_name == "title_cleaning":
            # Анализируем случаи, где очистка не сработала
            failed_results = [r for r in results if not r["success"]]
            if failed_results:
                suggestions.append("Добавить обработку специальных символов")
                suggestions.append("Улучшить регулярные выражения для ссылок")
            
            # Анализируем длинные названия
            long_titles = [r for r in results if len(r["input_text"]) > 50]
            if long_titles:
                suggestions.append("Добавить обрезку длинных названий")
        
        elif rule_name == "auto_tagging":
            # Анализируем случаи без тегов
            no_tags = []
            for r in results:
                if r["success"] and isinstance(r["output"], dict):
                    tags = r["output"].get("tags", [])
                    if not tags:
                        no_tags.append(r["input_text"])
            
            if no_tags:
                suggestions.append("Расширить список ключевых слов")
                suggestions.append("Добавить анализ контекста")
            
            # Анализируем домены
            domains_in_text = []
            for result in results:
                text = result["input_text"].lower()
                if any(domain in text for domain in ["instagram", "youtube", "facebook", "vk"]):
                    domains_in_text.append(result["input_text"])
            
            if domains_in_text:
                suggestions.append("Улучшить распознавание доменов")
        
        elif rule_name == "classification":
            # Анализируем неправильную классификацию
            misclassified = []
            for result in results:
                if result["success"]:
                    output = result["output"]
                    if isinstance(output, dict) and "category" in output:
                        # Проверяем логику классификации
                        text = result["input_text"]
                        expected_category = self.classify_content_improved(text)
                        actual_category = output["category"]
                        
                        if expected_category != actual_category:
                            misclassified.append({
                                "text": text,
                                "expected": expected_category,
                                "actual": actual_category
                            })
            
            if misclassified:
                suggestions.append("Улучшить логику классификации")
                suggestions.append("Добавить новые категории")
        
        return suggestions
    
    def classify_content_improved(self, text: str) -> str:
        """Улучшенная классификация контента"""
        cleaned = text.strip()
        
        # Более точная логика
        if len(cleaned) < 3:
            return "Garbage"
        elif len(cleaned) > 100:
            return "Long Content"
        elif any(char.isdigit() for char in cleaned):
            return "Data Entry"
        elif any(ord(char) > 127 for char in cleaned):
            return "Social Content"
        elif cleaned.startswith("http"):
            return "Link"
        elif any(word in cleaned.lower() for word in ["дизайн", "design", "figma"]):
            return "Design Content"
        elif any(word in cleaned.lower() for word in ["видео", "video", "youtube"]):
            return "Video Content"
        else:
            return "Regular Content"
    
    def create_rule_improvements(self) -> List[RuleImprovement]:
        """Создает улучшения правил на основе анализа"""
        improvements = []
        
        for metric in self.performance_metrics:
            if metric.success_rate < 0.9:  # Если успешность меньше 90%
                
                if metric.rule_name == "title_cleaning":
                    # Добавляем новые паттерны очистки
                    improvement = RuleImprovement(
                        rule_name="title_cleaning",
                        old_pattern="basic_cleaning",
                        new_pattern="enhanced_cleaning",
                        reason=f"Низкая успешность: {metric.success_rate:.1%}",
                        confidence=0.8,
                        test_cases=[error["input"] for error in metric.error_patterns[:3]]
                    )
                    improvements.append(improvement)
                
                elif metric.rule_name == "auto_tagging":
                    # Расширяем список тегов
                    improvement = RuleImprovement(
                        rule_name="auto_tagging",
                        old_pattern="basic_tagging",
                        new_pattern="enhanced_tagging",
                        reason=f"Низкая успешность: {metric.success_rate:.1%}",
                        confidence=0.7,
                        test_cases=[error["input"] for error in metric.error_patterns[:3]]
                    )
                    improvements.append(improvement)
                
                elif metric.rule_name == "classification":
                    # Улучшаем классификацию
                    improvement = RuleImprovement(
                        rule_name="classification",
                        old_pattern="basic_classification",
                        new_pattern="enhanced_classification",
                        reason=f"Низкая успешность: {metric.success_rate:.1%}",
                        confidence=0.9,
                        test_cases=[error["input"] for error in metric.error_patterns[:3]]
                    )
                    improvements.append(improvement)
        
        self.improvements = improvements
        return improvements
    
    def apply_improvements(self) -> Dict[str, Any]:
        """Применяет улучшения к правилам"""
        improved_rules = self.current_rules.copy()
        
        for improvement in self.improvements:
            if improvement.rule_name == "title_cleaning":
                # Добавляем новые паттерны очистки
                improved_rules["title_cleaning"]["patterns"].extend([
                    (r'[^\w\s\-\.]', ''),  # Удаляем специальные символы
                    (r'\s{2,}', ' '),      # Множественные пробелы
                    (r'^\d+\s*', ''),      # Цифры в начале
                ])
            
            elif improvement.rule_name == "auto_tagging":
                # Расширяем список доменов и ключевых слов
                improved_rules["auto_tagging"]["domains"].update({
                    "tiktok.com": "Social Media",
                    "twitter.com": "Social Media",
                    "linkedin.com": "Professional",
                    "medium.com": "Content"
                })
                
                improved_rules["auto_tagging"]["keywords"].update({
                    "маркетинг": "Marketing",
                    "marketing": "Marketing",
                    "реклама": "Advertising",
                    "advertising": "Advertising",
                    "контент": "Content",
                    "content": "Content"
                })
            
            elif improvement.rule_name == "classification":
                # Улучшаем логику классификации
                improved_rules["classification"]["rules"] = [
                    ("len(text) < 3", "Garbage"),
                    ("len(text) > 100", "Long Content"),
                    ("contains_digits", "Data Entry"),
                    ("contains_emoji", "Social Content"),
                    ("starts_with_http", "Link"),
                    ("contains_design_keywords", "Design Content"),
                    ("contains_video_keywords", "Video Content"),
                    ("contains_marketing_keywords", "Marketing Content"),
                    ("default", "Regular Content")
                ]
        
        return improved_rules
    
    def save_improvements(self, filename: str = "rule_improvements.json"):
        """Сохраняет улучшения правил"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": [
                {
                    "rule_name": m.rule_name,
                    "success_rate": m.success_rate,
                    "average_time_ms": m.average_time_ms,
                    "error_patterns": m.error_patterns,
                    "improvement_suggestions": m.improvement_suggestions
                }
                for m in self.performance_metrics
            ],
            "improvements": [
                {
                    "rule_name": i.rule_name,
                    "old_pattern": i.old_pattern,
                    "new_pattern": i.new_pattern,
                    "reason": i.reason,
                    "confidence": i.confidence,
                    "test_cases": i.test_cases
                }
                for i in self.improvements
            ],
            "improved_rules": self.apply_improvements()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Улучшения сохранены в {filename}")
    
    def print_analysis_summary(self):
        """Выводит сводку анализа"""
        if not self.performance_metrics:
            print("❌ Нет данных для анализа")
            return
        
        print("\n📊 АНАЛИЗ ПРОИЗВОДИТЕЛЬНОСТИ ДЕТЕРМИНИРОВАННЫХ ПРАВИЛ")
        print("=" * 60)
        
        for metric in self.performance_metrics:
            print(f"\n🔧 {metric.rule_name.upper()}:")
            print(f"   Успешность: {metric.success_rate:.1%}")
            print(f"   Среднее время: {metric.average_time_ms:.2f}ms")
            
            if metric.improvement_suggestions:
                print(f"   Предложения по улучшению:")
                for suggestion in metric.improvement_suggestions:
                    print(f"     • {suggestion}")
        
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        total_rules = len(self.performance_metrics)
        high_performance = len([m for m in self.performance_metrics if m.success_rate > 0.9])
        low_performance = len([m for m in self.performance_metrics if m.success_rate < 0.7])
        
        print(f"   Всего правил: {total_rules}")
        print(f"   Высокая производительность: {high_performance}")
        print(f"   Требует улучшения: {low_performance}")
        
        if self.improvements:
            print(f"\n🚀 ПРЕДЛОЖЕННЫЕ УЛУЧШЕНИЯ:")
            for improvement in self.improvements:
                print(f"   • {improvement.rule_name}: {improvement.reason}")

def main():
    """Основная функция для улучшения правил"""
    
    improver = DeterministicRuleImprover()
    
    # Загружаем результаты тестирования
    improver.load_test_results()
    
    # Анализируем производительность
    metrics = improver.analyze_performance()
    
    # Создаем улучшения
    improvements = improver.create_rule_improvements()
    
    # Выводим сводку
    improver.print_analysis_summary()
    
    # Сохраняем улучшения
    improver.save_improvements()
    
    print("\n✅ Анализ и улучшение завершены!")

if __name__ == "__main__":
    main() 