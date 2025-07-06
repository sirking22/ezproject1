"""
Интеграция с Telegram для Quick Voice Assistant
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TelegramMessage:
    """Модель сообщения Telegram"""
    text: str
    chat_id: str
    parse_mode: str = "HTML"
    reply_markup: Optional[Dict[str, Any]] = None
    disable_notification: bool = False

class TelegramIntegration:
    """Класс для интеграции с Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = None
        self.enabled = bool(bot_token and chat_id)
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    async def initialize(self):
        """Инициализация Telegram бота"""
        if not self.enabled:
            logger.warning("Интеграция с Telegram отключена")
            return
        
        try:
            # Здесь будет инициализация Telegram бота
            # from telegram import Bot
            # self.bot = Bot(token=self.bot_token)
            
            # Проверка доступности бота
            success = await self._test_connection()
            if success:
                logger.info("Telegram бот инициализирован")
            else:
                logger.error("Не удалось подключиться к Telegram API")
                self.enabled = False
                
        except Exception as e:
            logger.error(f"Ошибка инициализации Telegram: {e}")
            self.enabled = False
    
    async def _test_connection(self) -> bool:
        """Тестирование подключения к Telegram API"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/getMe")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        bot_info = data.get("result", {})
                        logger.info(f"Бот подключен: @{bot_info.get('username', 'unknown')}")
                        return True
            return False
        except Exception as e:
            logger.error(f"Ошибка тестирования подключения: {e}")
            return False
    
    async def send_message(self, text: str, source: str = "watch_voice") -> bool:
        """Отправка сообщения в Telegram"""
        if not self.enabled:
            return False
        
        try:
            # Форматирование сообщения
            formatted_text = self._format_message(text, source)
            
            # Отправка через API
            success = await self._send_via_api(formatted_text)
            
            if success:
                logger.info(f"Сообщение отправлено в Telegram: {text[:50]}...")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    
    async def send_voice_notification(self, command: str, response: str, action: str = None) -> bool:
        """Отправка уведомления о голосовой команде"""
        if not self.enabled:
            return False
        
        try:
            # Создание красивого уведомления
            notification = self._create_voice_notification(command, response, action)
            
            success = await self._send_via_api(notification)
            
            if success:
                logger.info(f"Уведомление о голосовой команде отправлено")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
            return False
    
    async def send_health_update(self, health_data: Dict[str, Any]) -> bool:
        """Отправка обновления о здоровье"""
        if not self.enabled:
            return False
        
        try:
            # Форматирование данных о здоровье
            health_message = self._format_health_data(health_data)
            
            success = await self._send_via_api(health_message)
            
            if success:
                logger.info("Обновление о здоровье отправлено")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка отправки обновления о здоровье: {e}")
            return False
    
    async def send_progress_report(self, progress_data: Dict[str, Any]) -> bool:
        """Отправка отчета о прогрессе"""
        if not self.enabled:
            return False
        
        try:
            # Форматирование отчета о прогрессе
            progress_message = self._format_progress_data(progress_data)
            
            success = await self._send_via_api(progress_message)
            
            if success:
                logger.info("Отчет о прогрессе отправлен")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка отправки отчета о прогрессе: {e}")
            return False
    
    def _format_message(self, text: str, source: str) -> str:
        """Форматирование сообщения для Telegram"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if source == "watch_voice":
            return f"🎤 <b>Голосовая команда</b>\n\n{text}\n\n⏰ {timestamp}"
        elif source == "system":
            return f"⚙️ <b>Системное уведомление</b>\n\n{text}\n\n⏰ {timestamp}"
        elif source == "health":
            return f"❤️ <b>Здоровье</b>\n\n{text}\n\n⏰ {timestamp}"
        else:
            return f"📱 <b>{source.title()}</b>\n\n{text}\n\n⏰ {timestamp}"
    
    def _create_voice_notification(self, command: str, response: str, action: str = None) -> str:
        """Создание уведомления о голосовой команде"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        message = f"🎤 <b>Голосовая команда обработана</b>\n\n"
        message += f"📝 <b>Команда:</b> {command}\n"
        message += f"💬 <b>Ответ:</b> {response}\n"
        
        if action:
            message += f"⚡ <b>Действие:</b> {action}\n"
        
        message += f"\n⏰ {timestamp}"
        
        return message
    
    def _format_health_data(self, health_data: Dict[str, Any]) -> str:
        """Форматирование данных о здоровье"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        message = f"❤️ <b>Обновление здоровья</b>\n\n"
        
        if "heart_rate" in health_data:
            message += f"💓 <b>Пульс:</b> {health_data['heart_rate']} уд/мин\n"
        
        if "steps" in health_data:
            message += f"👟 <b>Шаги:</b> {health_data['steps']}\n"
        
        if "calories" in health_data:
            message += f"🔥 <b>Калории:</b> {health_data['calories']}\n"
        
        if "stress" in health_data:
            message += f"😰 <b>Стресс:</b> {health_data['stress']}%\n"
        
        if "sleep" in health_data:
            message += f"😴 <b>Сон:</b> {health_data['sleep']} часов\n"
        
        message += f"\n⏰ {timestamp}"
        
        return message
    
    def _format_progress_data(self, progress_data: Dict[str, Any]) -> str:
        """Форматирование данных о прогрессе"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        message = f"📊 <b>Отчет о прогрессе</b>\n\n"
        
        if "habits_completed" in progress_data:
            message += f"✅ <b>Привычки:</b> {progress_data['habits_completed']}/{progress_data.get('habits_total', 0)}\n"
        
        if "tasks_completed" in progress_data:
            message += f"📋 <b>Задачи:</b> {progress_data['tasks_completed']}/{progress_data.get('tasks_total', 0)}\n"
        
        if "reflections_count" in progress_data:
            message += f"💭 <b>Рефлексии:</b> {progress_data['reflections_count']}\n"
        
        if "streak_days" in progress_data:
            message += f"🔥 <b>Серия дней:</b> {progress_data['streak_days']}\n"
        
        message += f"\n⏰ {timestamp}"
        
        return message
    
    async def _send_via_api(self, text: str) -> bool:
        """Отправка сообщения через Telegram API"""
        try:
            import httpx
            
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_notification": False
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("ok", False)
                else:
                    logger.error(f"Ошибка API Telegram: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Ошибка отправки через API: {e}")
            return False
    
    async def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """Получение информации о боте"""
        if not self.enabled:
            return None
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/getMe")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return data.get("result", {})
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о боте: {e}")
            return None

# Глобальный экземпляр для использования в других модулях
telegram_integration = None

async def initialize_telegram_integration(bot_token: str, chat_id: str):
    """Инициализация глобального экземпляра интеграции с Telegram"""
    global telegram_integration
    telegram_integration = TelegramIntegration(bot_token, chat_id)
    await telegram_integration.initialize()
    return telegram_integration

async def send_message(text: str, source: str = "watch_voice") -> bool:
    """Отправка сообщения через глобальный экземпляр"""
    if telegram_integration:
        return await telegram_integration.send_message(text, source)
    return False

async def send_voice_notification(command: str, response: str, action: str = None) -> bool:
    """Отправка уведомления о голосовой команде через глобальный экземпляр"""
    if telegram_integration:
        return await telegram_integration.send_voice_notification(command, response, action)
    return False 