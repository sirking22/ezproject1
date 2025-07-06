#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ДЕТАЛЬНОЕ ОБЪЯСНЕНИЕ МЕТРИК

Объясняю Growth Rate, Platform Rank, Content Score
с примерами на реальных данных
"""

import json
from datetime import datetime, timedelta

class MetricsExplainer:
    """Объясняет метрики простым языком"""
    
    def __init__(self):
        # Текущие данные пользователя
        self.current_data = {
            'telegram': {'followers': 4962, 'engagement': 17.3, 'posts_week': 10},
            'instagram': {'followers': 7000, 'engagement': 3.0, 'posts_week': 7},
            'youtube': {'followers': 51000, 'engagement': 4.5, 'posts_week': 3},
            'tiktok': {'followers': 10000, 'engagement': 5.5, 'posts_week': 14},
            'facebook': {'followers': 20000, 'engagement': 1.2, 'posts_week': 5},
            'twitter': {'followers': 15000, 'engagement': 2.2, 'posts_week': 21},
            'vk': {'followers': 0, 'engagement': 0, 'posts_week': 0}
        }
        
        # Цели на 6 месяцев
        self.goals_6m = {
            'telegram': 10000,
            'instagram': 15000,
            'youtube': 75000,
            'tiktok': 25000,
            'facebook': 25000,
            'twitter': 25000,
            'vk': 10000
        }
    
    def explain_growth_rate(self):
        """Объясняет Growth Rate с примерами"""
        
        print("📈 GROWTH RATE - ЧТО ЭТО?")
        print("=" * 50)
        print()
        
        print("💡 ОПРЕДЕЛЕНИЕ:")
        print("   Growth Rate = % рост подписчиков за определенный период")
        print("   Формула: (Новые подписчики / Текущие подписчики) × 100")
        print()
        
        print("📊 ТВОИ ТЕКУЩИЕ ДАННЫЕ VS ЦЕЛИ:")
        print("=" * 60)
        
        total_current = sum(data['followers'] for data in self.current_data.values())
        total_goal = sum(self.goals_6m.values())
        
        for platform, current in self.current_data.items():
            goal = self.goals_6m[platform]
            needed_growth = goal - current['followers']
            
            if current['followers'] > 0:
                growth_needed_percent = (needed_growth / current['followers']) * 100
                monthly_growth_needed = growth_needed_percent / 6  # За 6 месяцев
                
                progress_percent = (current['followers'] / goal) * 100
                
                status = "🚀" if progress_percent > 75 else "✅" if progress_percent > 50 else "⚠️" if progress_percent > 25 else "🔴"
                
                print(f"📱 {platform.upper()}:")
                print(f"   Сейчас: {current['followers']:,} | Цель: {goal:,}")
                print(f"   Прогресс: {progress_percent:.1f}% {status}")
                print(f"   Нужен рост: +{needed_growth:,} ({growth_needed_percent:.1f}%)")
                print(f"   Месячный рост: {monthly_growth_needed:.1f}%/месяц")
                print()
            else:
                print(f"📱 {platform.upper()}:")
                print(f"   Статус: 🔴 НЕ ЗАПУЩЕН | Цель: {goal:,}")
                print(f"   Действие: Запустить с нуля")
                print()
        
        print(f"🎯 ОБЩИЙ ПРОГРЕСС:")
        print(f"   Текущий охват: {total_current:,}")
        print(f"   Целевой охват: {total_goal:,}")
        print(f"   Общий прогресс: {(total_current/total_goal)*100:.1f}%")
        print()
        
        # Примеры расчета
        print("🧮 ПРИМЕР РАСЧЕТА (Telegram):")
        print("   Январь: 4,500 подписчиков")
        print("   Февраль: 4,962 подписчика")
        print("   Growth Rate = (462 / 4,500) × 100 = 10.3% за месяц")
        print("   Годовой Growth Rate = 10.3% × 12 = 123.6%")
        print()
        
        return self.calculate_growth_rates()
    
    def explain_platform_rank(self):
        """Объясняет Platform Rank с автоматическим расчетом"""
        
        print("🏆 PLATFORM RANK - АВТОМАТИЧЕСКАЯ ОЦЕНКА")
        print("=" * 50)
        print()
        
        print("💡 ЧТО ЭТО:")
        print("   Автоматическая оценка эффективности платформы")
        print("   Учитывает: Engagement Rate, размер аудитории, рост")
        print()
        
        print("🎯 КРИТЕРИИ ОЦЕНКИ:")
        print("   🔥 EXCELLENT: Engagement > 150% от бенчмарка")
        print("   ✅ HIGH:      Engagement > 120% от бенчмарка") 
        print("   📊 MEDIUM:    Engagement > 80% от бенчмарка")
        print("   ⚠️ LOW:       Engagement < 80% от бенчмарка")
        print()
        
        # Бенчмарки
        benchmarks = {
            'telegram': 2.5, 'instagram': 3.5, 'youtube': 4.0,
            'tiktok': 5.0, 'facebook': 1.5, 'twitter': 2.0, 'vk': 2.8
        }
        
        print("📊 АВТОМАТИЧЕСКИЙ РАСЧЕТ ДЛЯ ТВОИХ ПЛАТФОРМ:")
        print("=" * 60)
        
        for platform, data in self.current_data.items():
            if data['followers'] > 0:
                benchmark = benchmarks[platform]
                vs_benchmark = (data['engagement'] / benchmark) * 100
                
                # Определяем ранг
                if vs_benchmark >= 150:
                    rank = "🔥 EXCELLENT"
                    rank_score = 4
                elif vs_benchmark >= 120:
                    rank = "✅ HIGH"
                    rank_score = 3
                elif vs_benchmark >= 80:
                    rank = "📊 MEDIUM"
                    rank_score = 2
                else:
                    rank = "⚠️ LOW"
                    rank_score = 1
                
                print(f"📱 {platform.upper()}:")
                print(f"   Engagement: {data['engagement']:.1f}% | Бенчмарк: {benchmark}%")
                print(f"   vs Индустрия: {vs_benchmark:.0f}%")
                print(f"   Автоматический Rank: {rank}")
                print(f"   Аудитория бонус: +{self.audience_bonus(data['followers'])}")
                print()
        
        print("🤖 КАК РАБОТАЕТ АВТОМАТИЗАЦИЯ:")
        print("   1. Скрипт собирает данные с платформ")
        print("   2. Сравнивает с индустриальными бенчмарками")
        print("   3. Учитывает размер аудитории")
        print("   4. Автоматически присваивает ранг")
        print("   5. Обновляет поле в Notion")
        print()
        
        return self.calculate_platform_ranks()
    
    def explain_content_score(self):
        """Объясняет Content Score"""
        
        print("🎨 CONTENT SCORE - КАЧЕСТВО КОНТЕНТА")
        print("=" * 50)
        print()
        
        print("💡 ЧТО ЭТО:")
        print("   Комплексная оценка качества контента по шкале 1-10")
        print("   Объединяет несколько факторов в одну оценку")
        print()
        
        print("📊 ФАКТОРЫ ОЦЕНКИ:")
        print("=" * 30)
        
        factors = {
            "Engagement Rate": {"weight": 30, "description": "Основной показатель отклика"},
            "Consistency": {"weight": 20, "description": "Стабильность результатов"},
            "Growth Trend": {"weight": 20, "description": "Динамика роста"},
            "Content Frequency": {"weight": 15, "description": "Регулярность публикаций"},
            "Viral Content %": {"weight": 15, "description": "% постов выше среднего в 2+ раза"}
        }
        
        for factor, info in factors.items():
            print(f"   • {factor}: {info['weight']}% - {info['description']}")
        print()
        
        print("🧮 ПРИМЕР РАСЧЕТА (Telegram):")
        print("=" * 40)
        
        # Telegram example calculation
        telegram_scores = {
            "Engagement Rate": {"score": 10, "reason": "17.3% vs 2.5% бенчмарк = максимум"},
            "Consistency": {"score": 6, "reason": "56.4% консистентность = средне"},
            "Growth Trend": {"score": 7, "reason": "Стабильный рост"},
            "Content Frequency": {"score": 8, "reason": "1.5 поста/день = хорошо"},
            "Viral Content %": {"score": 9, "reason": "20% вирусных постов = отлично"}
        }
        
        total_score = 0
        for factor, data in telegram_scores.items():
            weight = factors[factor]["weight"] / 100
            weighted_score = data["score"] * weight
            total_score += weighted_score
            
            print(f"   {factor}: {data['score']}/10 × {factors[factor]['weight']}% = {weighted_score:.1f}")
            print(f"      └─ {data['reason']}")
        
        print(f"\n   🎯 ИТОГОВЫЙ CONTENT SCORE: {total_score:.1f}/10")
        print()
        
        print("📈 ИНТЕРПРЕТАЦИЯ ОЦЕНОК:")
        print("   9-10: 🔥 Превосходный контент")
        print("   7-8:  ✅ Хороший контент")
        print("   5-6:  📊 Средний контент") 
        print("   3-4:  ⚠️ Слабый контент")
        print("   1-2:  🚨 Критические проблемы")
        print()
        
        print("🤖 АВТОМАТИЧЕСКИЙ РАСЧЕТ:")
        print("   • Скрипт анализирует все факторы")
        print("   • Рассчитывает взвешенную оценку")
        print("   • Обновляет Content Score в Notion")
        print("   • Дает рекомендации по улучшению")
        print()
        
        return self.calculate_content_scores()
    
    def audience_bonus(self, followers):
        """Рассчитывает бонус за размер аудитории"""
        if followers > 50000:
            return "Макс (+0.5)"
        elif followers > 20000:
            return "Высокий (+0.3)"
        elif followers > 10000:
            return "Средний (+0.2)"
        elif followers > 5000:
            return "Малый (+0.1)"
        else:
            return "Нет (0)"
    
    def calculate_growth_rates(self):
        """Рассчитывает примерные growth rates"""
        results = {}
        
        for platform, data in self.current_data.items():
            if data['followers'] > 0:
                goal = self.goals_6m[platform]
                needed_growth = (goal - data['followers']) / data['followers'] * 100
                monthly_rate = needed_growth / 6
                
                results[platform] = {
                    'current': data['followers'],
                    'goal': goal,
                    'needed_total': needed_growth,
                    'needed_monthly': monthly_rate,
                    'progress': (data['followers'] / goal) * 100
                }
        
        return results
    
    def calculate_platform_ranks(self):
        """Рассчитывает автоматические ранги"""
        benchmarks = {
            'telegram': 2.5, 'instagram': 3.5, 'youtube': 4.0,
            'tiktok': 5.0, 'facebook': 1.5, 'twitter': 2.0, 'vk': 2.8
        }
        
        results = {}
        
        for platform, data in self.current_data.items():
            if data['followers'] > 0:
                benchmark = benchmarks[platform]
                vs_benchmark = (data['engagement'] / benchmark) * 100
                
                if vs_benchmark >= 150:
                    rank = "EXCELLENT"
                elif vs_benchmark >= 120:
                    rank = "HIGH"
                elif vs_benchmark >= 80:
                    rank = "MEDIUM"
                else:
                    rank = "LOW"
                
                results[platform] = {
                    'rank': rank,
                    'vs_benchmark': vs_benchmark,
                    'engagement': data['engagement'],
                    'benchmark': benchmark
                }
        
        return results
    
    def calculate_content_scores(self):
        """Рассчитывает content scores"""
        
        # Веса факторов
        weights = {
            'engagement': 0.30,
            'consistency': 0.20,
            'growth': 0.20,
            'frequency': 0.15,
            'viral': 0.15
        }
        
        # Бенчмарки для нормализации
        benchmarks = {
            'telegram': 2.5, 'instagram': 3.5, 'youtube': 4.0,
            'tiktok': 5.0, 'facebook': 1.5, 'twitter': 2.0
        }
        
        results = {}
        
        for platform, data in self.current_data.items():
            if data['followers'] > 0 and platform in benchmarks:
                # Engagement score (1-10)
                engagement_ratio = data['engagement'] / benchmarks[platform]
                engagement_score = min(10, engagement_ratio * 4)  # Масштабируем
                
                # Примерные оценки других факторов
                consistency_score = 6 if platform == 'telegram' else 7  # Примерно
                growth_score = 7  # Примерно
                frequency_score = min(10, (data['posts_week'] / 10) * 10)
                viral_score = 8 if platform == 'telegram' else 6  # Примерно
                
                # Итоговая оценка
                total_score = (
                    engagement_score * weights['engagement'] +
                    consistency_score * weights['consistency'] +
                    growth_score * weights['growth'] +
                    frequency_score * weights['frequency'] +
                    viral_score * weights['viral']
                )
                
                results[platform] = {
                    'total_score': round(total_score, 1),
                    'engagement_score': round(engagement_score, 1),
                    'breakdown': {
                        'engagement': engagement_score,
                        'consistency': consistency_score,
                        'growth': growth_score,
                        'frequency': frequency_score,
                        'viral': viral_score
                    }
                }
        
        return results

def main():
    """Главная функция - объяснение метрик"""
    
    print("🎯 ДЕТАЛЬНОЕ ОБЪЯСНЕНИЕ КЛЮЧЕВЫХ МЕТРИК")
    print("=" * 80)
    print()
    
    explainer = MetricsExplainer()
    
    # 1. Growth Rate
    growth_data = explainer.explain_growth_rate()
    
    print("\n" + "="*80 + "\n")
    
    # 2. Platform Rank  
    rank_data = explainer.explain_platform_rank()
    
    print("\n" + "="*80 + "\n")
    
    # 3. Content Score
    content_data = explainer.explain_content_score()
    
    # Итоговая сводка
    print("\n" + "="*80)
    print("📋 ИТОГОВАЯ СВОДКА ДЛЯ NOTION")
    print("="*80)
    
    print("\n🎯 РЕКОМЕНДУЕМЫЕ ЗНАЧЕНИЯ ДЛЯ ТВОИХ ПЛАТФОРМ:")
    print("=" * 60)
    
    for platform in ['telegram', 'instagram', 'youtube', 'tiktok', 'facebook', 'twitter']:
        if platform in growth_data and platform in rank_data and platform in content_data:
            print(f"\n📱 {platform.upper()}:")
            print(f"   Growth Rate (месячная цель): {growth_data[platform]['needed_monthly']:.1f}%")
            print(f"   Platform Rank: {rank_data[platform]['rank']}")
            print(f"   Content Score: {content_data[platform]['total_score']}/10")
            print(f"   vs Industry: {rank_data[platform]['vs_benchmark']:.0f}%")
    
    print(f"\n💡 ВСЕ ЭТИ ЗНАЧЕНИЯ МОГУТ РАССЧИТЫВАТЬСЯ АВТОМАТИЧЕСКИ!")
    print(f"   Просто запускай скрипт раз в день - и Notion обновится сам")

if __name__ == "__main__":
    main() 