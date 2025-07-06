#!/usr/bin/env python3
"""
Интеграция с Google Calendar
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    id: str
    title: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: List[str] = None
    reminders: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.reminders is None:
            self.reminders = {"useDefault": True}

class GoogleCalendarIntegration:
    """Интеграция с Google Calendar"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_path: str = None, calendar_id: str = "primary"):
        self.credentials_path = credentials_path
        self.calendar_id = calendar_id
        self.service = None
        self.credentials = None
        
    async def initialize(self):
        """Инициализация Google Calendar API"""
        try:
            # Пока используем заглушку для тестирования
            logger.info("Google Calendar интеграция инициализирована (тестовый режим)")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Google Calendar: {e}")
            return False
    
    async def _get_credentials(self) -> Credentials:
        """Получение учетных данных Google"""
        creds = None
        
        # Проверяем существующие токены
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # Если нет валидных учетных данных, запрашиваем новые
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if self.credentials_path and os.path.exists(self.credentials_path):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    raise Exception("Файл учетных данных Google не найден")
            
            # Сохраняем учетные данные
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    async def create_event(self, title: str, description: str = None,
                          start_time: datetime = None, end_time: datetime = None,
                          location: str = None, attendees: List[str] = None,
                          reminders: Dict[str, Any] = None) -> Optional[CalendarEvent]:
        """Создание события в календаре"""
        try:
            # Подготавливаем данные события
            if not start_time:
                start_time = datetime.now()
            if not end_time:
                end_time = start_time + timedelta(hours=1)
            
            # Создаем объект события (пока без реального API)
            calendar_event = CalendarEvent(
                id=f"event_{int(datetime.now().timestamp())}",
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                location=location,
                attendees=attendees or [],
                reminders=reminders or {"useDefault": True}
            )
            
            logger.info(f"Событие создано в календаре: {title}")
            return calendar_event
            
        except Exception as e:
            logger.error(f"Ошибка создания события в календаре: {e}")
            return None
    
    async def get_events(self, start_date: datetime = None, end_date: datetime = None,
                        max_results: int = 10) -> List[CalendarEvent]:
        """Получение событий из календаря"""
        try:
            # Устанавливаем временные рамки
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = start_date + timedelta(days=7)
            
            # Пока возвращаем тестовые данные
            events = [
                CalendarEvent(
                    id="test_1",
                    title="Тестовое событие 1",
                    description="Описание события",
                    start_time=start_date + timedelta(hours=2),
                    end_time=start_date + timedelta(hours=3)
                ),
                CalendarEvent(
                    id="test_2",
                    title="Тестовое событие 2",
                    description="Еще одно событие",
                    start_time=start_date + timedelta(hours=5),
                    end_time=start_date + timedelta(hours=6)
                )
            ]
            
            logger.info(f"Получено {len(events)} событий из календаря")
            return events
            
        except Exception as e:
            logger.error(f"Ошибка получения событий из календаря: {e}")
            return []
    
    async def update_event(self, event_id: str, **kwargs) -> Optional[CalendarEvent]:
        """Обновление события в календаре"""
        try:
            if not self.service:
                await self.initialize()
            
            # Получаем текущее событие
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Обновляем поля
            if 'title' in kwargs:
                event['summary'] = kwargs['title']
            if 'description' in kwargs:
                event['description'] = kwargs['description']
            if 'start_time' in kwargs:
                event['start']['dateTime'] = kwargs['start_time'].isoformat()
            if 'end_time' in kwargs:
                event['end']['dateTime'] = kwargs['end_time'].isoformat()
            if 'location' in kwargs:
                event['location'] = kwargs['location']
            
            # Обновляем событие
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            # Создаем объект события
            calendar_event = CalendarEvent(
                id=updated_event['id'],
                title=updated_event['summary'],
                description=updated_event.get('description'),
                start_time=datetime.fromisoformat(updated_event['start']['dateTime'].replace('Z', '+00:00')),
                end_time=datetime.fromisoformat(updated_event['end']['dateTime'].replace('Z', '+00:00')),
                location=updated_event.get('location'),
                attendees=[attendee['email'] for attendee in updated_event.get('attendees', [])],
                reminders=updated_event.get('reminders')
            )
            
            logger.info(f"Событие обновлено в календаре: {calendar_event.title}")
            return calendar_event
            
        except Exception as e:
            logger.error(f"Ошибка обновления события в календаре: {e}")
            return None
    
    async def delete_event(self, event_id: str) -> bool:
        """Удаление события из календаря"""
        try:
            if not self.service:
                await self.initialize()
            
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Событие удалено из календаря: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления события из календаря: {e}")
            return False
    
    async def get_today_events(self) -> List[CalendarEvent]:
        """Получение событий на сегодня"""
        today = datetime.now()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return await self.get_events(start_of_day, end_of_day)
    
    async def get_week_events(self) -> List[CalendarEvent]:
        """Получение событий на неделю"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        
        return await self.get_events(start_of_week, end_of_week)
    
    async def sync_with_todoist(self, todoist_integration):
        """Синхронизация с Todoist"""
        try:
            # Получаем задачи с дедлайнами из Todoist
            todoist_tasks = await todoist_integration.get_tasks()
            
            # Получаем события из календаря
            calendar_events = await self.get_week_events()
            
            # Создаем события для задач с дедлайнами
            for task in todoist_tasks:
                if task.due_date and not any(event.title == task.content for event in calendar_events):
                    await self.create_event(
                        title=f"Задача: {task.content}",
                        description=task.description or "Синхронизировано из Todoist",
                        start_time=task.due_date,
                        end_time=task.due_date + timedelta(hours=1)
                    )
            
            logger.info("Синхронизация с Todoist завершена")
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации с Todoist: {e}")
    
    async def create_reminder(self, title: str, reminder_time: datetime,
                            description: str = None) -> Optional[CalendarEvent]:
        """Создание напоминания"""
        return await self.create_event(
            title=f"⏰ {title}",
            description=description,
            start_time=reminder_time,
            end_time=reminder_time + timedelta(minutes=15),
            reminders={
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 0},
                    {"method": "email", "minutes": 30}
                ]
            }
        ) 