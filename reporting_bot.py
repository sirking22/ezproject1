#!/usr/bin/env python3
"""
🤖 REPORTING BOT - Интеграция отчетов с Notion
Принимает отчеты о работе и связывает их с задачами в Notion
"""

import os
import re
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

from services.designer_report_service import DesignerReportService
from services.notion_bot_service import NotionBotService

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ReportingBot:
    """Бот для приема отчетов и интеграции с Notion"""
    
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.cloudflare_proxy = os.getenv("CLOUDFLARE_PROXY")
        
        if not self.telegram_token or not self.notion_token:
            raise ValueError("❌ Отсутствуют обязательные токены TELEGRAM_BOT_TOKEN или NOTION_TOKEN")
        
        # Инициализируем сервисы
        self.report_service = DesignerReportService()
        self.notion_service = NotionBotService()
        
        # Состояния пользователей
        self.user_states = {}
        
        logger.info(f"✅ ReportingBot инициализирован: Telegram={bool(self.telegram_token)}, Notion={bool(self.notion_token)}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        if not user:
            await update.message.reply_text("❌ Ошибка получения пользователя")
            return
            
        welcome_text = f"""
🎯 **REPORTING BOT** - Система отчетов

Привет, {user.first_name or 'Пользователь'}! 

**Как использовать:**
• `/report` - Создать отчет о работе
• `/tasks` - Показать активные задачи
• `/help` - Помощь

**Формат отчета:**
```
Потратил 2 часа на дизайн логотипа
Ссылка: https://figma.com/file/...
Статус: В процессе
```

**Или просто напишите отчет:**
"Потратил 1.5 часа на верстку, сделал главную страницу"
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Создать отчет", callback_data="create_report")],
            [InlineKeyboardButton("📋 Активные задачи", callback_data="show_tasks")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📚 **ПОМОЩЬ ПО REPORTING BOT**

**Команды:**
• `/start` - Главное меню
• `/report` - Создать отчет
• `/tasks` - Показать задачи
• `/help` - Эта справка

**Формат отчета:**
```
Время: 2.5 часа
Задача: Дизайн логотипа
Описание: Создал варианты логотипа
Ссылки: https://figma.com/file/...
Статус: Завершено
```

**Автоматическое распознавание:**
• Время: "потратил 2 часа", "работал 1.5ч"
• Ссылки: Figma, LightShot, Yandex.Disk
• Статус: "завершено", "в процессе", "проблемы"

**Примеры:**
• "Потратил 3 часа на дизайн, сделал макет"
• "Работал 1.5ч над логотипом, готово"
• "2 часа верстка, есть проблемы с адаптивом"
        """
        
        if update.message:
            await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /report"""
        if not update.effective_user:
            if update.message:
                await update.message.reply_text("❌ Ошибка получения пользователя")
            return
            
        user_id = update.effective_user.id
        
        # Устанавливаем состояние ожидания отчета
        self.user_states[user_id] = "waiting_report"
        
        # Получаем активные задачи для выбора
        tasks = await self._get_active_tasks()
        
        if tasks:
            keyboard = []
            for task in tasks[:5]:  # Показываем первые 5 задач
                task_title = task.get('title', 'Без названия')[:30]
                keyboard.append([InlineKeyboardButton(
                    f"📋 {task_title}", 
                    callback_data=f"select_task_{task['id']}"
                )])
            
            keyboard.append([InlineKeyboardButton("❌ Без привязки к задаче", callback_data="no_task")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.message:
                await update.message.reply_text(
                    "📝 **Создание отчета**\n\nВыберите задачу или напишите отчет:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        else:
            if update.message:
                await update.message.reply_text(
                    "📝 **Создание отчета**\n\nНапишите ваш отчет:",
                    parse_mode='Markdown'
                )
    
    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /tasks"""
        tasks = await self._get_active_tasks()
        
        if not tasks:
            await update.message.reply_text("📋 Активных задач не найдено")
            return
        
        tasks_text = "📋 **АКТИВНЫЕ ЗАДАЧИ:**\n\n"
        
        for i, task in enumerate(tasks[:10], 1):
            title = task.get('title', 'Без названия')
            status = task.get('status', 'Неизвестно')
            priority = task.get('priority', 'Обычная')
            
            tasks_text += f"{i}. **{title}**\n"
            tasks_text += f"   Статус: {status} | Приоритет: {priority}\n\n"
        
        keyboard = [[InlineKeyboardButton("📝 Создать отчет", callback_data="create_report")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(tasks_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "create_report":
            await self.report_command(update, context)
        
        elif data == "show_tasks":
            await self.tasks_command(update, context)
        
        elif data == "help":
            await self.help_command(update, context)
        
        elif data.startswith("select_task_"):
            task_id = data.replace("select_task_", "")
            self.user_states[user_id] = f"waiting_report_task_{task_id}"
            
            await query.edit_message_text(
                f"📝 **Создание отчета**\n\nВыбрана задача: {task_id}\n\nНапишите ваш отчет:",
                parse_mode='Markdown'
            )
        
        elif data == "no_task":
            self.user_states[user_id] = "waiting_report"
            
            await query.edit_message_text(
                "📝 **Создание отчета**\n\nНапишите ваш отчет:",
                parse_mode='Markdown'
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Проверяем состояние пользователя
        user_state = self.user_states.get(user_id)
        
        if user_state and user_state.startswith("waiting_report"):
            await self._process_report(update, text, user_state)
        else:
            # Автоматическое распознавание отчета
            if self._is_likely_report(text):
                await self._process_report(update, text, "auto_report")
            else:
                await update.message.reply_text(
                    "💡 Напишите `/report` для создания отчета или `/help` для справки"
                )
    
    def _is_likely_report(self, text: str) -> bool:
        """Определяет, похоже ли сообщение на отчет"""
        text_lower = text.lower()
        
        # Ключевые слова для отчетов
        report_keywords = [
            'потратил', 'работал', 'часов', 'часа', 'час', 'минут',
            'сделал', 'завершил', 'готово', 'проблемы', 'готов',
            'дизайн', 'верстка', 'код', 'макет', 'логотип'
        ]
        
        # Проверяем наличие ключевых слов
        has_keywords = any(keyword in text_lower for keyword in report_keywords)
        
        # Проверяем наличие времени
        time_patterns = [
            r'\d+\s*(?:час|часа|часов|ч|минут|мин)',
            r'\d+\.\d+\s*(?:час|часа|часов|ч)'
        ]
        has_time = any(re.search(pattern, text_lower) for pattern in time_patterns)
        
        # Проверяем наличие ссылок
        has_links = bool(re.search(r'https?://', text))
        
        return has_keywords or has_time or has_links
    
    async def _process_report(self, update: Update, text: str, user_state: str):
        """Обрабатывает отчет пользователя"""
        user_id = update.effective_user.id
        
        try:
            # Парсим отчет
            report_data = self.report_service.parse_report(text)
            
            # Определяем связанную задачу
            task_id = None
            if user_state.startswith("waiting_report_task_"):
                task_id = user_state.replace("waiting_report_task_", "")
            else:
                # Ищем задачу по ключевым словам
                task_id = await self._find_related_task(report_data)
            
            # Создаем отчет в Notion
            report_result = await self._create_notion_report(report_data, task_id)
            
            # Формируем ответ
            response_text = self._format_report_response(report_data, report_result)
            
            # Очищаем состояние пользователя
            self.user_states.pop(user_id, None)
            
            await update.message.reply_text(response_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ошибка обработки отчета: {e}")
            await update.message.reply_text(
                f"❌ Ошибка обработки отчета: {str(e)}\n\nПопробуйте еще раз или используйте `/help`"
            )
    
    async def _get_active_tasks(self) -> List[Dict[str, Any]]:
        """Получает активные задачи из Notion"""
        try:
            # ID базы задач
            tasks_db_id = os.getenv("DESIGN_TASKS_DB", "d09df250-ce7e-4e0d-9fbe-4e036d320def")
            
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            # Запрос активных задач
            query_payload = {
                "filter": {
                    "and": [
                        {
                            "property": "Status",
                            "select": {
                                "does_not_equal": "Завершено"
                            }
                        },
                        {
                            "property": "Status",
                            "select": {
                                "does_not_equal": "Отменено"
                            }
                        }
                    ]
                },
                "sorts": [
                    {
                        "property": "Priority",
                        "direction": "descending"
                    }
                ],
                "page_size": 10
            }
            
            url = f"{self.cloudflare_proxy}/v1/databases/{tasks_db_id}/query"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=query_payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        tasks = []
                        
                        for result in data.get('results', []):
                            properties = result.get('properties', {})
                            
                            # Извлекаем название
                            name_prop = properties.get('Name', {}).get('title', [])
                            title = name_prop[0].get('plain_text', 'Без названия') if name_prop else 'Без названия'
                            
                            # Извлекаем статус
                            status_prop = properties.get('Status', {}).get('select', {})
                            status = status_prop.get('name', 'Неизвестно') if status_prop else 'Неизвестно'
                            
                            # Извлекаем приоритет
                            priority_prop = properties.get('Priority', {}).get('select', {})
                            priority = priority_prop.get('name', 'Обычная') if priority_prop else 'Обычная'
                            
                            tasks.append({
                                'id': result['id'],
                                'title': title,
                                'status': status,
                                'priority': priority
                            })
                        
                        return tasks
                    else:
                        logger.error(f"Ошибка получения задач: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Ошибка получения задач: {e}")
            return []
    
    async def _find_related_task(self, report_data: Dict[str, Any]) -> Optional[str]:
        """Ищет связанную задачу по ключевым словам"""
        try:
            tasks = await self._get_active_tasks()
            
            if not tasks:
                return None
            
            # Ключевые слова из отчета
            report_text = f"{report_data.get('description', '')} {report_data.get('title', '')}".lower()
            
            # Ищем совпадения
            for task in tasks:
                task_title = task['title'].lower()
                
                # Простое сравнение по ключевым словам
                if any(word in task_title for word in report_text.split() if len(word) > 3):
                    return task['id']
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка поиска связанной задачи: {e}")
            return None
    
    async def _create_notion_report(self, report_data: Dict[str, Any], task_id: Optional[str]) -> Dict[str, Any]:
        """Создает отчет в Notion"""
        try:
            # ID базы отчетов (создаем если нет)
            reports_db_id = os.getenv("REPORTS_DB", "reports_database_id")
            
            headers = {
                "Authorization": f"Bearer {self.notion_token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            # Подготавливаем данные для создания записи
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": report_data.get('title', 'Отчет о работе')
                            }
                        }
                    ]
                },
                "Description": {
                    "rich_text": [
                        {
                            "text": {
                                "content": report_data.get('description', '')
                            }
                        }
                    ]
                },
                "Time Spent": {
                    "number": report_data.get('time_spent', 0)
                },
                "Status": {
                    "select": {
                        "name": report_data.get('status', 'В процессе')
                    }
                },
                "Date": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }
            
            # Добавляем связанную задачу
            if task_id:
                properties["Related Task"] = {
                    "relation": [
                        {
                            "id": task_id
                        }
                    ]
                }
            
            # Добавляем материалы
            materials = report_data.get('materials', [])
            if materials:
                properties["Materials"] = {
                    "url": materials[0] if materials else ""
                }
            
            payload = {
                "parent": {
                    "database_id": reports_db_id
                },
                "properties": properties
            }
            
            url = f"{self.cloudflare_proxy}/v1/pages"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "page_id": result['id'],
                            "url": result.get('url', '')
                        }
                    else:
                        logger.error(f"Ошибка создания отчета: {response.status}")
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Ошибка создания отчета: {e}")
            return {"success": False, "error": str(e)}
    
    def _format_report_response(self, report_data: Dict[str, Any], report_result: Dict[str, Any]) -> str:
        """Формирует ответ на отчет"""
        response = "✅ **ОТЧЕТ СОЗДАН**\n\n"
        
        # Основная информация
        response += f"📝 **Описание:** {report_data.get('description', 'Не указано')}\n"
        response += f"⏱️ **Время:** {report_data.get('time_spent', 0)} часов\n"
        response += f"📊 **Статус:** {report_data.get('status', 'Не указан')}\n"
        
        # Материалы
        materials = report_data.get('materials', [])
        if materials:
            response += f"🔗 **Материалы:** {len(materials)} ссылок\n"
        
        # Результат создания
        if report_result.get('success'):
            response += f"📄 **Создано в Notion:** [Открыть]({report_result.get('url', '')})\n"
        else:
            response += f"❌ **Ошибка создания:** {report_result.get('error', 'Неизвестно')}\n"
        
        response += "\n🎯 Отчет сохранен и связан с задачей"
        
        return response
    
    def run(self):
        """Запускает бота"""
        application = Application.builder().token(self.telegram_token).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("report", self.report_command))
        application.add_handler(CommandHandler("tasks", self.tasks_command))
        
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        logger.info("🚀 ReportingBot запущен")
        
        # Запускаем бота синхронно
        application.run_polling()

def main():
    """Главная функция"""
    try:
        bot = ReportingBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main() 