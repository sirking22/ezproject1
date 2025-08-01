"""
Система сбора и тестирования данных для детерминированных механик
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class TestCase:
    """Тестовый случай для детерминированных правил"""
    input_text: str
    expected_output: Dict[str, Any]
    category: str
    description: str
    priority: str = "Medium"

@dataclass
class RuleResult:
    """Результат применения правила"""
    rule_name: str
    input_text: str
    output: Dict[str, Any]
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None

class DeterministicDataCollector:
    """Сборщик данных для тестирования детерминированных правил"""
    
    def __init__(self):
        self.test_cases = []
        self.results = []
        self.rules = {
            "title_cleaning": self.clean_title,
            "auto_tagging": self.auto_tag,
            "classification": self.classify_content,
            "validation": self.validate_data,
            "transformation": self.transform_data
        }
    
    def clean_title(self, text: str) -> str:
        """Очистка названий (детерминированное правило)"""
        # Удаляем Telegram эмодзи
        text = re.sub(r'^📱\s*', '', text)
        
        # Удаляем ссылки в начале
        text = re.sub(r'^https://.*?\s', '', text)
        
        # Множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Пробелы в начале/конце
        text = re.sub(r'^\s+|\s+$', '', text)
        
        return text
    
    def auto_tag(self, text: str) -> List[str]:
        """Автотегирование (детерминированное правило)"""
        tags = []
        
        # Доменные теги
        domains = {
            "instagram.com": "Social Media",
            "youtube.com": "Video Platform",
            "facebook.com": "Social Media",
            "vk.com": "Social Media",
            "t.me": "Telegram",
            "tiktok.com": "Social Media",
            "twitter.com": "Social Media"
        }
        
        for domain, tag in domains.items():
            if domain in text.lower():
                tags.append(tag)
        
        # Тип контента
        if any(word in text.lower() for word in ["дизайн", "design", "figma", "ui", "ux"]):
            tags.append("Design")
        
        if any(word in text.lower() for word in ["видео", "video", "youtube", "монтаж"]):
            tags.append("Video")
        
        if any(word in text.lower() for word in ["фото", "photo", "изображение", "image"]):
            tags.append("Photo")
        
        return tags
    
    def classify_content(self, text: str) -> str:
        """Классификация контента (детерминированное правило)"""
        cleaned = text.strip()
        
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
        else:
            return "Regular Content"
    
    def validate_data(self, text: str) -> bool:
        """Валидация данных (детерминированное правило)"""
        if not text or len(text.strip()) == 0:
            return False
        
        if len(text) > 1000:
            return False
        
        # Проверяем на битые символы
        if any(ord(char) < 32 and char not in '\n\r\t' for char in text):
            return False
        
        return True
    
    def transform_data(self, text: str) -> Dict[str, Any]:
        """Трансформация данных (детерминированное правило)"""
        result = {
            "cleaned_text": self.clean_title(text),
            "tags": self.auto_tag(text),
            "category": self.classify_content(text),
            "is_valid": self.validate_data(text),
            "word_count": len(text.split()),
            "char_count": len(text),
            "has_links": "http" in text.lower(),
            "has_emoji": any(ord(char) > 127 for char in text)
        }
        
        return result
    
    def add_test_case(self, test_case: TestCase):
        """Добавляет тестовый случай"""
        self.test_cases.append(test_case)
    
    def load_test_cases_from_file(self, filename: str):
        """Загружает тестовые случаи из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                test_case = TestCase(
                    input_text=item["input_text"],
                    expected_output=item["expected_output"],
                    category=item["category"],
                    description=item["description"],
                    priority=item.get("priority", "Medium")
                )
                self.add_test_case(test_case)
                
            print(f"✅ Загружено {len(data)} тестовых случаев из {filename}")
            
        except FileNotFoundError:
            print(f"⚠️ Файл {filename} не найден, создаем новый")
        except Exception as e:
            print(f"❌ Ошибка загрузки тестовых случаев: {e}")
    
    def generate_test_cases_from_report(self, report_text: str):
        """Генерирует тестовые случаи из отчета совещания"""
        
        # Извлекаем данные из отчета
        lines = report_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) > 10:  # Игнорируем короткие строки
                
                # Создаем тестовый случай для очистки
                test_case = TestCase(
                    input_text=line,
                    expected_output={
                        "cleaned_text": self.clean_title(line),
                        "tags": self.auto_tag(line),
                        "category": self.classify_content(line),
                        "is_valid": self.validate_data(line)
                    },
                    category="report_data",
                    description=f"Данные из отчета: {line[:50]}...",
                    priority="High"
                )
                
                self.add_test_case(test_case)
    
    async def test_rule(self, rule_name: str, input_text: str) -> RuleResult:
        """Тестирует одно правило"""
        start_time = time.time()
        
        try:
            rule_func = self.rules[rule_name]
            output = rule_func(input_text)
            
            processing_time = (time.time() - start_time) * 1000
            
            result = RuleResult(
                rule_name=rule_name,
                input_text=input_text,
                output=output,
                processing_time_ms=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            result = RuleResult(
                rule_name=rule_name,
                input_text=input_text,
                output={},
                processing_time_ms=processing_time,
                success=False,
                error_message=str(e)
            )
        
        return result
    
    async def run_all_tests(self) -> List[RuleResult]:
        """Запускает все тесты"""
        results = []
        
        print(f"🧪 Запуск тестирования {len(self.test_cases)} случаев...")
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"Тестирование {i}/{len(self.test_cases)}: {test_case.description[:50]}...")
            
            # Тестируем все правила
            for rule_name in self.rules.keys():
                result = await self.test_rule(rule_name, test_case.input_text)
                results.append(result)
        
        self.results = results
        return results
    
    def analyze_results(self) -> Dict[str, Any]:
        """Анализирует результаты тестирования"""
        if not self.results:
            return {"error": "Нет результатов для анализа"}
        
        analysis = {
            "total_tests": len(self.results),
            "successful_tests": len([r for r in self.results if r.success]),
            "failed_tests": len([r for r in self.results if not r.success]),
            "average_processing_time": sum(r.processing_time_ms for r in self.results) / len(self.results),
            "rules_performance": {},
            "error_patterns": []
        }
        
        # Анализ по правилам
        for rule_name in self.rules.keys():
            rule_results = [r for r in self.results if r.rule_name == rule_name]
            if rule_results:
                analysis["rules_performance"][rule_name] = {
                    "total": len(rule_results),
                    "successful": len([r for r in rule_results if r.success]),
                    "average_time": sum(r.processing_time_ms for r in rule_results) / len(rule_results),
                    "success_rate": len([r for r in rule_results if r.success]) / len(rule_results)
                }
        
        # Анализ ошибок
        errors = [r for r in self.results if not r.success]
        for error in errors:
            analysis["error_patterns"].append({
                "rule": error.rule_name,
                "input": error.input_text[:100],
                "error": error.error_message
            })
        
        return analysis
    
    def save_results(self, filename: str = "deterministic_test_results.json"):
        """Сохраняет результаты тестирования"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "test_cases": [
                {
                    "input_text": tc.input_text,
                    "expected_output": tc.expected_output,
                    "category": tc.category,
                    "description": tc.description,
                    "priority": tc.priority
                }
                for tc in self.test_cases
            ],
            "results": [
                {
                    "rule_name": r.rule_name,
                    "input_text": r.input_text,
                    "output": r.output,
                    "processing_time_ms": r.processing_time_ms,
                    "success": r.success,
                    "error_message": r.error_message
                }
                for r in self.results
            ],
            "analysis": self.analyze_results()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Результаты сохранены в {filename}")
    
    def print_summary(self):
        """Выводит краткую сводку результатов"""
        if not self.results:
            print("❌ Нет результатов для анализа")
            return
        
        analysis = self.analyze_results()
        
        print("\n📊 СВОДКА ТЕСТИРОВАНИЯ ДЕТЕРМИНИРОВАННЫХ ПРАВИЛ")
        print("=" * 60)
        
        print(f"Всего тестов: {analysis['total_tests']}")
        print(f"Успешных: {analysis['successful_tests']}")
        print(f"Ошибок: {analysis['failed_tests']}")
        print(f"Среднее время: {analysis['average_processing_time']:.2f}ms")
        
        print("\n📈 ПРОИЗВОДИТЕЛЬНОСТЬ ПО ПРАВИЛАМ:")
        for rule_name, stats in analysis["rules_performance"].items():
            print(f"  {rule_name}:")
            print(f"    Успешность: {stats['success_rate']:.1%}")
            print(f"    Время: {stats['average_time']:.2f}ms")
        
        if analysis["error_patterns"]:
            print("\n❌ ОШИБКИ:")
            for error in analysis["error_patterns"][:5]:  # Показываем первые 5
                print(f"  {error['rule']}: {error['error']}")

async def main():
    """Основная функция для тестирования"""
    
    collector = DeterministicDataCollector()
    
    # Загружаем тестовые случаи
    collector.load_test_cases_from_file("test_cases.json")
    
    # Генерируем тестовые случаи из отчета совещания
    report_text = """
    Дистиллятор: 24 июля
    Маслопресс: 1 августа
    Кофемашина: в течение августа
    Сковороды и кастрюли: на текущей неделе
    Индукционная плита Pro: начало массового производства на следующей неделе
    Уже получено два контейнера с дегидраторами, аэрогрилями и поддонами
    В ближайшие дни ожидается контейнер с аэрофритюрницами (RMA 02) и новыми озонаторами (05)
    Скоро ожидается "лавина" из четырех контейнеров с блендерами
    Из 73 товаров приняли только 25
    Причина — сотрудники склада Wildberries отсканировали не тот штрихкод
    Обновление карточек товаров: Это является приоритетом
    Задача максимум — обновить карточки для ключевых товаров к большой сентябрьской распродаже
    Приоритет будет отдан сезонным товарам: сначала соковыжималки и дегидраторы
    Затем климатическая техника (мойки воздуха, пылесосы)
    Основной упор в работе делается на поиск внешних площадок и авторов
    Была допущена ошибка при обращении в официальную редакцию
    Корректная задача — находить на сайте сторонних авторов
    Идут переговоры о совместном розыгрыше с компанией "Duty Box"
    После посещения VK Fest установлены контакты с ФК "Зенит"
    Фестиваль разочаровал и был оценен как слабая площадка для продвижения
    """
    
    collector.generate_test_cases_from_report(report_text)
    
    # Запускаем тестирование
    results = await collector.run_all_tests()
    
    # Анализируем результаты
    collector.print_summary()
    
    # Сохраняем результаты
    collector.save_results()
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main()) 