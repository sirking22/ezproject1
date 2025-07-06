import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../shared_code')))

from integrations.notion import NotionClient
from integrations.yandex_cloud import YandexCloudClient
from utils.logging_utils import get_logger

logger = get_logger("life_bot.learning")
notion = NotionClient()
yandex = YandexCloudClient()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ....models.base import LearningProgress
from ....repositories.notion_repository import NotionLearningRepository
from datetime import datetime
from ....utils.date_utils import calculate_next_review
from typing import Optional

class LearningHandler:
    """Handler for learning-related commands"""
    
    def __init__(self, learning_repository: NotionLearningRepository):
        self.learning_repository = learning_repository
    
    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /learn command"""
        keyboard = [
            [
                InlineKeyboardButton("📚 Начать обучение", callback_data="learn_start"),
                InlineKeyboardButton("📋 Мой прогресс", callback_data="learn_progress")
            ],
            [
                InlineKeyboardButton("🔄 На повторение", callback_data="learn_review"),
                InlineKeyboardButton("📊 Статистика", callback_data="learn_stats")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📚 Управление обучением\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
    
    async def start_learning(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start learning session"""
        # Получаем задачи, которые нужно изучить
        tasks = await self.learning_repository.list({
            "status": {"equals": "Not Started"}
        })
        
        if not tasks:
            await update.callback_query.message.reply_text(
                "У вас нет новых материалов для изучения! "
                "Добавьте новые задачи через команду /task"
            )
            return
        
        # Берем первую задачу
        current_task = tasks[0]
        
        # Создаем клавиатуру для оценки уверенности
        keyboard = [
            [
                InlineKeyboardButton("😕 Не уверен (20%)", callback_data="confidence_20"),
                InlineKeyboardButton("🤔 Частично (40%)", callback_data="confidence_40")
            ],
            [
                InlineKeyboardButton("👍 Хорошо (70%)", callback_data="confidence_70"),
                InlineKeyboardButton("💪 Отлично (95%)", callback_data="confidence_95")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Сохраняем текущую задачу в контексте
        context.user_data["current_learning_task"] = current_task.id
        
        await update.callback_query.message.reply_text(
            f"📚 *Изучаем новый материал*\n\n"
            f"Задача: *{current_task.title}*\n"
            f"Описание: {current_task.description or 'Нет описания'}\n\n"
            f"Оцените ваш уровень понимания материала:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def handle_confidence_rating(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle confidence rating selection"""
        query = update.callback_query
        confidence = int(query.data.split("_")[1])
        task_id = context.user_data.get("current_learning_task")
        
        if not task_id:
            await query.message.reply_text("Ошибка: не найдена текущая задача")
            return
        
        # Создаем запись о прогрессе
        progress = LearningProgress(
            id="",  # ID будет присвоен Notion
            task_id=task_id,
            status="In Progress",
            last_review=datetime.utcnow(),
            next_review=calculate_next_review(confidence),
            confidence_level=confidence,
            notes=None
        )
        
        # Сохраняем в Notion
        created_progress = await self.learning_repository.create(progress)
        
        # Очищаем контекст
        context.user_data.pop("current_learning_task", None)
        
        # Формируем сообщение о следующем повторении
        next_review = created_progress.next_review
        next_review_text = (
            f"Следующее повторение: {next_review.strftime('%d.%m.%Y')}"
            if next_review else "Повторение не требуется"
        )
        
        await query.message.reply_text(
            f"✅ Прогресс сохранен!\n\n"
            f"Уровень уверенности: {confidence}%\n"
            f"{next_review_text}\n\n"
            "Хотите продолжить обучение? Используйте команду /learn"
        )
    
    async def show_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show learning progress"""
        # Получаем все записи о прогрессе
        progress_records = await self.learning_repository.list()
        
        if not progress_records:
            await update.callback_query.message.reply_text(
                "У вас пока нет записей о прогрессе обучения. "
                "Начните обучение с помощью команды /learn"
            )
            return
        
        # Группируем по уровню уверенности
        confidence_groups = {
            "Начальный (0-30%)": 0,
            "Средний (31-60%)": 0,
            "Хороший (61-85%)": 0,
            "Отличный (86-100%)": 0
        }
        
        for record in progress_records:
            conf = record.confidence_level
            if conf <= 30:
                confidence_groups["Начальный (0-30%)"] += 1
            elif conf <= 60:
                confidence_groups["Средний (31-60%)"] += 1
            elif conf <= 85:
                confidence_groups["Хороший (61-85%)"] += 1
            else:
                confidence_groups["Отличный (86-100%)"] += 1
        
        # Формируем сообщение
        message = "📊 *Ваш прогресс в обучении*\n\n"
        for group, count in confidence_groups.items():
            message += f"{group}: {count} тем\n"
        
        message += f"\nВсего тем: {len(progress_records)}"
        
        await update.callback_query.message.reply_text(
            message,
            parse_mode="Markdown"
        )
    
    async def show_review_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show tasks that need review"""
        now = datetime.utcnow()
        
        # Получаем задачи на повторение
        progress_records = await self.learning_repository.list({
            "next_review": {"before": now.isoformat()}
        })
        
        if not progress_records:
            await update.callback_query.message.reply_text(
                "У вас нет материалов для повторения! "
                "Все ваши знания свежи в памяти 🎉"
            )
            return
        
        message = "🔄 *Материалы для повторения:*\n\n"
        for i, record in enumerate(progress_records, 1):
            message += (
                f"{i}. Задача: *{record.task_id}*\n"
                f"   Последнее повторение: {record.last_review.strftime('%d.%m.%Y')}\n"
                f"   Уверенность: {record.confidence_level}%\n\n"
            )
        
        keyboard = [[
            InlineKeyboardButton("📚 Начать повторение", callback_data="learn_start_review")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        ) 