#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ЕЖЕДНЕВНЫЙ МОНИТОРИНГ TELEGRAM КАНАЛА

Система автоматических алертов и обновления дашборда:
✅ Ежедневная аналитика
✅ Алерты по KPI  
✅ Обновление Notion
✅ Еженедельные отчеты
"""

import requests
import logging

logger = logging.getLogger(__name__)
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class TelegramDailyMonitor:
    """Система ежедневного мониторинга Telegram канала"""
    
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
        
        # KPI Thresholds для алертов
        self.kpi_thresholds = {
            'view_rate_min': 12.0,        # Критический минимум
            'view_rate_target': 15.0,     # Целевой показатель
            'viral_post_threshold': 1500,  # "Вирусный" пост
            'low_performance_threshold': 500,  # Низкая производительность
            'subscriber_growth_weekly': 50,    # Мин. рост в неделю
        }
        
        # История для трендового анализа
        self.history_file = 'telegram_daily_history.json'
    
    def run_daily_monitoring(self, channel="rawmid") -> Dict:
        """Основная функция ежедневного мониторинга"""
        
        print("🔄 ЗАПУСК ЕЖЕДНЕВНОГО МОНИТОРИНГА")
        print("=" * 50)
        
        # 1. Собираем текущие метрики
        current_metrics = self.collect_current_metrics(channel)
        
        # 2. Сравниваем с историей
        trend_analysis = self.analyze_trends(current_metrics)
        
        # 3. Проверяем алерты
        alerts = self.check_alerts(current_metrics, trend_analysis)
        
        # 4. Обновляем Notion
        self.update_notion_dashboard(current_metrics)
        
        # 5. Сохраняем историю
        self.save_daily_history(current_metrics)
        
        # 6. Генерируем отчет
        daily_report = self.generate_daily_report(current_metrics, trend_analysis, alerts)
        
        # 7. Отправляем алерты при необходимости
        if alerts:
            self.send_alerts(alerts, daily_report)
        
        print("✅ ЕЖЕДНЕВНЫЙ МОНИТОРИНГ ЗАВЕРШЕН")
        return {
            'metrics': current_metrics,
            'trends': trend_analysis,
            'alerts': alerts,
            'report': daily_report
        }
    
    def collect_current_metrics(self, channel: str) -> Dict:
        """Собирает текущие метрики канала"""
        
        print("📊 Сбор метрик...")
        
        metrics = {
            'date': datetime.now().isoformat(),
            'subscribers': 0,
            'posts_today': 0,
            'total_posts': 0,
            'avg_views': 0,
            'today_best_post': 0,
            'view_rate': 0,
            'new_posts_performance': []
        }
        
        try:
            # Подписчики
            count_url = f"https://api.telegram.org/bot{self.bot_token}/getChatMemberCount"
            count_try:
        response = requests.get(count_url, params={'chat_id': f'@{channel}'}, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {{e}}")
        return None
    
    response
            
            if count_response.status_code == 200:
                count_data = count_response.json()
                if count_data.get('ok'):
                    metrics['subscribers'] = count_data['result']
                    print(f"   👥 Подписчики: {metrics['subscribers']:,}")
            
            # Данные постов
            posts_data = self.get_recent_posts(channel)
            if posts_data:
                # Общая статистика
                metrics['total_posts'] = len(posts_data)
                total_views = sum(p.get('views', 0) for p in posts_data)
                metrics['avg_views'] = total_views / len(posts_data) if len(posts_data) > 0 else 0
                
                # Посты за сегодня
                today = datetime.now().date()
                today_posts = [p for p in posts_data if p.get('date') and p['date'].date() == today]
                metrics['posts_today'] = len(today_posts)
                
                if today_posts:
                    metrics['today_best_post'] = max(p.get('views', 0) for p in today_posts)
                    metrics['new_posts_performance'] = [
                        {'views': p.get('views', 0), 'url': p.get('url', '')} 
                        for p in today_posts
                    ]
                
                # View Rate
                if metrics['subscribers'] > 0 and metrics['avg_views'] > 0:
                    metrics['view_rate'] = (metrics['avg_views'] / metrics['subscribers']) * 100
                
                print(f"   📝 Всего постов: {metrics['total_posts']}")
                print(f"   📅 Постов сегодня: {metrics['posts_today']}")
                print(f"   📊 Средние просмотры: {metrics['avg_views']:.0f}")
                print(f"   🎯 View Rate: {metrics['view_rate']:.1f}%")
        
        except Exception as e:
            print(f"   ❌ Ошибка сбора метрик: {e}")
        
        return metrics
    
    def analyze_trends(self, current_metrics: Dict) -> Dict:
        """Анализирует тренды на основе истории"""
        
        print("📈 Анализ трендов...")
        
        trends = {
            'subscriber_change': 0,
            'view_rate_change': 0,
            'performance_trend': 'stable',
            'weekly_growth': 0,
            'recommendation': ''
        }
        
        try:
            # Загружаем историю
            history = self.load_history()
            
            if len(history) > 1:
                yesterday = history[-1] if history else {}
                week_ago = history[-7] if len(history) >= 7 else {}
                
                # Изменение подписчиков
                if yesterday.get('subscribers'):
                    trends['subscriber_change'] = current_metrics['subscribers'] - yesterday['subscribers']
                
                # Изменение View Rate
                if yesterday.get('view_rate'):
                    trends['view_rate_change'] = current_metrics['view_rate'] - yesterday['view_rate']
                
                # Недельный рост
                if week_ago.get('subscribers'):
                    trends['weekly_growth'] = current_metrics['subscribers'] - week_ago['subscribers']
                
                # Общий тренд производительности
                recent_view_rates = [d.get('view_rate', 0) for d in history[-7:] if d.get('view_rate')]
                if len(recent_view_rates) >= 3:
                    if recent_view_rates[-1] > recent_view_rates[0]:
                        trends['performance_trend'] = 'improving'
                    elif recent_view_rates[-1] < recent_view_rates[0]:
                        trends['performance_trend'] = 'declining'
                
                print(f"   📊 Изменение подписчиков: {trends['subscriber_change']:+d}")
                print(f"   📈 Изменение View Rate: {trends['view_rate_change']:+.1f}%")
                print(f"   📅 Рост за неделю: {trends['weekly_growth']:+d}")
                print(f"   🎯 Тренд: {trends['performance_trend']}")
        
        except Exception as e:
            print(f"   ❌ Ошибка анализа трендов: {e}")
        
        return trends
    
    def check_alerts(self, metrics: Dict, trends: Dict) -> List[Dict]:
        """Проверяет условия для алертов"""
        
        print("🚨 Проверка алертов...")
        
        alerts = []
        
        # 1. Критическое падение View Rate
        if metrics['view_rate'] < self.kpi_thresholds['view_rate_min']:
            alerts.append({
                'type': 'critical',
                'metric': 'view_rate',
                'message': f"🚨 Критическое падение View Rate: {metrics['view_rate']:.1f}% < {self.kpi_thresholds['view_rate_min']}%",
                'action': 'Срочно проанализировать контент и время публикации'
            })
        
        # 2. Падение View Rate два дня подряд
        if trends['view_rate_change'] < -2:  # Падение более чем на 2%
            alerts.append({
                'type': 'warning',
                'metric': 'view_rate_trend',
                'message': f"⚠️ View Rate падает: {trends['view_rate_change']:+.1f}%",
                'action': 'Проверить качество недавних постов'
            })
        
        # 3. Отсутствие роста подписчиков
        if trends['weekly_growth'] < self.kpi_thresholds['subscriber_growth_weekly']:
            alerts.append({
                'type': 'info',
                'metric': 'subscriber_growth',
                'message': f"📊 Медленный рост подписчиков: {trends['weekly_growth']} за неделю",
                'action': 'Активизировать стратегию роста'
            })
        
        # 4. Вирусный пост (положительный алерт)
        if metrics['today_best_post'] > self.kpi_thresholds['viral_post_threshold']:
            alerts.append({
                'type': 'success',
                'metric': 'viral_post',
                'message': f"🚀 Вирусный пост сегодня: {metrics['today_best_post']:,} просмотров!",
                'action': 'Проанализировать и повторить успешный формат'
            })
        
        # 5. Низкая производительность постов
        low_performance_posts = [p for p in metrics['new_posts_performance'] 
                               if p['views'] < self.kpi_thresholds['low_performance_threshold']]
        if low_performance_posts:
            alerts.append({
                'type': 'warning',
                'metric': 'post_performance',
                'message': f"⚠️ {len(low_performance_posts)} постов с низкими просмотрами (<{self.kpi_thresholds['low_performance_threshold']})",
                'action': 'Пересмотреть стратегию контента'
            })
        
        if alerts:
            print(f"   🚨 Найдено {len(alerts)} алертов")
            for alert in alerts:
                print(f"   {alert['message']}")
        else:
            print("   ✅ Все показатели в норме")
        
        return alerts
    
    def update_notion_dashboard(self, metrics: Dict) -> bool:
        """Обновляет дашборд в Notion"""
        
        print("📝 Обновление Notion...")
        
        try:
            # Обновляем Platform Database
            platforms_query = {
                "filter": {
                    "property": "Platforms",
                    "title": {
                        "equals": "Telegram"
                    }
                }
            }
            
            query_url = f"https://api.notion.so/v1/databases/{self.platforms_db_id}/query"
            try:
        response = requests.post(query_url, headers=self.headers, json=platforms_query)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in POST request: {{e}}")
        return None
    
    response
            
            
                data = response.json()
                if data['results']:
                    page_id = data['results'][0]['id']
                    
                    # Обновляем данные
                    update_data = {
                        "properties": {
                            "Followers": {"number": metrics['subscribers']},
                            "Posts": {"number": metrics['total_posts']},
                            "Avg Views": {"number": int(metrics['avg_views'])},
                            "Last Updated": {
                                "date": {
                                    "start": datetime.now().isoformat()
                                }
                            }
                        }
                    }
                    
                    update_url = f"https://api.notion.so/v1/pages/{page_id}"
                    update_try:
        response = requests.patch(update_url, headers=self.headers, json=update_data)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in PATCH request: {{e}}")
        return None
    
    response
                    
                    if update_response.status_code == 200:
                        print("   ✅ Notion обновлен")
                        return True
                    else:
                        print(f"   ❌ Ошибка обновления: {update_response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Ошибка Notion: {e}")
        
        return False
    
    def generate_daily_report(self, metrics: Dict, trends: Dict, alerts: List) -> str:
        """Генерирует ежедневный отчет"""
        
        report = f"""
📊 ЕЖЕДНЕВНЫЙ ОТЧЕТ TELEGRAM
{'='*40}
📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}

🎯 ОСНОВНЫЕ ПОКАЗАТЕЛИ:
   👥 Подписчики: {metrics['subscribers']:,} ({trends['subscriber_change']:+d})
   📝 Постов сегодня: {metrics['posts_today']}
   📊 View Rate: {metrics['view_rate']:.1f}% ({trends['view_rate_change']:+.1f}%)
   📈 Рост за неделю: {trends['weekly_growth']:+d} подписчиков

📝 КОНТЕНТ СЕГОДНЯ:
   🏆 Лучший пост: {metrics['today_best_post']:,} просмотров
   📊 Средние просмотры: {metrics['avg_views']:.0f}
   🎯 Тренд производительности: {trends['performance_trend']}
"""
        
        if alerts:
            report += f"\n🚨 АЛЕРТЫ ({len(alerts)}):\n"
            for alert in alerts:
                icon = {"critical": "🚨", "warning": "⚠️", "info": "📊", "success": "🚀"}
                report += f"   {icon.get(alert['type'], '📊')} {alert['message']}\n"
                report += f"      → {alert['action']}\n"
        else:
            report += "\n✅ ВСЕ ПОКАЗАТЕЛИ В НОРМЕ\n"
        
        # Рекомендации на основе данных
        report += f"\n💡 РЕКОМЕНДАЦИИ НА ЗАВТРА:\n"
        
        if metrics['view_rate'] < 15:
            report += "   📈 Оптимизировать время публикации\n"
        
        if metrics['posts_today'] == 0:
            report += "   📝 Сегодня не было постов - планировать регулярность\n"
        elif metrics['posts_today'] > 3:
            report += "   ⚠️ Много постов сегодня - следить за качеством\n"
        
        if trends['weekly_growth'] < 50:
            report += "   👥 Активизировать стратегию роста\n"
        
        if any(alert['type'] == 'success' for alert in alerts):
            report += "   🚀 Анализировать успешный контент для повтора\n"
        
        return report
    
    def save_daily_history(self, metrics: Dict) -> None:
        """Сохраняет данные в историю"""
        
        try:
            history = self.load_history()
            history.append(metrics)
            
            # Сохраняем только последние 30 дней
            if len(history) > 30:
                history = history[-30:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2, default=str)
        
        except Exception as e:
            print(f"❌ Ошибка сохранения истории: {e}")
    
    def load_history(self) -> List[Dict]:
        """Загружает историю данных"""
        
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"❌ Ошибка загрузки истории: {e}")
            return []
    
    def get_recent_posts(self, channel: str) -> List[Dict]:
        """Получает данные недавних постов"""
        
        try:
            url = f"https://t.me/s/{channel}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error in GET request: {{e}}")
        return None
    
    response
            
            
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                posts_elements = soup.find_all('div', class_='tgme_widget_message')
                
                posts_data = []
                for post_elem in posts_elements:
                    views_elem = post_elem.find('span', class_='tgme_widget_message_views')
                    if views_elem:
                        views_text = views_elem.text.strip()
                        views = self.convert_count_to_number(views_text)
                        
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
            print(f"❌ Ошибка получения постов: {e}")
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
    
    def send_alerts(self, alerts: List[Dict], report: str) -> None:
        """Отправляет алерты (в консоль или файл)"""
        
        critical_alerts = [a for a in alerts if a['type'] == 'critical']
        
        if critical_alerts:
            print("\n🚨 КРИТИЧЕСКИЕ АЛЕРТЫ!")
            for alert in critical_alerts:
                print(f"   {alert['message']}")
                print(f"   → {alert['action']}")
            
            # Сохраняем алерты в файл
            alert_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            alert_filename = f"telegram_alerts_{alert_timestamp}.txt"
            
            with open(alert_filename, 'w', encoding='utf-8') as f:
                f.write(f"🚨 КРИТИЧЕСКИЕ АЛЕРТЫ - {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write("=" * 50 + "\n\n")
                for alert in critical_alerts:
                    f.write(f"{alert['message']}\n")
                    f.write(f"Действие: {alert['action']}\n\n")
            
            print(f"   📄 Алерты сохранены: {alert_filename}")
    
    def run_weekly_analysis(self) -> str:
        """Запускает еженедельный углубленный анализ"""
        
        print("\n📊 ЕЖЕНЕДЕЛЬНЫЙ АНАЛИЗ")
        print("=" * 40)
        
        history = self.load_history()
        
        if len(history) < 7:
            return "Недостаточно данных для еженедельного анализа"
        
        week_data = history[-7:]
        
        # Анализ недели
        weekly_summary = {
            'avg_view_rate': sum(d.get('view_rate', 0) for d in week_data) / len(week_data),
            'total_new_subscribers': week_data[-1]['subscribers'] - week_data[0]['subscribers'],
            'total_posts': sum(d.get('posts_today', 0) for d in week_data),
            'best_day_view_rate': max(d.get('view_rate', 0) for d in week_data),
            'worst_day_view_rate': min(d.get('view_rate', 0) for d in week_data)
        }
        
        report = f"""
📊 ЕЖЕНЕДЕЛЬНЫЙ ОТЧЕТ
{'='*50}
📅 Период: {week_data[0]['date'][:10]} - {week_data[-1]['date'][:10]}

📈 ИТОГИ НЕДЕЛИ:
   👥 Новых подписчиков: {weekly_summary['total_new_subscribers']:+d}
   📝 Постов опубликовано: {weekly_summary['total_posts']}
   📊 Средний View Rate: {weekly_summary['avg_view_rate']:.1f}%
   🏆 Лучший день: {weekly_summary['best_day_view_rate']:.1f}%
   📉 Худший день: {weekly_summary['worst_day_view_rate']:.1f}%

💡 ВЫВОДЫ И РЕКОМЕНДАЦИИ:
"""
        
        # Рекомендации на основе данных
        if weekly_summary['avg_view_rate'] > 17:
            report += "   ✅ Отличная производительность! Продолжить текущую стратегию\n"
        elif weekly_summary['avg_view_rate'] < 15:
            report += "   ⚠️ View Rate ниже среднего. Пересмотреть контент-стратегию\n"
        
        if weekly_summary['total_new_subscribers'] < 50:
            report += "   📈 Медленный рост. Усилить маркетинговые активности\n"
        
        if weekly_summary['total_posts'] < 7:
            report += "   📝 Мало контента. Увеличить частоту публикаций\n"
        
        print(report)
        return report

def main():
    """Главная функция - запуск мониторинга"""
    
    print("🚀 СИСТЕМА ЕЖЕДНЕВНОГО МОНИТОРИНГА TELEGRAM")
    print("=" * 60)
    
    monitor = TelegramDailyMonitor()
    
    # Проверяем день недели для еженедельного анализа
    is_monday = datetime.now().weekday() == 0
    
    # Запускаем ежедневный мониторинг
    result = monitor.run_daily_monitoring("rawmid")
    
    # Выводим отчет
    print(result['report'])
    
    # Сохраняем отчет
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"telegram_daily_report_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result['report'])
    
    print(f"\n💾 Отчет сохранен: {filename}")
    
    # Еженедельный анализ по понедельникам
    if is_monday:
        weekly_report = monitor.run_weekly_analysis()
        weekly_filename = f"telegram_weekly_report_{timestamp}.txt"
        
        with open(weekly_filename, 'w', encoding='utf-8') as f:
            f.write(weekly_report)
        
        print(f"📊 Еженедельный отчет: {weekly_filename}")

if __name__ == "__main__":
    main() 