import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import os
from pathlib import Path

@dataclass
class PerformanceMetric:
    """Метрика производительности"""
    timestamp: str
    operation: str
    duration: float
    model_used: str
    tokens_used: int
    cost: float
    success: bool
    error: Optional[str] = None

class PerformanceMonitor:
    """Мониторинг производительности системы"""
    
    def __init__(self, log_file: str = "performance_log.json"):
        self.log_file = Path(log_file)
        self.metrics: List[PerformanceMetric] = []
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Загружаем существующие метрики
        self.load_metrics()
    
    def load_metrics(self):
        """Загружает метрики из файла"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics = [PerformanceMetric(**metric) for metric in data]
            except Exception as e:
                print(f"Ошибка загрузки метрик: {e}")
    
    def save_metrics(self):
        """Сохраняет метрики в файл"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(metric) for metric in self.metrics], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения метрик: {e}")
    
    def add_metric(self, operation: str, duration: float, model_used: str, 
                  tokens_used: int, cost: float, success: bool, error: str = None):
        """Добавляет новую метрику"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            duration=duration,
            model_used=model_used,
            tokens_used=tokens_used,
            cost=cost,
            success=success,
            error=error
        )
        
        self.metrics.append(metric)
        
        # Сохраняем каждые 10 метрик
        if len(self.metrics) % 10 == 0:
            self.save_metrics()
    
    def get_performance_stats(self, days: int = 7) -> Dict[str, Any]:
        """Получает статистику производительности"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_metrics = [
            m for m in self.metrics 
            if datetime.fromisoformat(m.timestamp) > cutoff_date
        ]
        
        if not recent_metrics:
            return {"error": "Нет данных за указанный период"}
        
        # Общая статистика
        total_operations = len(recent_metrics)
        successful_operations = len([m for m in recent_metrics if m.success])
        total_duration = sum(m.duration for m in recent_metrics)
        total_tokens = sum(m.tokens_used for m in recent_metrics)
        total_cost = sum(m.cost for m in recent_metrics)
        
        # Статистика по моделям
        model_stats = {}
        for metric in recent_metrics:
            model = metric.model_used
            if model not in model_stats:
                model_stats[model] = {
                    "operations": 0,
                    "total_tokens": 0,
                    "total_cost": 0,
                    "avg_duration": 0,
                    "success_rate": 0
                }
            
            model_stats[model]["operations"] += 1
            model_stats[model]["total_tokens"] += metric.tokens_used
            model_stats[model]["total_cost"] += metric.cost
        
        # Вычисляем средние значения
        for model in model_stats:
            model_metrics = [m for m in recent_metrics if m.model_used == model]
            model_stats[model]["avg_duration"] = sum(m.duration for m in model_metrics) / len(model_metrics)
            model_stats[model]["success_rate"] = len([m for m in model_metrics if m.success]) / len(model_metrics)
        
        return {
            "period_days": days,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
            "avg_duration": total_duration / total_operations if total_operations > 0 else 0,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "model_stats": model_stats,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }
    
    def print_performance_report(self, days: int = 7):
        """Выводит отчёт о производительности"""
        stats = self.get_performance_stats(days)
        
        if "error" in stats:
            print(f"❌ {stats['error']}")
            return
        
        print(f"\n📊 ОТЧЁТ О ПРОИЗВОДИТЕЛЬНОСТИ (за {days} дней)")
        print("=" * 60)
        
        print(f"🔢 Общие операции: {stats['total_operations']}")
        print(f"✅ Успешные операции: {stats['successful_operations']}")
        print(f"📈 Успешность: {stats['success_rate']:.1%}")
        print(f"⏱️  Среднее время: {stats['avg_duration']:.2f}с")
        print(f"📝 Общее токенов: {stats['total_tokens']:,}")
        print(f"💰 Общая стоимость: ${stats['total_cost']:.6f}")
        print(f"🎯 Кэш-хиты: {stats['cache_hits']}")
        print(f"❌ Кэш-промахи: {stats['cache_misses']}")
        print(f"📊 Эффективность кэша: {stats['cache_hit_rate']:.1%}")
        
        print(f"\n🏢 СТАТИСТИКА ПО МОДЕЛЯМ:")
        for model, model_stats in stats['model_stats'].items():
            print(f"\n  📝 {model}:")
            print(f"    Операции: {model_stats['operations']}")
            print(f"    Токены: {model_stats['total_tokens']:,}")
            print(f"    Стоимость: ${model_stats['total_cost']:.6f}")
            print(f"    Среднее время: {model_stats['avg_duration']:.2f}с")
            print(f"    Успешность: {model_stats['success_rate']:.1%}")
    
    def get_optimization_recommendations(self) -> List[str]:
        """Получает рекомендации по оптимизации"""
        stats = self.get_performance_stats(7)
        recommendations = []
        
        if "error" in stats:
            return ["Недостаточно данных для анализа"]
        
        # Анализ успешности
        if stats['success_rate'] < 0.9:
            recommendations.append("⚠️  Низкая успешность операций - проверьте стабильность API")
        
        # Анализ времени ответа
        if stats['avg_duration'] > 5.0:
            recommendations.append("🐌 Медленные ответы - рассмотрите более быстрые модели")
        
        # Анализ стоимости
        if stats['total_cost'] > 1.0:
            recommendations.append("💰 Высокая стоимость - используйте более дешёвые модели для простых задач")
        
        # Анализ кэша
        if stats['cache_hit_rate'] < 0.3:
            recommendations.append("💾 Низкая эффективность кэша - увеличьте кэширование")
        
        # Анализ по моделям
        for model, model_stats in stats['model_stats'].items():
            if model_stats['avg_duration'] > 3.0:
                recommendations.append(f"🐌 Модель {model} медленная - рассмотрите альтернативы")
            
            if model_stats['total_cost'] > 0.5:
                recommendations.append(f"💰 Модель {model} дорогая - используйте для сложных задач только")
        
        if not recommendations:
            recommendations.append("✅ Система работает оптимально!")
        
        return recommendations

class CacheManager:
    """Управление кэшем для оптимизации"""
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.cache: Dict[str, Dict] = {}
        self.access_times: Dict[str, float] = {}
    
    def _cleanup_expired(self):
        """Удаляет просроченные записи"""
        current_time = time.time()
        expired_keys = [
            key for key, access_time in self.access_times.items()
            if current_time - access_time > self.ttl_hours * 3600
        ]
        
        for key in expired_keys:
            del self.cache[key]
            del self.access_times[key]
    
    def _evict_lru(self):
        """Удаляет наименее используемые записи"""
        if len(self.cache) >= self.max_size:
            # Находим самую старую запись
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
    
    def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша"""
        self._cleanup_expired()
        
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]['value']
        
        return None
    
    def set(self, key: str, value: Any):
        """Сохраняет значение в кэш"""
        self._cleanup_expired()
        self._evict_lru()
        
        self.cache[key] = {
            'value': value,
            'created_at': time.time()
        }
        self.access_times[key] = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получает статистику кэша"""
        self._cleanup_expired()
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size if self.max_size > 0 else 0,
            "ttl_hours": self.ttl_hours
        }

# Глобальные экземпляры
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager() 