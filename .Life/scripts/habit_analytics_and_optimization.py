import os
import asyncio
from datetime import datetime, timedelta
from notion_client import AsyncClient
from dotenv import load_dotenv
import json

load_dotenv()

HABITS_DB = os.getenv('NOTION_DATABASE_ID_HABITS')
RITUALS_DB = os.getenv('NOTION_DATABASE_ID_RITUALS')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')

class HabitAnalytics:
    def __init__(self):
        self.client = AsyncClient(auth=NOTION_TOKEN)
        self.analytics_data = {}
    
    async def collect_habit_data(self):
        """Собирает данные о привычках за последние 30 дней"""
        print("=== Сбор данных о привычках ===")
        
        # Получаем привычки за последние 30 дней
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        response = await self.client.databases.query(
            database_id=HABITS_DB,
            filter={
                "property": "Дата",
                "date": {
                    "on_or_after": thirty_days_ago
                }
            }
        )
        
        habits = response.get('results', [])
        print(f"Найдено привычек за 30 дней: {len(habits)}")
        
        # Анализируем каждую привычку
        habit_stats = {}
        for habit in habits:
            props = habit['properties']
            
            # Извлекаем данные
            name = props.get('Привычка', {}).get('title', [])
            name_text = name[0]['plain_text'] if name else 'Без названия'
            
            completed = props.get('Выполнено', {}).get('checkbox', False) if props.get('Выполнено') else False
            energy = props.get('Уровень энергии', {}).get('number') if props.get('Уровень энергии') else None
            mood_select = props.get('Настроение', {})
            mood = mood_select.get('select', {}).get('name') if mood_select and mood_select.get('select') else None
            duration = props.get('Длительность', {}).get('number') if props.get('Длительность') else None
            comments = props.get('Комментарии', {}).get('rich_text', []) if props.get('Комментарии') else []
            comments_text = comments[0]['text']['content'] if comments else ''
            
            # Связь с ритуалом
            ritual_relation = props.get('Ритуалы', {}).get('relation', []) if props.get('Ритуалы') else []
            ritual_id = ritual_relation[0]['id'] if ritual_relation else None
            
            # Группируем по типу привычки (убираем дату из названия)
            habit_type = name_text.split(' - ')[0] if ' - ' in name_text else name_text
            
            if habit_type not in habit_stats:
                habit_stats[habit_type] = {
                    'total': 0,
                    'completed': 0,
                    'energy_levels': [],
                    'moods': [],
                    'durations': [],
                    'comments': [],
                    'ritual_id': ritual_id
                }
            
            habit_stats[habit_type]['total'] += 1
            if completed:
                habit_stats[habit_type]['completed'] += 1
            
            if energy is not None:
                habit_stats[habit_type]['energy_levels'].append(energy)
            if mood:
                habit_stats[habit_type]['moods'].append(mood)
            if duration:
                habit_stats[habit_type]['durations'].append(duration)
            if comments_text:
                habit_stats[habit_type]['comments'].append(comments_text)
        
        self.analytics_data = habit_stats
        return habit_stats
    
    async def analyze_effectiveness(self):
        """Анализирует эффективность привычек"""
        print("\n=== Анализ эффективности ===")
        
        effectiveness_report = {}
        
        for habit_type, stats in self.analytics_data.items():
            completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            avg_energy = sum(stats['energy_levels']) / len(stats['energy_levels']) if stats['energy_levels'] else 0
            avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
            
            # Анализируем настроения
            mood_counts = {}
            for mood in stats['moods']:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            # Определяем приоритетность
            priority_score = 0
            if completion_rate >= 80:
                priority_score = 3  # Высокий приоритет
            elif completion_rate >= 50:
                priority_score = 2  # Средний приоритет
            else:
                priority_score = 1  # Низкий приоритет
            
            effectiveness_report[habit_type] = {
                'completion_rate': completion_rate,
                'avg_energy': avg_energy,
                'avg_duration': avg_duration,
                'mood_distribution': mood_counts,
                'priority_score': priority_score,
                'total_attempts': stats['total'],
                'successful_attempts': stats['completed']
            }
            
            print(f"\n{habit_type}:")
            print(f"  Выполнение: {completion_rate:.1f}% ({stats['completed']}/{stats['total']})")
            print(f"  Средняя энергия: {avg_energy:.1f}")
            print(f"  Средняя длительность: {avg_duration:.1f} мин")
            print(f"  Приоритет: {'Высокий' if priority_score == 3 else 'Средний' if priority_score == 2 else 'Низкий'}")
        
        return effectiveness_report
    
    async def generate_optimization_suggestions(self, effectiveness_report):
        """Генерирует предложения по оптимизации"""
        print("\n=== Предложения по оптимизации ===")
        
        suggestions = []
        
        for habit_type, report in effectiveness_report.items():
            suggestions_for_habit = []
            
            # Анализ выполнения
            if report['completion_rate'] < 50:
                suggestions_for_habit.append("🔴 Низкое выполнение - упростить или изменить подход")
            elif report['completion_rate'] < 80:
                suggestions_for_habit.append("🟡 Среднее выполнение - добавить напоминания или мотивацию")
            else:
                suggestions_for_habit.append("🟢 Высокое выполнение - можно усложнить или добавить новые элементы")
            
            # Анализ энергии
            if report['avg_energy'] < 5:
                suggestions_for_habit.append("🔋 Низкая энергия - перенести на другое время или упростить")
            elif report['avg_energy'] > 8:
                suggestions_for_habit.append("⚡ Высокая энергия - можно добавить сложности")
            
            # Анализ настроения
            if report['mood_distribution']:
                most_common_mood = max(report['mood_distribution'], key=report['mood_distribution'].get)
                if most_common_mood in ['Плохо', 'Устал']:
                    suggestions_for_habit.append("😔 Часто плохое настроение - добавить элементы удовольствия")
                elif most_common_mood in ['Отлично', 'Вдохновлён']:
                    suggestions_for_habit.append("😊 Хорошее настроение - использовать как якорь для других привычек")
            
            suggestions.append({
                'habit_type': habit_type,
                'suggestions': suggestions_for_habit,
                'priority_score': report['priority_score']
            })
        
        # Сортируем по приоритету
        suggestions.sort(key=lambda x: x['priority_score'], reverse=True)
        
        for suggestion in suggestions:
            print(f"\n{suggestion['habit_type']} (Приоритет: {suggestion['priority_score']}):")
            for s in suggestion['suggestions']:
                print(f"  {s}")
        
        return suggestions
    
    async def update_ritual_with_feedback(self, ritual_id, feedback_data):
        """Обновляет ритуал с обратной связью"""
        if not ritual_id:
            return
        
        try:
            # Получаем текущий ритуал
            ritual = await self.client.pages.retrieve(page_id=ritual_id)
            
            # Добавляем обратную связь в описание
            current_description = ritual['properties'].get('Описание', {}).get('rich_text', [])
            current_text = current_description[0]['text']['content'] if current_description else ''
            
            feedback_text = f"\n\n=== Обратная связь ({datetime.now().strftime('%Y-%m-%d')}) ===\n"
            feedback_text += f"Эффективность: {feedback_data.get('effectiveness', 'Не оценено')}\n"
            feedback_text += f"Сложность: {feedback_data.get('difficulty', 'Не оценено')}\n"
            feedback_text += f"Предложения: {feedback_data.get('suggestions', 'Нет')}\n"
            
            new_description = current_text + feedback_text
            
            # Обновляем ритуал
            await self.client.pages.update(
                page_id=ritual_id,
                properties={
                    'Описание': {'rich_text': [{'text': {'content': new_description}}]}
                }
            )
            
            print(f"✅ Обратная связь добавлена в ритуал")
            
        except Exception as e:
            print(f"❌ Ошибка обновления ритуала: {e}")
    
    async def create_weekly_report(self):
        """Создаёт еженедельный отчёт"""
        print("\n=== Создание еженедельного отчёта ===")
        
        # Собираем данные
        await self.collect_habit_data()
        effectiveness_report = await self.analyze_effectiveness()
        suggestions = await self.generate_optimization_suggestions(effectiveness_report)
        
        # Создаём отчёт
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'period': '30 дней',
            'total_habits': sum(stats['total'] for stats in self.analytics_data.values()),
            'completed_habits': sum(stats['completed'] for stats in self.analytics_data.values()),
            'overall_completion_rate': sum(stats['completed'] for stats in self.analytics_data.values()) / sum(stats['total'] for stats in self.analytics_data.values()) * 100 if sum(stats['total'] for stats in self.analytics_data.values()) > 0 else 0,
            'effectiveness_report': effectiveness_report,
            'suggestions': suggestions
        }
        
        # Сохраняем отчёт
        with open(f"docs/habit_analytics_report_{datetime.now().strftime('%Y%m%d')}.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Отчёт сохранён: docs/habit_analytics_report_{datetime.now().strftime('%Y%m%d')}.json")
        
        return report

async def main():
    analytics = HabitAnalytics()
    
    # Создаём еженедельный отчёт
    report = await analytics.create_weekly_report()
    
    print(f"\n=== ИТОГИ ===")
    print(f"Общее выполнение: {report['overall_completion_rate']:.1f}%")
    print(f"Всего привычек: {report['total_habits']}")
    print(f"Выполнено: {report['completed_habits']}")
    
    # Топ-3 самых эффективных привычки
    top_habits = sorted(report['effectiveness_report'].items(), 
                       key=lambda x: x[1]['completion_rate'], reverse=True)[:3]
    
    print(f"\nТоп-3 эффективных привычки:")
    for i, (habit, stats) in enumerate(top_habits, 1):
        print(f"{i}. {habit}: {stats['completion_rate']:.1f}%")

if __name__ == '__main__':
    asyncio.run(main()) 