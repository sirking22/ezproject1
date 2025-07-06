#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 УНИВЕРСАЛЬНЫЕ МЕТРИКИ ДЛЯ ВСЕХ СОЦИАЛЬНЫХ ПЛАТФОРМ

Система KPI и алертов для:
✅ Telegram, Instagram, YouTube, TikTok, Facebook, Twitter, VK
✅ Унифицированные показатели
✅ Автоматические алерты
✅ Обновление Notion дашборда
"""

import requests
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from dotenv import load_dotenv

# Настройка логирования
logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class UniversalMetrics:
    """Универсальная структура метрик для всех платформ"""
    
    # Основные показатели
    platform: str = ""
    followers: int = 0
    posts_count: int = 0
    total_reach: int = 0
    avg_engagement: float = 0
    
    # Универсальные KPI
    growth_rate: float = 0          # % рост подписчиков за месяц
    engagement_rate: float = 0      # (лайки + комментарии + шейры) / подписчики * 100
    reach_rate: float = 0           # просмотры / подписчики * 100
    posting_frequency: float = 0    # постов в неделю
    
    # Качественные показатели
    content_score: int = 0          # 1-10 оценка качества контента
    consistency_score: float = 0    # стабильность показателей
    trend_direction: str = "stable" # growing, stable, declining
    
    # Сравнительные метрики
    vs_industry: float = 0          # % отклонение от индустрии
    vs_competitors: float = 0       # % vs конкуренты
    platform_rank: str = "medium"  # low, medium, high, excellent
    
    # Бизнес-метрики
    conversion_rate: float = 0      # подписчики → клиенты
    cpm: float = 0                  # стоимость за 1000 показов
    roi: float = 0                  # возврат инвестиций

class UniversalSocialAnalytics:
    """Универсальная аналитика для всех социальных платформ"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.platforms_db_id = os.getenv('NOTION_PLATFORMS_DB_ID')
        
        self.headers = {
            'Authorization': f'Bearer {self.notion_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        
        # Индустриальные бенчмарки по платформам
        self.benchmarks = {
            'telegram': {
                'engagement_rate': 2.5,
                'reach_rate': 15.0,
                'posts_per_week': 10,
                'growth_rate_monthly': 5.0
            },
            'instagram': {
                'engagement_rate': 3.5,
                'reach_rate': 25.0,
                'posts_per_week': 7,
                'growth_rate_monthly': 8.0
            },
            'youtube': {
                'engagement_rate': 4.0,
                'reach_rate': 30.0,
                'posts_per_week': 3,
                'growth_rate_monthly': 10.0
            },
            'tiktok': {
                'engagement_rate': 5.0,
                'reach_rate': 35.0,
                'posts_per_week': 14,
                'growth_rate_monthly': 15.0
            },
            'facebook': {
                'engagement_rate': 1.5,
                'reach_rate': 8.0,
                'posts_per_week': 5,
                'growth_rate_monthly': 3.0
            },
            'twitter': {
                'engagement_rate': 2.0,
                'reach_rate': 12.0,
                'posts_per_week': 21,
                'growth_rate_monthly': 4.0
            },
            'vk': {
                'engagement_rate': 2.8,
                'reach_rate': 18.0,
                'posts_per_week': 7,
                'growth_rate_monthly': 6.0
            }
        }
        
        # Пороги для алертов (универсальные)
        self.alert_thresholds = {
            'critical_engagement_drop': -50,    # % падение engagement
            'critical_reach_drop': -30,         # % падение охвата
            'low_posting_frequency': 0.5,       # < 0.5 постов/неделю
            'negative_growth': -2,              # % убыль подписчиков
            'excellent_performance': 150,       # % превышение бенчмарка
        }
    
    def analyze_all_platforms(self) -> Dict[str, UniversalMetrics]:
        """Анализирует все платформы в дашборде"""
        
        print("🔄 АНАЛИЗ ВСЕХ ПЛАТФОРМ")
        print("=" * 60)
        
        platforms_data = self.get_notion_platforms()
        results = {}
        
        for platform_data in platforms_data:
            platform_name = platform_data.get('name', '').lower()
            
            if platform_name in self.benchmarks:
                metrics = self.calculate_universal_metrics(platform_data, platform_name)
                results[platform_name] = metrics
                
                print(f"\n📱 {platform_name.upper()}:")
                print(f"   👥 Подписчики: {metrics.followers:,}")
                print(f"   📊 Engagement Rate: {metrics.engagement_rate:.1f}%")
                print(f"   📈 Рейтинг: {metrics.platform_rank}")
        
        return results
    
    def calculate_universal_metrics(self, platform_data: Dict, platform_name: str) -> UniversalMetrics:
        """Рассчитывает универсальные метрики для платформы"""
        
        metrics = UniversalMetrics()
        metrics.platform = platform_name
        
        # Базовые данные
        metrics.followers = platform_data.get('followers', 0)
        metrics.posts_count = platform_data.get('posts', 0)
        
        # Рассчитываем метрики на основе доступных данных
        benchmark = self.benchmarks[platform_name]
        
        # Примерные расчеты (в реальности нужны API данные)
        if metrics.followers > 0:
            # Engagement Rate - примерная оценка
            if platform_name == 'telegram':
                metrics.engagement_rate = 2.5  # Из наших данных
                metrics.reach_rate = 17.3      # Из наших данных
            else:
                # Для остальных - примерная оценка по размеру аудитории
                follower_factor = min(metrics.followers / 10000, 2.0)
                metrics.engagement_rate = benchmark['engagement_rate'] * (1 + follower_factor * 0.1)
                metrics.reach_rate = benchmark['reach_rate'] * (1 + follower_factor * 0.05)
        
        # Оценка качества относительно бенчмарка
        engagement_vs_benchmark = (metrics.engagement_rate / benchmark['engagement_rate']) * 100
        metrics.vs_industry = engagement_vs_benchmark - 100
        
        # Определяем рейтинг платформы
        if engagement_vs_benchmark >= 150:
            metrics.platform_rank = "excellent"
            metrics.content_score = 9
        elif engagement_vs_benchmark >= 120:
            metrics.platform_rank = "high"
            metrics.content_score = 7
        elif engagement_vs_benchmark >= 80:
            metrics.platform_rank = "medium"
            metrics.content_score = 5
        else:
            metrics.platform_rank = "low"
            metrics.content_score = 3
        
        return metrics
    
    def check_universal_alerts(self, all_metrics: Dict[str, UniversalMetrics]) -> List[Dict]:
        """Проверяет алерты по всем платформам"""
        
        print(f"\n🚨 ПРОВЕРКА АЛЕРТОВ ПО ВСЕМ ПЛАТФОРМАМ")
        print("=" * 50)
        
        alerts = []
        
        for platform, metrics in all_metrics.items():
            platform_alerts = self.check_platform_alerts(platform, metrics)
            alerts.extend(platform_alerts)
        
        # Межплатформенные алерты
        cross_platform_alerts = self.check_cross_platform_alerts(all_metrics)
        alerts.extend(cross_platform_alerts)
        
        if alerts:
            print(f"   🚨 Найдено {len(alerts)} алертов")
            for alert in alerts:
                print(f"   {alert['message']}")
        else:
            print("   ✅ Все платформы в норме")
        
        return alerts
    
    def check_platform_alerts(self, platform: str, metrics: UniversalMetrics) -> List[Dict]:
        """Проверяет алерты для конкретной платформы"""
        
        alerts = []
        
        # 1. Отличная производительность
        if metrics.vs_industry > self.alert_thresholds['excellent_performance']:
            alerts.append({
                'type': 'success',
                'platform': platform,
                'metric': 'performance',
                'message': f"🚀 {platform.upper()}: Отличные результаты! +{metrics.vs_industry:.0f}% vs индустрии",
                'action': 'Анализировать и тиражировать успешные практики'
            })
        
        # 2. Низкий engagement
        benchmark = self.benchmarks[platform]['engagement_rate']
        if metrics.engagement_rate < benchmark * 0.5:  # Меньше 50% от бенчмарка
            alerts.append({
                'type': 'warning',
                'platform': platform,
                'metric': 'engagement',
                'message': f"⚠️ {platform.upper()}: Низкий engagement {metrics.engagement_rate:.1f}% < {benchmark:.1f}%",
                'action': 'Пересмотреть контент-стратегию'
            })
        
        # 3. Малая аудитория при хорошем engagement
        if metrics.followers < 5000 and metrics.engagement_rate > benchmark * 1.2:
            alerts.append({
                'type': 'info',
                'platform': platform,
                'metric': 'growth_opportunity',
                'message': f"💡 {platform.upper()}: Хороший engagement при малой аудитории - потенциал роста!",
                'action': 'Инвестировать в продвижение этой платформы'
            })
        
        # 4. Большая аудитория при низком engagement
        if metrics.followers > 20000 and metrics.engagement_rate < benchmark * 0.8:
            alerts.append({
                'type': 'critical',
                'platform': platform,
                'metric': 'audience_quality',
                'message': f"🚨 {platform.upper()}: Большая аудитория ({metrics.followers:,}) но низкий engagement",
                'action': 'Срочно улучшать качество контента и активность'
            })
        
        return alerts
    
    def check_cross_platform_alerts(self, all_metrics: Dict[str, UniversalMetrics]) -> List[Dict]:
        """Проверяет межплатформенные алерты"""
        
        alerts = []
        
        # Находим лучшую и худшую платформы по engagement
        if len(all_metrics) >= 2:
            platforms_by_engagement = sorted(
                all_metrics.items(), 
                key=lambda x: x[1].engagement_rate, 
                reverse=True
            )
            
            best_platform = platforms_by_engagement[0]
            worst_platform = platforms_by_engagement[-1]
            
            # Большая разница между платформами
            engagement_gap = best_platform[1].engagement_rate - worst_platform[1].engagement_rate
            
            if engagement_gap > 3.0:  # Разница больше 3%
                alerts.append({
                    'type': 'info',
                    'platform': 'cross_platform',
                    'metric': 'platform_gap',
                    'message': f"📊 Большая разница: {best_platform[0].upper()} ({best_platform[1].engagement_rate:.1f}%) vs {worst_platform[0].upper()} ({worst_platform[1].engagement_rate:.1f}%)",
                    'action': f'Перенести успешные практики с {best_platform[0]} на {worst_platform[0]}'
                })
        
        # Общий размер аудитории
        total_followers = sum(m.followers for m in all_metrics.values())
        
        if total_followers > 100000:
            alerts.append({
                'type': 'success',
                'platform': 'total',
                'metric': 'reach',
                'message': f"🎉 Общий охват: {total_followers:,} подписчиков!",
                'action': 'Использовать для кросс-промо и синергии'
            })
        
        return alerts
    
    def update_notion_universal_metrics(self, all_metrics: Dict[str, UniversalMetrics]) -> bool:
        """Обновляет универсальные метрики в Notion"""
        
        print(f"\n📝 ОБНОВЛЕНИЕ NOTION С УНИВЕРСАЛЬНЫМИ МЕТРИКАМИ")
        print("=" * 50)
        
        try:
            for platform_name, metrics in all_metrics.items():
                success = self.update_platform_in_notion(platform_name, metrics)
                if success:
                    print(f"   ✅ {platform_name.upper()} обновлен")
                else:
                    print(f"   ❌ Ошибка обновления {platform_name.upper()}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка обновления Notion: {e}")
            return False
    
    def update_platform_in_notion(self, platform_name: str, metrics: UniversalMetrics) -> bool:
        """Обновляет конкретную платформу в Notion"""
        
        try:
            # Ищем платформу
            platforms_query = {
                "filter": {
                    "property": "Platforms",
                    "title": {
                        "contains": platform_name.capitalize()
                    }
                }
            }
            
            query_url = f"https://api.notion.so/v1/databases/{self.platforms_db_id}/query"
            try:
                response = requests.post(query_url, headers=self.headers, json=platforms_query)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Error in POST request: {e}")
                return False
            
            data = response.json()
            if data['results']:
                page_id = data['results'][0]['id']
                
                # Подготавливаем данные для обновления
                update_data = {
                    "properties": {
                        "Followers": {"number": metrics.followers},
                        "Engagement Rate": {"number": metrics.engagement_rate},
                        "Platform Rank": {
                            "select": {
                                "name": metrics.platform_rank.capitalize()
                            }
                        },
                        "vs Industry": {"number": metrics.vs_industry},
                        "Content Score": {"number": metrics.content_score},
                        "Last Updated": {
                            "date": {
                                "start": datetime.now().isoformat()
                            }
                        }
                    }
                }
                
                update_url = f"https://api.notion.so/v1/pages/{page_id}"
                try:
                    update_response = requests.patch(update_url, headers=self.headers, json=update_data)
                    update_response.raise_for_status()
                    return True
                except requests.RequestException as e:
                    logger.error(f"Error in PATCH request: {e}")
                    return False
            
            return False
        
        except Exception as e:
            logger.error(f"Ошибка обновления {platform_name}: {e}")
            return False
    
    def get_notion_platforms(self) -> List[Dict]:
        """Получает данные платформ из Notion"""
        
        try:
            query_url = f"https://api.notion.so/v1/databases/{self.platforms_db_id}/query"
            try:
                response = requests.post(query_url, headers=self.headers)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Error in POST request: {e}")
                return []
            
            data = response.json()
            platforms = []
            
            for result in data['results']:
                props = result['properties']
                
                platform = {
                    'name': '',
                    'followers': 0,
                    'posts': 0,
                    'page_id': result['id']
                }
                
                # Извлекаем название платформы
                if 'Platforms' in props and props['Platforms']['title']:
                    platform['name'] = props['Platforms']['title'][0]['text']['content']
                
                # Извлекаем подписчиков
                if 'Followers' in props and props['Followers']['number']:
                    platform['followers'] = props['Followers']['number']
                
                # Извлекаем количество постов
                if 'Posts' in props and props['Posts']['number']:
                    platform['posts'] = props['Posts']['number']
                
                platforms.append(platform)
            
            return platforms
            
        except Exception as e:
            logger.error(f"Ошибка получения платформ: {e}")
            return []
    
    def generate_universal_report(self, all_metrics: Dict[str, UniversalMetrics], alerts: List[Dict]) -> str:
        """Генерирует универсальный отчет по всем платформам"""
        
        total_followers = sum(m.followers for m in all_metrics.values())
        avg_engagement = sum(m.engagement_rate for m in all_metrics.values()) / len(all_metrics)
        
        # Топ платформы
        top_by_followers = max(all_metrics.items(), key=lambda x: x[1].followers)
        top_by_engagement = max(all_metrics.items(), key=lambda x: x[1].engagement_rate)
        
        report = f"""
📊 УНИВЕРСАЛЬНЫЙ ОТЧЕТ ПО ВСЕМ ПЛАТФОРМАМ
{'='*60}
📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}

🎯 ОБЩИЕ ПОКАЗАТЕЛИ:
   👥 Общий охват: {total_followers:,} подписчиков
   📊 Средний Engagement: {avg_engagement:.1f}%
   📱 Активных платформ: {len(all_metrics)}

🏆 ЛИДЕРЫ:
   👥 По аудитории: {top_by_followers[0].upper()} ({top_by_followers[1].followers:,})
   📊 По engagement: {top_by_engagement[0].upper()} ({top_by_engagement[1].engagement_rate:.1f}%)

📈 ДЕТАЛИЗАЦИЯ ПО ПЛАТФОРМАМ:
"""
        
        for platform, metrics in all_metrics.items():
            status_icon = {
                'excellent': '🔥',
                'high': '✅', 
                'medium': '📊',
                'low': '⚠️'
            }.get(metrics.platform_rank, '📊')
            
            report += f"""
   {status_icon} {platform.upper()}:
      👥 {metrics.followers:,} подписчиков
      📊 {metrics.engagement_rate:.1f}% engagement
      🎯 {metrics.platform_rank} рейтинг
      📈 {metrics.vs_industry:+.0f}% vs индустрии
"""
        
        if alerts:
            report += f"\n🚨 АЛЕРТЫ И РЕКОМЕНДАЦИИ ({len(alerts)}):\n"
            for alert in alerts:
                icon = {"critical": "🚨", "warning": "⚠️", "info": "💡", "success": "🚀"}
                report += f"   {icon.get(alert['type'], '📊')} {alert['message']}\n"
        
        # Стратегические рекомендации
        report += f"\n💡 СТРАТЕГИЧЕСКИЕ РЕКОМЕНДАЦИИ:\n"
        
        # На основе анализа данных
        if total_followers < 50000:
            report += "   📈 Фокус на рост аудитории - потенциал большой\n"
        
        if avg_engagement > 3.0:
            report += "   🚀 Отличный engagement - масштабировать успешные форматы\n"
        elif avg_engagement < 2.0:
            report += "   🎯 Низкий engagement - пересмотреть контент-стратегию\n"
        
        # Рекомендации по платформам
        low_performers = [p for p, m in all_metrics.items() if m.platform_rank == 'low']
        if low_performers:
            report += f"   ⚠️ Проблемные платформы: {', '.join(p.upper() for p in low_performers)}\n"
        
        excellent_performers = [p for p, m in all_metrics.items() if m.platform_rank == 'excellent']
        if excellent_performers:
            report += f"   🏆 Звездные платформы: {', '.join(p.upper() for p in excellent_performers)} - тиражировать опыт\n"
        
        return report

def main():
    """Главная функция - анализ всех платформ"""
    
    print("🚀 УНИВЕРСАЛЬНАЯ АНАЛИТИКА ВСЕХ СОЦИАЛЬНЫХ ПЛАТФОРМ")
    print("=" * 80)
    
    analyzer = UniversalSocialAnalytics()
    
    # 1. Анализируем все платформы
    all_metrics = analyzer.analyze_all_platforms()
    
    # 2. Проверяем алерты
    alerts = analyzer.check_universal_alerts(all_metrics)
    
    # 3. Обновляем Notion
    analyzer.update_notion_universal_metrics(all_metrics)
    
    # 4. Генерируем отчет
    report = analyzer.generate_universal_report(all_metrics, alerts)
    print(report)
    
    # 5. Сохраняем отчет
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"universal_social_report_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Отчет сохранен: {filename}")

if __name__ == "__main__":
    main() 