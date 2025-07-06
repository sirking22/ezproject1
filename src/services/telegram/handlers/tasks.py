#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ОБРАБОТЧИК ЗАДАЧ С ЧЕКЛИСТАМИ

Интеграция упрощенной системы чеклистов в Telegram бота.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from ....models.base import Task
from ....repositories.notion_repository import NotionTaskRepository
from datetime import datetime
from typing import Optional, List

from ...checklist_service import checklist_service
from ...base_service import BaseService

logger = logging.getLogger(__name__)

class TaskHandler(BaseService):
    """Обработчик задач с автоматическим созданием чеклистов"""
    
    def __init__(self, task_repository: NotionTaskRepository):
        super().__init__()
        self.task_repository = task_repository
        self.checklist_service = checklist_service
        self.MAX_MESSAGE_LENGTH = 2048  # Reduced from 4096 to be safer
        self.STATUS_ICONS = {
            "Not Started": "🔵",
            "In Progress": "🟡",
            "Completed": "🟢",
            "Cancelled": "🔴"
        }
        logger.info("TaskHandler initialized")
    
    def _get_status_icon(self, status: str) -> str:
        """Get status icon for given status"""
        return self.STATUS_ICONS.get(status, "⚪")
    
    async def start_task_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Начинает процесс создания задачи"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Создать задачу", callback_data="create_task")],
            [InlineKeyboardButton("📋 Создать с чеклистом", callback_data="create_task_with_checklist")],
            [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 **Создание задачи**\n\n"
            "Выберите тип создания:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return 1
    
    async def handle_task_creation_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает выбор типа создания задачи"""
        
        query = update.callback_query
        if query is None:
            return ConversationHandler.END
            
        await query.answer()
        
        if query.data == "create_task":
            await query.edit_message_text(
                "📝 **Создание обычной задачи**\n\n"
                "Отправьте название задачи:"
            )
            context.user_data['task_type'] = 'simple'
            return 2
            
        elif query.data == "create_task_with_checklist":
            await query.edit_message_text(
                "📋 **Создание задачи с чеклистом**\n\n"
                "Отправьте название задачи.\n"
                "Система автоматически создаст чеклисты из связанных гайдов:"
            )
            context.user_data['task_type'] = 'with_checklist'
            return 2
            
        elif query.data == "cancel":
            await query.edit_message_text("❌ Создание задачи отменено")
            return ConversationHandler.END
        
        return ConversationHandler.END
    
    async def handle_task_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает название задачи"""
        
        if update.message is None or update.message.text is None:
            return ConversationHandler.END
            
        task_title = update.message.text
        context.user_data['task_title'] = task_title
        
        await update.message.reply_text(
            f"📝 **Название задачи:** {task_title}\n\n"
            "Теперь отправьте описание задачи (или /skip для пропуска):"
        )
        
        return 3
    
    async def handle_task_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обрабатывает описание задачи"""
        
        if update.message is None or update.message.text is None:
            return ConversationHandler.END
        
        if update.message.text == "/skip":
            context.user_data['task_description'] = ""
        else:
            context.user_data['task_description'] = update.message.text
        
        # Создаем задачу
        task_id = await self.create_task(context.user_data)
        
        if task_id:
            task_type = context.user_data.get('task_type', 'simple')
            
            if task_type == 'with_checklist':
                # Создаем чеклисты
                checklists_count = await self.checklist_service.process_task_creation(task_id)
                
                if checklists_count > 0:
                    await update.message.reply_text(
                        f"✅ **Задача создана с чеклистами!**\n\n"
                        f"📝 Название: {context.user_data['task_title']}\n"
                        f"📋 Создано чеклистов: {checklists_count}\n"
                        f"🔗 ID задачи: `{task_id}`",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        f"✅ **Задача создана!**\n\n"
                        f"📝 Название: {context.user_data['task_title']}\n"
                        f"ℹ️ Чеклисты не созданы (нет связанных гайдов)\n"
                        f"🔗 ID задачи: `{task_id}`",
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text(
                    f"✅ **Задача создана!**\n\n"
                    f"📝 Название: {context.user_data['task_title']}\n"
                    f"🔗 ID задачи: `{task_id}`",
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text("❌ Ошибка создания задачи")
        
        return ConversationHandler.END
    
    async def create_task(self, task_data: dict) -> Optional[str]:
        """Создает задачу в Notion"""
        
        try:
            # Создаем задачу
            task_properties = {
                "Name": {
                    "title": [{"text": {"content": task_data['task_title']}}]
                },
                "Статус": {
                    "status": {"name": "To do"}
                },
                "Приоритет": {
                    "select": {"name": "Средний"}
                }
            }
            
            # Добавляем описание если есть
            if task_data.get('task_description'):
                task_properties["Описание"] = {
                    "rich_text": [{"text": {"content": task_data['task_description']}}]
                }
            
            response = await self.checklist_service.client.pages.create(
                parent={"database_id": self.checklist_service.databases['tasks']},
                properties=task_properties
            )
            
            return response['id']
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания задачи: {e}")
            return None
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Отменяет создание задачи"""
        
        await update.callback_query.edit_message_text("❌ Создание задачи отменено")
        return ConversationHandler.END
    
    async def task_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /task command"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("📝 Создать задачу", callback_data="task_create"),
                    InlineKeyboardButton("📋 Мои задачи", callback_data="task_list")
                ],
                [
                    InlineKeyboardButton("🔍 Найти задачу", callback_data="task_search"),
                    InlineKeyboardButton("📊 Статистика", callback_data="task_stats")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🎯 Управление задачами\n\n"
                "Выберите действие:",
                reply_markup=reply_markup
            )
            logger.debug("Task command menu displayed")
        except Exception as e:
            logger.error(f"Error in task_command: {str(e)}")
            await update.message.reply_text(
                "❌ Произошла ошибка при отображении меню. Попробуйте позже."
            )

    def _format_task_message(self, tasks: List[Task], start_idx: int = 0) -> tuple[str, bool]:
        """Format tasks into a message, returning the message and whether there are more tasks"""
        try:
            logger.info(f"Formatting tasks starting from index {start_idx}")
            message = "📋 Ваши задачи:\n\n"
            current_length = len(message)
            tasks_added = 0
            
            for i, task in enumerate(tasks[start_idx:], start_idx + 1):
                logger.debug(f"Formatting task {i}: {task.title}")
                # Basic task info
                task_line = f"{i}. {self._get_status_icon(task.status)} "
                
                # Add priority
                priority_map = {"High": "🔥", "Medium": "⚡", "Low": "📎"}
                task_line += f"{priority_map.get(task.priority, '📎')} "
                
                # Add title (required)
                task_line += f"*{task.title}*\n"
                
                # Add description (optional)
                if task.description:
                    desc = task.description[:100] + "..." if len(task.description) > 100 else task.description
                    task_line += f"{desc}\n"
                
                # Add tags (optional)
                if task.tags:
                    tags_text = " ".join([f"#{tag}" for tag in task.tags])
                    task_line += f"🏷️ {tags_text}\n"
                
                # Add dates (optional)
                if task.due_date:
                    task_line += f"📅 До {task.due_date.strftime('%d.%m.%Y')}\n"
                if task.completed_at:
                    task_line += f"✅ Завершено {task.completed_at.strftime('%d.%m.%Y')}\n"
                
                # Add separator
                task_line += "➖➖➖➖➖➖➖➖➖➖\n"
                
                # Check message length
                if current_length + len(task_line) > self.MAX_MESSAGE_LENGTH:
                    logger.info("Message length limit reached")
                    return message, True
                
                message += task_line
                current_length += len(task_line)
                tasks_added += 1
                
                # Check chunk size
                if tasks_added >= 5:  # Reduced from 10 to 5 for better readability
                    logger.info("Chunk size limit reached")
                    return message, True
            
            # Add navigation hint if there are more tasks
            if start_idx + tasks_added < len(tasks):
                message += "\n👉 Используйте кнопки навигации ниже"
                return message, True
                
            logger.info(f"Formatted {tasks_added} tasks successfully")
            return message, False
            
        except Exception as e:
            logger.error(f"Error formatting task message: {str(e)}", exc_info=True)
            return "❌ Ошибка при форматировании сообщения", False
            
    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List user's tasks"""
        try:
            # Get page from context or default to 0
            page = context.user_data.get("task_list_page", 0)
            
            logger.info("Starting task listing process...")
            logger.info(f"Using database ID: {self.task_repository.database_id}")
            
            # Validate database first
            is_valid, error_msg = await self.task_repository.validate_database()
            if not is_valid:
                logger.error(f"Database validation failed: {error_msg}")
                await update.callback_query.message.reply_text(
                    f"❌ Ошибка подключения к базе данных Notion:\n\n{error_msg}\n\n"
                    "Пожалуйста:\n"
                    "1. Проверьте ID базы данных\n"
                    "2. Убедитесь, что интеграция имеет доступ к базе\n"
                    "3. Проверьте структуру базы данных"
                )
                await update.callback_query.answer()
                return
            
            # Get all non-completed tasks
            logger.info("Fetching tasks from Notion...")
            tasks = await self.task_repository.list({
                "status": {"not_equals": "Completed"}
            })
            logger.info(f"Fetched {len(tasks)} tasks from Notion")
            
            if not tasks:
                logger.info("No tasks found in database")
                await update.callback_query.message.reply_text(
                    "У вас пока нет активных задач! Создайте новую задачу командой /task\n\n"
                    "Подключение к базе данных Notion успешно установлено, "
                    "но активных задач не найдено."
                )
                await update.callback_query.answer()
                return
                
            # Sort tasks
            logger.info("Sorting tasks...")
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            status_order = {"In Progress": 0, "Not Started": 1, "Cancelled": 2}
            
            tasks.sort(key=lambda x: (
                priority_order.get(x.priority, 3),
                status_order.get(x.status, 3),
                x.due_date or datetime.max
            ))
            
            logger.info(f"Sorted {len(tasks)} tasks")
            
            # Format message
            logger.info("Formatting task message...")
            message, has_more = self._format_task_message(tasks, page * 5)
            logger.info(f"Formatted message, has_more: {has_more}")
            
            # Create navigation buttons if needed
            keyboard = []
            if page > 0:
                keyboard.append(InlineKeyboardButton("⬅️ Назад", callback_data="task_list_prev"))
            if has_more:
                keyboard.append(InlineKeyboardButton("➡️ Далее", callback_data="task_list_next"))
            
            if keyboard:
                keyboard = [keyboard]  # Wrap in list for proper markup
            keyboard.append([InlineKeyboardButton("🔄 Обновить", callback_data="task_list")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            logger.info("Sending response to user...")
            await update.callback_query.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await update.callback_query.answer()
            logger.info("Task list sent successfully")
            
        except Exception as e:
            logger.error(f"Error in list_tasks: {str(e)}", exc_info=True)
            await update.callback_query.message.reply_text(
                f"❌ Произошла ошибка при получении списка задач:\n{str(e)}\n\nПопробуйте позже или проверьте настройки подключения к Notion."
            )
            await update.callback_query.answer()

    async def update_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show task update options"""
        tasks = await self.task_repository.list({"status": {"equals": "Not Started"}})
        
        if not tasks:
            await update.callback_query.message.reply_text(
                "У вас нет активных задач для обновления."
            )
            await update.callback_query.answer()
            return
            
        keyboard = []
        for task in tasks:
            keyboard.append([
                InlineKeyboardButton(
                    f"📌 {task.title}",
                    callback_data=f"task_update_{task.id}"
                )
            ])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            "Выберите задачу для обновления:",
            reply_markup=reply_markup
        )
        await update.callback_query.answer()

    async def update_task_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle task status update"""
        try:
            query = update.callback_query
            task_id = query.data.split("_")[2]  # Format: task_update_<id>
            
            # Get current task
            task = await self.task_repository.get(task_id)
            if not task:
                await query.answer("❌ Задача не найдена")
                return
                
            # Create keyboard with status options
            statuses = ["Not Started", "In Progress", "Completed", "Cancelled"]
            keyboard = []
            for status in statuses:
                if status != task.status:  # Don't show current status
                    status_icon = self._get_status_icon(status)
                    keyboard.append([
                        InlineKeyboardButton(
                            f"{status_icon} {status}",
                            callback_data=f"task_status_{task_id}_{status}"
                        )
                    ])
                    
            keyboard.append([
                InlineKeyboardButton("↩️ Назад", callback_data="task_list")
            ])
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            current_status_icon = self._get_status_icon(task.status)
            
            await query.message.reply_text(
                f"📌 Задача: *{task.title}*\n"
                f"Текущий статус: {current_status_icon} {task.status}\n\n"
                f"Выберите новый статус:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await query.answer()
            logger.debug(f"Status update options displayed for task {task_id}")
        except Exception as e:
            logger.error(f"Error in update_task_status: {str(e)}")
            await update.callback_query.message.reply_text(
                "❌ Произошла ошибка при обновлении статуса. Попробуйте позже."
            )
            await update.callback_query.answer()

    async def handle_status_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle status change confirmation"""
        try:
            query = update.callback_query
            _, _, task_id, new_status = query.data.split("_")  # Format: task_status_<id>_<status>
            
            # Get current task
            task = await self.task_repository.get(task_id)
            if not task:
                await query.answer("❌ Задача не найдена")
                return
                
            old_status = task.status
            old_icon = self._get_status_icon(old_status)
            new_icon = self._get_status_icon(new_status)
            
            # Update task status and metadata
            updated_task_data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": new_status,
                "due_date": task.due_date,
                "tags": task.tags,
                "priority": task.priority,
                "created_at": task.created_at,
                "updated_at": datetime.now(),
                "completed_at": datetime.now() if new_status == "Completed" else None,
                "cancelled_at": datetime.now() if new_status == "Cancelled" else None,
                "time_estimate": task.time_estimate if hasattr(task, "time_estimate") else None,
                "actual_time": task.actual_time if hasattr(task, "actual_time") else None
            }
            
            # Create new Task object with updated data
            updated_task = Task(**updated_task_data)
            
            # Update task in repository
            result = await self.task_repository.update(task.id, updated_task)
            if not result:
                await query.answer("❌ Ошибка при обновлении статуса")
                return
                
            # Send confirmation message
            confirmation_text = (
                f"✅ Статус задачи обновлен!\n\n"
                f"📌 *{updated_task.title}*\n"
                f"Статус: {old_icon} {old_status} → {new_icon} {new_status}\n"
            )
            
            if new_status == "Completed":
                confirmation_text += f"📅 Завершено: {updated_task.completed_at.strftime('%d.%m.%Y %H:%M')}\n"
            elif new_status == "Cancelled":
                confirmation_text += f"❌ Отменено: {updated_task.cancelled_at.strftime('%d.%m.%Y %H:%M')}\n"
                
            keyboard = [[InlineKeyboardButton("↩️ К списку задач", callback_data="task_list")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                confirmation_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await query.answer("✅ Статус обновлен")
            logger.info(f"Task {task_id} status updated from {old_status} to {new_status}")
        except Exception as e:
            logger.error(f"Error in handle_status_update: {str(e)}")
            await update.callback_query.message.reply_text(
                "❌ Произошла ошибка при обновлении статуса. Попробуйте позже."
            )
            await update.callback_query.answer()

    async def manage_tags(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show task tag management options"""
        tasks = await self.task_repository.list({"status": {"equals": "Not Started"}})
        
        if not tasks:
            await update.callback_query.message.reply_text(
                "У вас нет активных задач для управления тегами."
            )
            await update.callback_query.answer()
            return
            
        keyboard = []
        for task in tasks:
            keyboard.append([
                InlineKeyboardButton(
                    f"🏷 {task.title}",
                    callback_data=f"task_tags_{task.id}"
                )
            ])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            "Выберите задачу для управления тегами:",
            reply_markup=reply_markup
        )
        await update.callback_query.answer()

    async def update_task_tags(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle task tags update"""
        query = update.callback_query
        task_id = query.data.split("_")[2]  # Format: task_tags_<id>
        
        # Get current task
        task = await self.task_repository.get(task_id)
        if not task:
            await query.answer("❌ Задача не найдена")
            return
            
        # Available tags
        available_tags = ["Важно", "Срочно", "Работа", "Учеба", "Личное", "Проект"]
        current_tags = task.tags or []
        
        # Create keyboard with tag options
        keyboard = []
        for tag in available_tags:
            keyboard.append([
                InlineKeyboardButton(
                    f"{'✅' if tag in current_tags else '❌'} {tag}",
                    callback_data=f"task_tag_toggle_{task_id}_{tag}"
                )
            ])
        keyboard.append([
            InlineKeyboardButton("✅ Готово", callback_data=f"task_tags_done_{task_id}")
        ])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"🏷 Управление тегами задачи:\n"
            f"*{task.title}*\n\n"
            f"Текущие теги: {', '.join(current_tags) if current_tags else 'нет'}\n"
            f"Нажмите на тег чтобы добавить/убрать его:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        await query.answer()

    async def toggle_task_tag(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle tag for a task"""
        query = update.callback_query
        _, _, _, task_id, tag = query.data.split("_")  # Format: task_tag_toggle_<id>_<tag>
        
        # Get current task
        task = await self.task_repository.get(task_id)
        if not task:
            await query.answer("❌ Задача не найдена")
            return
            
        # Toggle tag
        current_tags = task.tags or []
        if tag in current_tags:
            current_tags.remove(tag)
            await query.answer(f"Тег '{tag}' убран")
        else:
            current_tags.append(tag)
            await query.answer(f"Тег '{tag}' добавлен")
            
        # Update task
        task.tags = current_tags
        await self.task_repository.update(task)
        
        # Update keyboard
        available_tags = ["Важно", "Срочно", "Работа", "Учеба", "Личное", "Проект"]
        keyboard = []
        for t in available_tags:
            keyboard.append([
                InlineKeyboardButton(
                    f"{'✅' if t in current_tags else '❌'} {t}",
                    callback_data=f"task_tag_toggle_{task_id}_{t}"
                )
            ])
        keyboard.append([
            InlineKeyboardButton("✅ Готово", callback_data=f"task_tags_done_{task_id}")
        ])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"🏷 Управление тегами задачи:\n"
            f"*{task.title}*\n\n"
            f"Текущие теги: {', '.join(current_tags) if current_tags else 'нет'}\n"
            f"Нажмите на тег чтобы добавить/убрать его:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    async def finish_task_tags(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finish tag management"""
        query = update.callback_query
        _, _, _, task_id = query.data.split("_")  # Format: task_tags_done_<id>
        
        # Get current task
        task = await self.task_repository.get(task_id)
        if not task:
            await query.answer("❌ Задача не найдена")
            return
            
        await query.message.edit_text(
            f"✅ Теги задачи обновлены!\n\n"
            f"📌 *{task.title}*\n"
            f"🏷 Теги: {', '.join(task.tags) if task.tags else 'нет'}",
            parse_mode="Markdown"
        )
        await query.answer("Теги сохранены")

    async def filter_by_tags(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show tag filter options"""
        # Get all tasks to collect unique tags
        tasks = await self.task_repository.list({})
        all_tags = set()
        for task in tasks:
            all_tags.update(task.tags)
            
        if not all_tags:
            await update.callback_query.message.reply_text(
                "❌ Нет доступных тегов для фильтрации."
            )
            await update.callback_query.answer()
            return
            
        # Create keyboard with tag options
        keyboard = []
        for tag in sorted(all_tags):
            keyboard.append([
                InlineKeyboardButton(
                    f"#{tag}",
                    callback_data=f"task_filter_apply_{tag}"
                )
            ])
            
        keyboard.append([
            InlineKeyboardButton("↩️ Назад", callback_data="task_list")
        ])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            "🏷 Выберите тег для фильтрации задач:",
            reply_markup=reply_markup
        )
        await update.callback_query.answer()

    async def apply_tag_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Apply selected tag filter"""
        query = update.callback_query
        tag = query.data.split("_")[3]  # Format: task_filter_apply_<tag>
        
        # Get tasks with selected tag
        tasks = await self.task_repository.list({
            "tags": {"contains": tag},
            "status": {"not_equals": "Completed"}
        })
        
        if not tasks:
            keyboard = [[InlineKeyboardButton("↩️ Назад", callback_data="task_filter_tags")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                f"❌ Нет активных задач с тегом #{tag}",
                reply_markup=reply_markup
            )
            await query.answer()
            return
            
        # Sort tasks
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        status_order = {"In Progress": 0, "Not Started": 1, "Cancelled": 2}
        
        tasks.sort(key=lambda x: (
            priority_order.get(x.priority, 3),
            status_order.get(x.status, 3),
            x.due_date or datetime.max
        ))
        
        # Send tasks in chunks
        start_idx = 0
        while start_idx < len(tasks):
            message, has_more = self._format_task_message(tasks, start_idx)
            
            # Add action buttons to the last message
            if not has_more:
                keyboard = [
                    [
                        InlineKeyboardButton("🔄 Сбросить фильтр", callback_data="task_list"),
                        InlineKeyboardButton("🏷 Другой тег", callback_data="task_filter_tags")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(
                    f"🔍 Задачи с тегом #{tag}:\n\n" + message[message.find("\n\n") + 2:],
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            else:
                await query.message.reply_text(
                    message,
                    parse_mode="Markdown"
                )
            
            start_idx += 10
            
        await query.answer()

    async def show_sort_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show task sorting options"""
        keyboard = [
            [
                InlineKeyboardButton("📅 По сроку", callback_data="task_sort_due_date"),
                InlineKeyboardButton("🔥 По приоритету", callback_data="task_sort_priority")
            ],
            [
                InlineKeyboardButton("📊 По статусу", callback_data="task_sort_status"),
                InlineKeyboardButton("📝 По названию", callback_data="task_sort_title")
            ],
            [
                InlineKeyboardButton("↩️ Назад", callback_data="task_list")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            "📊 Выберите способ сортировки:",
            reply_markup=reply_markup
        )
        await update.callback_query.answer()

    async def apply_sort(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Apply selected sorting"""
        query = update.callback_query
        sort_type = query.data.split("_")[2]  # Format: task_sort_<type>
        
        # Get active tasks
        tasks = await self.task_repository.list({
            "status": {"not_equals": "Completed"}
        })
        
        if not tasks:
            await query.message.reply_text("❌ Нет активных задач для сортировки.")
            await query.answer()
            return
            
        # Apply sorting
        if sort_type == "due_date":
            tasks.sort(key=lambda x: x.due_date or datetime.max)
        elif sort_type == "priority":
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            tasks.sort(key=lambda x: priority_order.get(x.priority, 3))
        elif sort_type == "status":
            status_order = {"In Progress": 0, "Not Started": 1, "Cancelled": 2}
            tasks.sort(key=lambda x: status_order.get(x.status, 3))
        else:  # title
            tasks.sort(key=lambda x: x.title.lower())
            
        # Send sorted tasks
        start_idx = 0
        while start_idx < len(tasks):
            message, has_more = self._format_task_message(tasks, start_idx)
            
            # Add action buttons to the last message
            if not has_more:
                keyboard = [
                    [
                        InlineKeyboardButton("📊 Другая сортировка", callback_data="task_sort"),
                        InlineKeyboardButton("↩️ К списку", callback_data="task_list")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                sort_name = {
                    "due_date": "по сроку",
                    "priority": "по приоритету",
                    "status": "по статусу",
                    "title": "по названию"
                }.get(sort_type, "")
                
                await query.message.reply_text(
                    f"📊 Задачи {sort_name}:\n\n" + message[message.find("\n\n") + 2:],
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            else:
                await query.message.reply_text(
                    message,
                    parse_mode="Markdown"
                )
            
            start_idx += 10
            
        await query.answer() 


# Создаем обработчик разговора
def get_task_conversation_handler():
    """Возвращает обработчик разговора для создания задач"""
    
    task_handler = TaskHandler()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('task', task_handler.start_task_creation)],
        states={
            1: [CallbackQueryHandler(task_handler.handle_task_creation_choice)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_handler.handle_task_title)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_handler.handle_task_description)]
        },
        fallbacks=[CallbackQueryHandler(task_handler.cancel, pattern='^cancel$')]
    )
    
    return conv_handler 