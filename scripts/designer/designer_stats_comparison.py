#!/usr/bin/env python3
"""
Сравнительная статистика по дизайнерам
Анализ загрузки и эффективности команды
"""

import asyncio
from collections import defaultdict
from mcp_notion_server import NotionMCPServer

async def analyze_all_designers():
    """Анализ всех дизайнеров"""
    try:
        # Инициализация сервера
        server = NotionMCPServer()
        
        # Получение всех задач
        tasks_db_id = server.tasks_db_id or "d09df250ce7e4e0d9fbe4e036d320def"
        print(f"🔍 Получение всех задач из базы: {tasks_db_id}")
        
        tasks_response = await server.get_database_pages(tasks_db_id)
        
        if not tasks_response.get('success'):
            print(f"❌ Ошибка получения задач: {tasks_response.get('error')}")
            return
        
        all_tasks = tasks_response.get('pages', [])
        print(f"📊 Всего задач в базе: {len(all_tasks)}")
        
        # Статистика по дизайнерам
        designer_stats = {}
        
        # Обработка каждой задачи
        for task in all_tasks:
            properties = task.get('properties', {})
            participants = properties.get('Участники', [])
            status = properties.get('Статус', {})
            title = properties.get('Задача', 'Без названия')
            
            # Обрабатываем каждого участника  
            participant_names = []
            if isinstance(participants, list):
                participant_names = [p for p in participants if isinstance(p, str) and p.strip()]
            
            # Парсим статус из строки (MCP возвращает строки вместо объектов)
            status_name = 'unknown'
            if isinstance(status, str):
                try:
                    import json
                    status_data = json.loads(status.replace("'", '"'))
                    if 'status' in status_data:
                        status_name = status_data['status'].get('name', 'unknown').lower()
                except:
                    pass
            
            for participant in participant_names:
                if participant:
                    # Инициализация дизайнера если его нет
                    if participant not in designer_stats:
                        designer_stats[participant] = {
                            'total': 0,
                            'to_do': 0,
                            'in_progress': 0,
                            'done': 0,
                            'backlog': 0,
                            'tasks': []
                        }
                    
                    designer_stats[participant]['total'] += 1
                    designer_stats[participant]['tasks'].append({
                        'title': title,
                        'status': status_name,
                        'id': task['id']
                    })
                    
                    # Подсчет по статусам
                    if 'to do' in status_name:
                        designer_stats[participant]['to_do'] += 1
                    elif 'progress' in status_name:
                        designer_stats[participant]['in_progress'] += 1
                    elif 'done' in status_name:
                        designer_stats[participant]['done'] += 1
                    elif 'backlog' in status_name:
                        designer_stats[participant]['backlog'] += 1
        
        # Вывод результатов
        print("\n" + "="*80)
        print("👥 СРАВНИТЕЛЬНАЯ СТАТИСТИКА ПО ДИЗАЙНЕРАМ")
        print("="*80)
        
        # Сортируем по общему количеству задач
        sorted_designers = sorted(designer_stats.items(), 
                                key=lambda x: x[1]['total'], reverse=True)
        
        for designer, stats in sorted_designers:
            if stats['total'] > 0:  # Только дизайнеры с задачами
                print(f"\n🎨 {designer}")
                print(f"   📋 Всего задач: {stats['total']}")
                print(f"   ⚫ К выполнению: {stats['to_do']}")
                print(f"   🟡 В процессе: {stats['in_progress']}")
                print(f"   🟢 Выполнено: {stats['done']}")
                print(f"   🟤 В очереди: {stats['backlog']}")
                
                # Процент загрузки (активные задачи)
                active_tasks = stats['to_do'] + stats['in_progress']
                if stats['total'] > 0:
                    load_percent = (active_tasks / stats['total']) * 100
                    print(f"   🔥 Загрузка: {active_tasks}/{stats['total']} ({load_percent:.1f}%)")
                
                # Эффективность (выполненные / общие)
                if stats['total'] > 0:
                    efficiency = (stats['done'] / stats['total']) * 100
                    print(f"   ⚡ Эффективность: {efficiency:.1f}%")
        
        # Общая статистика
        print("\n" + "="*80)
        print("📊 ОБЩАЯ СТАТИСТИКА КОМАНДЫ")
        print("="*80)
        
        total_designers = len([d for d, s in designer_stats.items() if s['total'] > 0])
        total_tasks = sum(s['total'] for s in designer_stats.values())
        total_active = sum(s['to_do'] + s['in_progress'] for s in designer_stats.values())
        total_done = sum(s['done'] for s in designer_stats.values())
        
        print(f"👥 Активных дизайнеров: {total_designers}")
        print(f"📋 Всего задач: {total_tasks}")
        print(f"🔥 Активных задач: {total_active}")
        print(f"✅ Выполнено задач: {total_done}")
        
        if total_tasks > 0:
            team_efficiency = (total_done / total_tasks) * 100
            print(f"⚡ Эффективность команды: {team_efficiency:.1f}%")
        
        # Топ-3 самых загруженных
        print(f"\n🏆 ТОП-3 САМЫХ ЗАГРУЖЕННЫХ:")
        for i, (designer, stats) in enumerate(sorted_designers[:3], 1):
            if stats['total'] > 0:
                active = stats['to_do'] + stats['in_progress']
                print(f"   {i}. {designer}: {active} активных задач")
        
        return designer_stats
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {}

async def main():
    """Основная функция"""
    print("🚀 Анализ эффективности дизайнеров")
    print("="*50)
    
    # Выполняем анализ
    stats = await analyze_all_designers()
    
    print(f"\n✅ Анализ завершен для {len(stats) if stats else 0} дизайнеров")

if __name__ == "__main__":
    asyncio.run(main()) 