#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реальный сервис для работы с Notion базами в боте
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

class NotionBotService:
    """Сервис для работы с Notion базами в боте"""
    
    def __init__(self):
        self.api_key = os.getenv('NOTION_TOKEN')
        if not self.api_key:
            logger.error("❌ NOTION_TOKEN не найден в .env")
            raise ValueError("NOTION_TOKEN не найден в .env")
            
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        logger.info(f"✅ Подключение к Notion с токеном: {self.api_key[:10]}...")
        
        # ID баз данных
        self.databases = {
            'tasks': os.getenv('TASKS_DB_ID'),
            'projects': os.getenv('PROJECTS_DB_ID'),
            'subtasks': os.getenv('SUBTASKS_DB_ID'),
            'kpi': os.getenv('KPI_DB_ID'),
            'materials': os.getenv('MATERIALS_DB_ID'),
            'ideas': os.getenv('IDEAS_DB_ID'),
            'guides': os.getenv('GUIDES_DB_ID'),
            'concepts': os.getenv('CONCEPTS_DB_ID'),
        }
        
        logger.info("🔗 NotionBotService инициализирован")
    
    def get_user_tasks(self, user_name: str, limit: int = 10) -> List[Dict]:
        """Получить задачи пользователя"""
        try:
            db_id = self.databases['tasks']
            if not db_id:
                return []
            
            # Получаем все задачи без фильтра (пока)
            filter_data = {
                "page_size": limit
            }
            
            response = requests.post(
                f"{self.base_url}/databases/{db_id}/query",
                headers=self.headers,
                json=filter_data
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                tasks = []
                for task in results:
                    props = task.get('properties', {})
                    task_name = props.get('Задача', {}).get('title', [{}])[0].get('plain_text', 'Без названия')
                    status = props.get('Статус', {}).get('select', {}).get('name', 'Не указан')
                    tasks.append({
                        'name': task_name,
                        'status': status,
                        'id': task['id']
                    })
                return tasks
            else:
                logger.error(f"Ошибка получения задач: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка get_user_tasks: {e}")
            return []
    
    def get_all_tasks(self, limit: int = 20) -> List[Dict]:
        """Получить все задачи отдела"""
        try:
            db_id = self.databases['tasks']
            if not db_id:
                return []
            
            logger.info(f"🔍 Запрос к Notion API: {db_id}")
            logger.info(f"🔑 Токен: {self.api_key[:10]}...")
            
            response = requests.post(
                f"{self.base_url}/databases/{db_id}/query",
                headers=self.headers,
                json={"page_size": limit}
            )
            
            logger.info(f"📡 Ответ Notion: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"❌ Ошибка API: {response.text}")
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                tasks = []
                for task in results:
                    props = task.get('properties', {})
                    task_name = props.get('Задача', {}).get('title', [{}])[0].get('plain_text', 'Без названия')
                    status = props.get('Статус', {}).get('select', {}).get('name', 'Не указан')
                    assignee = props.get('Участники', {}).get('people', [])
                    assignee_names = [person.get('name', '') for person in assignee]
                    
                    tasks.append({
                        'name': task_name,
                        'status': status,
                        'assignees': assignee_names,
                        'id': task['id']
                    })
                return tasks
            else:
                logger.error(f"Ошибка получения всех задач: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка get_all_tasks: {e}")
            return []
    
    def get_team_reports(self) -> Dict:
        """Получить отчеты команды"""
        try:
            # Получаем задачи
            tasks = self.get_all_tasks(100)
            
            # Статистика
            total_tasks = len(tasks)
            done_tasks = len([t for t in tasks if t['status'] == 'Done'])
            in_progress = len([t for t in tasks if t['status'] == 'In Progress'])
            todo_tasks = len([t for t in tasks if t['status'] == 'To do'])
            
            # KPI
            completion_rate = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                'total_tasks': total_tasks,
                'done_tasks': done_tasks,
                'in_progress': in_progress,
                'todo_tasks': todo_tasks,
                'completion_rate': round(completion_rate, 1)
            }
            
        except Exception as e:
            logger.error(f"Ошибка get_team_reports: {e}")
            return {}
    
    def get_kpi_data(self) -> List[Dict]:
        """Получить данные KPI"""
        try:
            db_id = self.databases['kpi']
            if not db_id:
                return []
            
            response = requests.post(
                f"{self.base_url}/databases/{db_id}/query",
                headers=self.headers,
                json={"page_size": 50}
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                kpi_data = []
                for kpi in results:
                    props = kpi.get('properties', {})
                    name = props.get('Name', {}).get('title', [{}])[0].get('plain_text', 'Без названия')
                    target = props.get('Цель', {}).get('number', 0) or 0
                    current = props.get('Текущее значение', {}).get('number', 0) or 0
                    
                    kpi_data.append({
                        'name': name,
                        'target': target,
                        'current': current,
                        'progress': round((current / target * 100) if target > 0 else 0, 1)
                    })
                return kpi_data
            else:
                logger.error(f"Ошибка получения KPI: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка get_kpi_data: {e}")
            return []
    
    def get_projects(self) -> List[Dict]:
        """Получить проекты"""
        try:
            db_id = self.databases['projects']
            if not db_id:
                return []
            
            response = requests.post(
                f"{self.base_url}/databases/{db_id}/query",
                headers=self.headers,
                json={"page_size": 20}
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                projects = []
                for project in results:
                    props = project.get('properties', {})
                    name = props.get('Name', {}).get('title', [{}])[0].get('plain_text', 'Без названия')
                    status = props.get('Статус', {}).get('select', {}).get('name', 'Не указан')
                    
                    projects.append({
                        'name': name,
                        'status': status,
                        'id': project['id']
                    })
                return projects
            else:
                logger.error(f"Ошибка получения проектов: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка get_projects: {e}")
            return []
    
    def get_guides(self, category: str = None) -> List[Dict]:
        """Получить гайды и инструкции"""
        try:
            db_id = self.databases['guides']
            if not db_id:
                return []
            
            filter_data = {"page_size": 20}
            if category:
                filter_data["filter"] = {
                    "property": "Категория",
                    "select": {"equals": category}
                }
            
            response = requests.post(
                f"{self.base_url}/databases/{db_id}/query",
                headers=self.headers,
                json=filter_data
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                guides = []
                for guide in results:
                    props = guide.get('properties', {})
                    name = props.get('Name', {}).get('title', [{}])[0].get('plain_text', 'Без названия')
                    category = props.get('Категория', {}).get('select', {}).get('name', 'Общие')
                    
                    guides.append({
                        'name': name,
                        'category': category,
                        'id': guide['id']
                    })
                return guides
            else:
                logger.error(f"Ошибка получения гайдов: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка get_guides: {e}")
            return []

# Создаем глобальный экземпляр
notion_service = NotionBotService() 