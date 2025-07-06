#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 КОМПЛЕКСНАЯ СИСТЕМА АНАЛИТИКИ TELEGRAM

Лучшие практики метрик для Telegram каналов:
✅ Основные KPI
✅ Engagement метрики  
✅ Рост и ретеншн
✅ Контент-аналитика
✅ Конкурентный анализ
"""

import requests
import os
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional
import statistics

# Настройка логирования
logger = logging.getLogger(__name__)

@dataclass
class TelegramMetrics:
    """Структура метрик Telegram канала"""
    
    # Основные показатели
    subscribers: int = 0
    posts_count: int = 0
    avg_views: float = 0
    total_views: int = 0
    
    # Engagement метрики
    engagement_rate: float = 0  # (лайки + комментарии) / просмотры * 100
    view_rate: float = 0  # просмотры / подписчики * 100
    comment_rate: float = 0  # комментарии / просмотры * 100
    forward_rate: float = 0  # репосты / просмотры * 100
    
    # Рост и активность
    subscriber_growth: int = 0
    subscriber_growth_rate: float = 0  # % рост за период
    posts_frequency: float = 0  # постов в день
    
    # Качество контента
    top_post_views: int = 0
    worst_post_views: int = 0
    content_consistency: float = 0  # стандартное отклонение просмотров
    
    # Сравнительные показатели
    industry_benchmark: float = 0
    competitor_performance: float = 0
    
    # Временные метрики
    peak_activity_hour: str = ""
    best_posting_day: str = ""

class TelegramAnalyticsFramework:
    """Фреймворк аналитики на основе лучших практик"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.platforms_db_id = os.getenv('NOTION_PLATFORMS_DB_ID')
        self.content_db_id = os.getenv('NOTION_CONTENT_PLAN_DB_ID')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        self.headers = {
            'Authorization': f'Bearer {self.notion_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        
        # Бенчмарки индустрии (средние показатели)
        self.industry_benchmarks = {
            'view_rate': 15.0,  # 15% подписчиков смотрят пост
            'engagement_rate': 2.5,  # 2.5% от просмотров
            'posts_per_day': 1.5,  # 1-2 поста в день
            'subscriber_growth_monthly': 5.0  # 5% рост в месяц
        }
    
    def get_comprehensive_metrics(self, channel="rawmid") -> TelegramMetrics:
        """Получает все возможные метрики канала"""
        
        print("📊 РАСЧЕТ КОМПЛЕКСНЫХ МЕТРИК")
        print("=" * 60)
        
        metrics = TelegramMetrics()
        
        # 1. Основные данные канала
        channel_data = self.get_channel_basic_data(channel)
        if channel_data:
            metrics.subscribers = channel_data.get('subscribers', 0)
            print(f"   👥 Подписчики: {metrics.subscribers:,}")
        
        # 2. Данные постов
        posts_data = self.get_posts_analytics(channel)
        if posts_data:
            metrics.posts_count = len(posts_data)
            metrics.total_views = sum(p.get('views', 0) for p in posts_data)
            metrics.avg_views = metrics.total_views / metrics.posts_count if metrics.posts_count > 0 else 0
            
            views_list = [p.get('views', 0) for p in posts_data if p.get('views', 0) > 0]
            if views_list:
                metrics.top_post_views = max(views_list)
                metrics.worst_post_views = min(views_list)
                metrics.content_consistency = statistics.stdev(views_list) if len(views_list) > 1 else 0
            
            print(f"   📝 Постов: {metrics.posts_count}")
            print(f"   👀 Общие просмотры: {metrics.total_views:,}")
            print(f"   📊 Средние просмотры: {metrics.avg_views:,.0f}")
        
        # 3. Расчет ключевых KPI
        metrics = self.calculate_key_kpis(metrics)
        
        # 4. Анализ роста
        metrics = self.analyze_growth_metrics(metrics, channel)
        
        # 5. Контент-аналитика
        metrics = self.analyze_content_performance(metrics, posts_data)
        
        return metrics
    
    def calculate_key_kpis(self, metrics: TelegramMetrics) -> TelegramMetrics:
        """Рассчитывает ключевые KPI"""
        
        print(f"\n🎯 РАСЧЕТ КЛЮЧЕВЫХ KPI")
        print("=" * 40)
        
        # View Rate (охват) - % подписчиков, которые видят посты
        if metrics.subscribers > 0 and metrics.avg_views > 0:
            metrics.view_rate = (metrics.avg_views / metrics.subscribers) * 100
            print(f"   📈 View Rate: {metrics.view_rate:.1f}%")
            
            # Сравнение с бенчмарком
            benchmark_diff = metrics.view_rate - self.industry_benchmarks['view_rate']
            status = "✅ Выше среднего" if benchmark_diff > 0 else "⚠️ Ниже среднего"
            print(f"   📊 vs Бенчмарк ({self.industry_benchmarks['view_rate']}%): {benchmark_diff:+.1f}% {status}")
        
        # Consistency Score (консистентность контента)
        if metrics.avg_views > 0 and metrics.content_consistency > 0:
            consistency_score = 100 - (metrics.content_consistency / metrics.avg_views * 100)
            print(f"   🎯 Консистентность: {consistency_score:.1f}%")
        
        return metrics
    
    def analyze_growth_metrics(self, metrics: TelegramMetrics, channel: str) -> TelegramMetrics:
        """Анализирует метрики роста"""
        
        print(f"\n📈 АНАЛИЗ РОСТА")
        print("=" * 40)
        
        # Здесь можно добавить логику сравнения с историческими данными
        # Пока используем примерные расчеты
        
        # Частота постинга (за последние 30 дней)
        # Предполагаем, что имеем 15 постов за ~10 дней
        estimated_days = 10  # Примерная оценка
        metrics.posts_frequency = metrics.posts_count / estimated_days if estimated_days > 0 else 0
        
        print(f"   📝 Частота: {metrics.posts_frequency:.1f} постов/день")
        
        benchmark_freq = self.industry_benchmarks['posts_per_day']
        if metrics.posts_frequency > benchmark_freq:
            print(f"   ✅ Частота выше рекомендуемой ({benchmark_freq}/день)")
        else:
            print(f"   ⚠️ Можно увеличить частоту постинга (рекомендуемо {benchmark_freq}/день)")
        
        return metrics
    
    def analyze_content_performance(self, metrics: TelegramMetrics, posts_data: List) -> TelegramMetrics:
        """Анализирует эффективность контента"""
        
        print(f"\n📝 АНАЛИЗ КОНТЕНТА")
        print("=" * 40)
        
        if not posts_data:
            return metrics
        
        # Анализ распределения просмотров
        views_list = [p.get('views', 0) for p in posts_data if p.get('views', 0) > 0]
        
        if views_list:
            # Медиана и квартили
            median_views = statistics.median(views_list)
            q75 = statistics.quantiles(views_list, n=4)[2] if len(views_list) >= 4 else max(views_list)
            q25 = statistics.quantiles(views_list, n=4)[0] if len(views_list) >= 4 else min(views_list)
            
            print(f"   📊 Медиана просмотров: {median_views:,.0f}")
            print(f"   🏆 Топ 25% постов: >{q75:,.0f} просмотров")
            print(f"   📉 Низкие 25% постов: <{q25:,.0f} просмотров")
            
            # Процент "вирусных" постов (выше среднего в 1.5 раза)
            viral_threshold = metrics.avg_views * 1.5
            viral_posts = len([v for v in views_list if v > viral_threshold])
            viral_percentage = (viral_posts / len(views_list)) * 100
            
            print(f"   🚀 'Вирусные' посты (>{viral_threshold:,.0f}): {viral_posts} ({viral_percentage:.1f}%)")
        
        return metrics
    
    def get_channel_basic_data(self, channel: str) -> Dict:
        """Получает базовые данные канала"""
        
        try:
            # Используем Bot API
            chat_url = f"https://api.telegram.org/bot{self.bot_token}/getChat"
            count_url = f"https://api.telegram.org/bot{self.bot_token}/getChatMemberCount"
            
            chat_response = requests.get(chat_url, params={'chat_id': f'@{channel}'}, timeout=10)
            count_response = requests.get(count_url, params={'chat_id': f'@{channel}'}, timeout=10)
            
            subscribers = 0
            if count_response.status_code == 200:
                count_data = count_response.json()
                if count_data.get('ok'):
                    subscribers = count_data['result']
            
            return {'subscribers': subscribers}
            
        except Exception as e:
            print(f"   ❌ Ошибка получения базовых данных: {e}")
            return {}
    
    def get_posts_analytics(self, channel: str) -> List[Dict]:
        """Получает аналитику постов"""
        
        try:
            url = f"https://t.me/s/{channel}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                posts_elements = soup.find_all('div', class_='tgme_widget_message')
                
                posts_data = []
                for post_elem in posts_elements:
                    views_elem = post_elem.find('span', class_='tgme_widget_message_views')
                    if views_elem:
                        views_text = views_elem.text.strip()
                        views = self.convert_count_to_number(views_text)
                        
                        # Получаем дату
                        date_elem = post_elem.find('time', class_='datetime')
                        post_date = None
                        if date_elem:
                            datetime_attr = date_elem.get('datetime', '')
                            if datetime_attr:
                                try:
                                    post_date = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                                except:
                                    pass
                        
                        posts_data.append({
                            'views': views,
                            'date': post_date,
                            'url': f"https://t.me/{channel}/{post_elem.get('data-post', '').split('/')[-1]}"
                        })
                
                return posts_data
            
            return []
            
        except Exception as e:
            print(f"   ❌ Ошибка получения постов: {e}")
            return []
    
    def convert_count_to_number(self, count_str: str) -> int:
        """Конвертирует строку счетчика в число"""
        
        if not count_str:
            return 0
        
        count_str = str(count_str).replace(' ', '').replace(',', '').lower()
        
        import re
        match = re.search(r'([\d.,]+[km]?)', count_str)
        if not match:
            return 0
        
        number_str = match.group(1)
        
        try:
            if 'k' in number_str:
                return int(float(number_str.replace('k', '')) * 1000)
            elif 'm' in number_str:
                return int(float(number_str.replace('m', '')) * 1000000)
            else:
                return int(float(number_str))
        except:
            return 0
    
    def generate_recommendations(self, metrics: TelegramMetrics) -> List[str]:
        """Генерирует рекомендации на основе метрик"""
        
        recommendations = []
        
        # Анализ View Rate
        if metrics.view_rate < self.industry_benchmarks['view_rate']:
            recommendations.append(
                f"📈 Улучшить охват: текущий {metrics.view_rate:.1f}% < {self.industry_benchmarks['view_rate']}% (бенчмарк)"
            )
            recommendations.append("   • Оптимизировать время публикации")
            recommendations.append("   • Улучшить заголовки и превью")
            recommendations.append("   • Добавить интерактив (опросы, вопросы)")
        
        # Анализ частоты постинга
        if metrics.posts_frequency < self.industry_benchmarks['posts_per_day']:
            recommendations.append(
                f"📝 Увеличить частоту: {metrics.posts_frequency:.1f} < {self.industry_benchmarks['posts_per_day']} постов/день"
            )
            recommendations.append("   • Создать контент-календарь")
            recommendations.append("   • Добавить пользовательский контент (UGC)")
        
        # Анализ консистентности
        if metrics.content_consistency > metrics.avg_views * 0.5:  # Высокое отклонение
            recommendations.append("🎯 Улучшить консистентность контента")
            recommendations.append("   • Анализировать топ-посты и повторять форматы")
            recommendations.append("   • A/B тестировать разные типы контента")
        
        # Общие рекомендации
        if metrics.subscribers < 10000:
            recommendations.append("👥 Стратегия роста до 10K подписчиков:")
            recommendations.append("   • Кросс-промо с другими каналами")
            recommendations.append("   • Конкурсы и розыгрыши")
            recommendations.append("   • Реферальная программа")
        
        return recommendations
    
    def create_analytics_report(self, metrics: TelegramMetrics) -> str:
        """Создает аналитический отчет"""
        
        report = f"""
📊 АНАЛИТИЧЕСКИЙ ОТЧЕТ TELEGRAM
{'='*50}
📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}
📱 Канал: @rawmid

🎯 КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ:
   👥 Подписчики: {metrics.subscribers:,}
   📝 Постов: {metrics.posts_count}
   👀 Общие просмотры: {metrics.total_views:,}
   📊 Средние просмотры: {metrics.avg_views:,.0f}

📈 PERFORMANCE МЕТРИКИ:
   🎯 View Rate: {metrics.view_rate:.1f}% (охват подписчиков)
   📝 Частота постинга: {metrics.posts_frequency:.1f} постов/день
   🏆 Лучший пост: {metrics.top_post_views:,} просмотров
   📉 Худший пост: {metrics.worst_post_views:,} просмотров

🏆 СРАВНЕНИЕ С БЕНЧМАРКАМИ:
   📊 View Rate: {metrics.view_rate:.1f}% vs {self.industry_benchmarks['view_rate']}% (индустрия)
   📝 Частота: {metrics.posts_frequency:.1f} vs {self.industry_benchmarks['posts_per_day']} (рекомендуемо)

🎯 РЕКОМЕНДАЦИИ:
"""
        
        recommendations = self.generate_recommendations(metrics)
        for rec in recommendations:
            report += f"{rec}\n"
        
        return report

def main():
    """Главная функция - демонстрация системы аналитики"""
    
    print("🚀 ЗАПУСК КОМПЛЕКСНОЙ АНАЛИТИКИ TELEGRAM")
    print("=" * 80)
    
    analyzer = TelegramAnalyticsFramework()
    
    # Получаем метрики
    metrics = analyzer.get_comprehensive_metrics("rawmid")
    
    # Генерируем отчет
    report = analyzer.create_analytics_report(metrics)
    print(report)
    
    # Сохраняем отчет
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"telegram_analytics_report_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Отчет сохранен: {filename}")
    
    # Предлагаем автоматизацию
    print(f"\n🔄 СЛЕДУЮЩИЕ ШАГИ:")
    print(f"   1. Настроить ежедневный запуск аналитики")
    print(f"   2. Создать дашборд в Notion")
    print(f"   3. Настроить алерты по KPI")
    print(f"   4. Добавить конкурентный анализ")

if __name__ == "__main__":
    main() 