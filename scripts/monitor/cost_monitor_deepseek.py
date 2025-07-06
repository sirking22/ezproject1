#!/usr/bin/env python3
"""
Система мониторинга затрат DeepSeek API
Отслеживает расходы и предупреждает о превышении лимитов
"""

import os
import json
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CostRecord:
    """Запись о затратах"""
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    request_id: str
    success: bool
    error: Optional[str] = None

@dataclass
class CostLimits:
    """Лимиты затрат"""
    daily_limit: float = 10.0  # $10 в день
    hourly_limit: float = 2.0  # $2 в час
    request_limit: float = 0.1  # $0.1 за запрос
    warning_threshold: float = 0.8  # 80% от лимита

class DeepSeekCostMonitor:
    """Монитор затрат для DeepSeek API"""
    
    def __init__(self, data_file: str = "deepseek_costs.json"):
        self.data_file = Path(data_file)
        self.costs_file = Path("costs_history.json")
        self.limits = CostLimits()
        
        # Загружаем историю затрат
        self.cost_history: List[CostRecord] = self._load_cost_history()
        
        # Статистика
        self.stats = {
            "total_cost": 0.0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "daily_cost": 0.0,
            "hourly_cost": 0.0
        }
        
        # Обновляем статистику
        self._update_stats()
        
        logger.info(f"💰 Монитор затрат инициализирован. Лимит: ${self.limits.daily_limit}/день")
    
    def _load_cost_history(self) -> List[CostRecord]:
        """Загрузка истории затрат"""
        if self.costs_file.exists():
            try:
                with open(self.costs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [CostRecord(**record) for record in data]
            except Exception as e:
                logger.error(f"Ошибка загрузки истории затрат: {e}")
        return []
    
    def _save_cost_history(self):
        """Сохранение истории затрат"""
        try:
            with open(self.costs_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(record) for record in self.cost_history], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения истории затрат: {e}")
    
    def _update_stats(self):
        """Обновление статистики"""
        now = datetime.now()
        today = now.date()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        # Фильтруем записи по времени
        today_costs = [c for c in self.cost_history if datetime.fromisoformat(c.timestamp).date() == today]
        hour_costs = [c for c in self.cost_history if datetime.fromisoformat(c.timestamp) >= current_hour]
        
        # Обновляем статистику
        self.stats["total_cost"] = sum(c.cost for c in self.cost_history)
        self.stats["total_requests"] = len(self.cost_history)
        self.stats["successful_requests"] = len([c for c in self.cost_history if c.success])
        self.stats["failed_requests"] = len([c for c in self.cost_history if not c.success])
        self.stats["daily_cost"] = sum(c.cost for c in today_costs)
        self.stats["hourly_cost"] = sum(c.cost for c in hour_costs)
    
    def add_cost_record(self, record: CostRecord):
        """Добавление записи о затратах"""
        self.cost_history.append(record)
        self._update_stats()
        self._save_cost_history()
        
        # Проверяем лимиты
        self._check_limits()
    
    def _check_limits(self):
        """Проверка лимитов затрат"""
        daily_usage = self.stats["daily_cost"] / self.limits.daily_limit
        hourly_usage = self.stats["hourly_cost"] / self.limits.hourly_limit
        
        # Предупреждения
        if daily_usage >= self.limits.warning_threshold:
            logger.warning(f"⚠️ Дневной лимит почти исчерпан: ${self.stats['daily_cost']:.2f}/${self.limits.daily_limit:.2f} ({daily_usage:.1%})")
        
        if hourly_usage >= self.limits.warning_threshold:
            logger.warning(f"⚠️ Часовой лимит почти исчерпан: ${self.stats['hourly_cost']:.2f}/${self.limits.hourly_limit:.2f} ({hourly_usage:.1%})")
        
        # Критические превышения
        if daily_usage >= 1.0:
            logger.error(f"🚨 ДНЕВНОЙ ЛИМИТ ПРЕВЫШЕН! ${self.stats['daily_cost']:.2f}/${self.limits.daily_limit:.2f}")
            raise Exception("Превышен дневной лимит затрат!")
        
        if hourly_usage >= 1.0:
            logger.error(f"🚨 ЧАСОВОЙ ЛИМИТ ПРЕВЫШЕН! ${self.stats['hourly_cost']:.2f}/${self.limits.hourly_limit:.2f}")
            raise Exception("Превышен часовой лимит затрат!")
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Получение сводки затрат"""
        return {
            "total_cost": self.stats["total_cost"],
            "daily_cost": self.stats["daily_cost"],
            "hourly_cost": self.stats["hourly_cost"],
            "total_requests": self.stats["total_requests"],
            "success_rate": self.stats["successful_requests"] / max(self.stats["total_requests"], 1),
            "daily_limit_usage": self.stats["daily_cost"] / self.limits.daily_limit,
            "hourly_limit_usage": self.stats["hourly_cost"] / self.limits.hourly_limit,
            "limits": asdict(self.limits)
        }
    
    def print_summary(self):
        """Вывод сводки затрат"""
        summary = self.get_cost_summary()
        
        print("💰 СВОДКА ЗАТРАТ DEEPSEEK API")
        print("=" * 50)
        print(f"📊 Общие затраты: ${summary['total_cost']:.4f}")
        print(f"📅 За сегодня: ${summary['daily_cost']:.4f} ({summary['daily_limit_usage']:.1%} от лимита)")
        print(f"⏰ За час: ${summary['hourly_cost']:.4f} ({summary['hourly_limit_usage']:.1%} от лимита)")
        print(f"📝 Всего запросов: {summary['total_requests']}")
        print(f"✅ Успешность: {summary['success_rate']:.1%}")
        print(f"🎯 Лимиты: ${self.limits.daily_limit}/день, ${self.limits.hourly_limit}/час")
        
        # Предупреждения
        if summary['daily_limit_usage'] >= 0.8:
            print(f"⚠️  ВНИМАНИЕ: Дневной лимит почти исчерпан!")
        if summary['hourly_limit_usage'] >= 0.8:
            print(f"⚠️  ВНИМАНИЕ: Часовой лимит почти исчерпан!")
    
    def get_daily_chart(self) -> str:
        """Генерация ASCII графика дневных затрат"""
        summary = self.get_cost_summary()
        usage = summary['daily_limit_usage']
        
        # Создаем график
        bar_length = 20
        filled_length = int(bar_length * usage)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        return f"[{bar}] {usage:.1%}"

# Глобальный экземпляр монитора
cost_monitor = DeepSeekCostMonitor()

def track_cost(model: str, input_tokens: int, output_tokens: int, cost: float, 
               request_id: str, success: bool = True, error: str = None):
    """Функция для отслеживания затрат"""
    record = CostRecord(
        timestamp=datetime.now().isoformat(),
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        request_id=request_id,
        success=success,
        error=error
    )
    
    cost_monitor.add_cost_record(record)
    return record

async def test_cost_monitoring():
    """Тестирование системы мониторинга затрат"""
    print("🧪 ТЕСТИРОВАНИЕ МОНИТОРИНГА ЗАТРАТ")
    print("=" * 50)
    
    # Симулируем несколько запросов
    test_records = [
        ("deepseek-chat", 100, 50, 0.001, "test_1", True),
        ("deepseek-chat", 200, 100, 0.002, "test_2", True),
        ("deepseek-reasoner", 500, 200, 0.005, "test_3", False, "Timeout"),
        ("deepseek-chat", 150, 75, 0.0015, "test_4", True),
    ]
    
    for record in test_records:
        track_cost(*record)
        print(f"📝 Добавлена запись: {record[0]} - ${record[3]:.4f}")
        time.sleep(0.1)
    
    # Выводим сводку
    print("\n" + "=" * 50)
    cost_monitor.print_summary()
    
    # ASCII график
    print(f"\n📊 Дневные затраты: {cost_monitor.get_daily_chart()}")

def main():
    """Главная функция"""
    print("💰 DEEPSEEK COST MONITOR")
    print("=" * 50)
    
    # Показываем текущую сводку
    cost_monitor.print_summary()
    
    # Тестируем систему
    asyncio.run(test_cost_monitoring())

if __name__ == "__main__":
    main() 