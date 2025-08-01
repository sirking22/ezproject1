#!/usr/bin/env python3
"""
🎯 PRODUCT MANAGEMENT BOT
Telegram бот для управления продуктами RAMIT

КОМАНДЫ:
/products - список всех продуктов
/product [артикул] - информация о продукте
/materials [артикул] - материалы продукта
/status [артикул] [статус] - изменение статуса
/analytics - аналитика жизненного цикла
/lifecycle - отчет по жизненному циклу
/overdue - просроченные продукты
/attention - продукты, требующие внимания
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from notion_client import AsyncClient
from dotenv import load_dotenv

# Импортируем менеджер жизненного цикла
from product_lifecycle_manager import ProductLifecycleManager

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/product_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductManagementBot:
    """Telegram бот для управления продуктами"""
    
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.notion = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
        self.product_lines_db = os.getenv("PRODUCT_LINES_DB", "")
        self.lifecycle_manager = ProductLifecycleManager()
        
        # Кэш продуктов (обновляется каждые 5 минут)
        self.products_cache = []
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 минут
        
        # Статистика использования
        self.usage_stats = {
            "commands_used": {},
            "total_requests": 0,
            "last_activity": None
        }

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_message = """
🎯 **PRODUCT MANAGEMENT BOT**
Бот для управления продуктами RAMIT

**Доступные команды:**
📋 `/products` - список всех продуктов
🔍 `/product [артикул]` - информация о продукте
📁 `/materials [артикул]` - материалы продукта
🔄 `/status [артикул] [статус]` - изменение статуса
📊 `/analytics` - аналитика жизненного цикла
📈 `/lifecycle` - отчет по жизненному циклу
⚠️ `/overdue` - просроченные продукты
👀 `/attention` - продукты, требующие внимания

**Примеры:**
`/product RMA-03` - информация о продукте RMA-03
`/status RMA-03 Производство` - перевести в статус "Производство"
`/materials BDM-07` - материалы продукта BDM-07
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        self._update_stats("start")

    async def products_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /products - список всех продуктов"""
        await update.message.reply_text("📦 Загружаю список продуктов...")
        
        try:
            products = await self._get_products()
            
            if not products:
                await update.message.reply_text("❌ Продукты не найдены")
                return
            
            # Группируем по статусам
            products_by_status = {}
            for product in products:
                status = product.get("status", "Неизвестно")
                if status not in products_by_status:
                    products_by_status[status] = []
                products_by_status[status].append(product)
            
            # Формируем сообщение
            message = f"📦 **ВСЕГО ПРОДУКТОВ: {len(products)}**\n\n"
            
            for status, status_products in products_by_status.items():
                message += f"**{status}** ({len(status_products)}):\n"
                for product in status_products[:10]:  # Показываем первые 10
                    article = product.get("article", "")
                    name = product.get("name", "")
                    message += f"• {article} - {name}\n"
                
                if len(status_products) > 10:
                    message += f"• ... и еще {len(status_products) - 10}\n"
                message += "\n"
            
            # Добавляем кнопки для детального просмотра
            keyboard = [
                [InlineKeyboardButton("📊 Аналитика", callback_data="analytics")],
                [InlineKeyboardButton("⚠️ Просроченные", callback_data="overdue")],
                [InlineKeyboardButton("👀 Требуют внимания", callback_data="attention")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            self._update_stats("products")
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения продуктов: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def product_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /product [артикул] - информация о продукте"""
        if not context.args:
            await update.message.reply_text("❌ Укажите артикул продукта\nПример: `/product RMA-03`", parse_mode='Markdown')
            return
        
        article = context.args[0].upper()
        await update.message.reply_text(f"🔍 Ищу продукт {article}...")
        
        try:
            products = await self._get_products()
            product = None
            
            for p in products:
                if p.get("article", "").upper() == article:
                    product = p
                    break
            
            if not product:
                await update.message.reply_text(f"❌ Продукт с артикулом {article} не найден")
                return
            
            # Формируем детальную информацию
            message = f"""
🔍 **ИНФОРМАЦИЯ О ПРОДУКТЕ**

**Артикул:** {product.get('article', '')}
**Название:** {product.get('name', '')}
**Категория:** {product.get('category', '')}
**Статус:** {product.get('status', '')}
**Дата создания:** {self._format_date(product.get('created_time', ''))}

**Действия:**
            """
            
            # Кнопки для действий
            keyboard = [
                [InlineKeyboardButton("📁 Материалы", callback_data=f"materials_{article}")],
                [InlineKeyboardButton("🔄 Изменить статус", callback_data=f"change_status_{article}")],
                [InlineKeyboardButton("📊 Детали", callback_data=f"details_{article}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            self._update_stats("product")
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения продукта: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status [артикул] [статус] - изменение статуса"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Укажите артикул и новый статус\n"
                "Пример: `/status RMA-03 Производство`\n\n"
                "**Доступные статусы:**\n"
                "• Предпроизводство\n"
                "• Производство\n"
                "• Продвижение\n"
                "• Поддержка\n"
                "• Архив",
                parse_mode='Markdown'
            )
            return
        
        article = context.args[0].upper()
        new_status = " ".join(context.args[1:])
        
        await update.message.reply_text(f"🔄 Изменяю статус продукта {article} на '{new_status}'...")
        
        try:
            products = await self._get_products()
            product = None
            
            for p in products:
                if p.get("article", "").upper() == article:
                    product = p
                    break
            
            if not product:
                await update.message.reply_text(f"❌ Продукт с артикулом {article} не найден")
                return
            
            # Проверяем валидность статуса
            valid_statuses = list(self.lifecycle_manager.lifecycle_statuses.keys())
            if new_status not in valid_statuses:
                await update.message.reply_text(
                    f"❌ Неверный статус '{new_status}'\n\n"
                    f"**Доступные статусы:**\n" + "\n".join([f"• {s}" for s in valid_statuses]),
                    parse_mode='Markdown'
                )
                return
            
            # Изменяем статус
            success = await self.lifecycle_manager.update_product_status(
                product["id"],
                new_status,
                f"Изменен через Telegram бот пользователем {update.effective_user.username}",
                "manual"
            )
            
            if success:
                await update.message.reply_text(
                    f"✅ Статус продукта {article} успешно изменен на '{new_status}'"
                )
            else:
                await update.message.reply_text(f"❌ Ошибка при изменении статуса")
            
            self._update_stats("status")
            
        except Exception as e:
            logger.error(f"❌ Ошибка изменения статуса: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def analytics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /analytics - аналитика жизненного цикла"""
        await update.message.reply_text("📊 Загружаю аналитику...")
        
        try:
            analytics = await self.lifecycle_manager.get_lifecycle_analytics()
            
            message = f"""
📊 **АНАЛИТИКА ЖИЗНЕННОГО ЦИКЛА**

**Общая статистика:**
📦 Всего продуктов: {analytics['total_products']}

**Распределение по статусам:**
            """
            
            for status, count in analytics['status_distribution'].items():
                percentage = (count / analytics['total_products'] * 100) if analytics['total_products'] > 0 else 0
                message += f"• {status}: {count} ({percentage:.1f}%)\n"
            
            # Эффективность
            efficiency = analytics.get('lifecycle_efficiency', {})
            if efficiency:
                message += f"""
**Эффективность:**
🎯 Точность статусов: {efficiency.get('status_accuracy', 0):.1f}%
⏱️ Временная эффективность: {efficiency.get('timeline_efficiency', 0):.1f}%
📈 Общая эффективность: {efficiency.get('overall_efficiency', 0):.1f}%
                """
            
            # Продукты, требующие внимания
            attention_needed = analytics.get('attention_needed', [])
            if attention_needed:
                message += f"\n⚠️ **Требуют внимания:** {len(attention_needed)} продуктов"
            
            # Кнопки для детального просмотра
            keyboard = [
                [InlineKeyboardButton("📈 Детальный отчет", callback_data="detailed_analytics")],
                [InlineKeyboardButton("⚠️ Просроченные", callback_data="overdue")],
                [InlineKeyboardButton("👀 Требуют внимания", callback_data="attention")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            self._update_stats("analytics")
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения аналитики: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def overdue_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /overdue - просроченные продукты"""
        await update.message.reply_text("⚠️ Проверяю просроченные продукты...")
        
        try:
            transitions_result = await self.lifecycle_manager.check_auto_transitions()
            overdue_products = transitions_result.get('overdue_products', [])
            
            if not overdue_products:
                await update.message.reply_text("✅ Просроченных продуктов нет!")
                return
            
            message = f"⚠️ **ПРОСРОЧЕННЫЕ ПРОДУКТЫ: {len(overdue_products)}**\n\n"
            
            for item in overdue_products[:10]:  # Показываем первые 10
                product = item['product']
                days_overdue = item['days_overdue']
                message += f"• {product.get('article', '')} - {product.get('name', '')}\n"
                message += f"  Статус: {product.get('status', '')}\n"
                message += f"  Просрочено на: {days_overdue} дней\n\n"
            
            if len(overdue_products) > 10:
                message += f"... и еще {len(overdue_products) - 10} продуктов"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            self._update_stats("overdue")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки просроченных: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def attention_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /attention - продукты, требующие внимания"""
        await update.message.reply_text("👀 Проверяю продукты, требующие внимания...")
        
        try:
            analytics = await self.lifecycle_manager.get_lifecycle_analytics()
            attention_needed = analytics.get('attention_needed', [])
            
            if not attention_needed:
                await update.message.reply_text("✅ Все продукты в норме!")
                return
            
            message = f"👀 **ТРЕБУЮТ ВНИМАНИЯ: {len(attention_needed)}**\n\n"
            
            for item in attention_needed[:10]:  # Показываем первые 10
                product = item['product']
                days_in_status = item['days_in_status']
                max_days = item['max_days']
                percentage = (days_in_status / max_days * 100) if max_days > 0 else 0
                
                message += f"• {product.get('article', '')} - {product.get('name', '')}\n"
                message += f"  Статус: {product.get('status', '')}\n"
                message += f"  В статусе: {days_in_status} дней ({percentage:.1f}% от максимума)\n\n"
            
            if len(attention_needed) > 10:
                message += f"... и еще {len(attention_needed) - 10} продуктов"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            self._update_stats("attention")
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки внимания: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def lifecycle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /lifecycle - полный отчет по жизненному циклу"""
        await update.message.reply_text("📈 Генерирую отчет по жизненному циклу...")
        
        try:
            report = await self.lifecycle_manager.generate_lifecycle_report()
            
            message = f"""
📈 **ОТЧЕТ ПО ЖИЗНЕННОМУ ЦИКЛУ**
📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}

**Сводка:**
📦 Всего продуктов: {report['summary']['total_products']}

**Распределение по статусам:**
            """
            
            for status, count in report['summary']['products_by_status'].items():
                percentage = (count / report['summary']['total_products'] * 100) if report['summary']['total_products'] > 0 else 0
                message += f"• {status}: {count} ({percentage:.1f}%)\n"
            
            # Эффективность
            efficiency = report['summary'].get('efficiency_metrics', {})
            if efficiency:
                message += f"""
**Метрики эффективности:**
🎯 Точность статусов: {efficiency.get('status_accuracy', 0):.1f}%
⏱️ Временная эффективность: {efficiency.get('timeline_efficiency', 0):.1f}%
📈 Общая эффективность: {efficiency.get('overall_efficiency', 0):.1f}%
                """
            
            # Рекомендации
            recommendations = report.get('recommendations', [])
            if recommendations:
                message += "\n**💡 РЕКОМЕНДАЦИИ:**\n"
                for rec in recommendations[:5]:  # Показываем первые 5
                    message += f"• {rec}\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            self._update_stats("lifecycle")
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчета: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "analytics":
            await self.analytics_command(update, context)
        elif data == "overdue":
            await self.overdue_command(update, context)
        elif data == "attention":
            await self.attention_command(update, context)
        elif data == "detailed_analytics":
            await self.lifecycle_command(update, context)
        elif data.startswith("materials_"):
            article = data.split("_", 1)[1]
            await self._show_materials(query, article)
        elif data.startswith("change_status_"):
            article = data.split("_", 2)[2]
            await self._show_status_options(query, article)
        elif data.startswith("status_"):
            parts = data.split("_", 2)
            article = parts[1]
            status = parts[2]
            await self._change_product_status(query, article, status)

    async def _show_materials(self, query, article: str):
        """Показать материалы продукта"""
        try:
            # Здесь будет логика получения материалов
            message = f"📁 **МАТЕРИАЛЫ ПРОДУКТА {article}**\n\n"
            message += "🔗 Ссылки на материалы:\n"
            message += "• Видео материалы (2+ файла)\n"
            message += "• Фото материалы\n"
            message += "• Документы\n"
            message += "• Ссылки на Яндекс.Диск\n\n"
            message += "📋 Система материалов в разработке..."
            
            await query.edit_message_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Ошибка показа материалов: {e}")
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def _show_status_options(self, query, article: str):
        """Показать варианты статусов для изменения"""
        try:
            valid_statuses = list(self.lifecycle_manager.lifecycle_statuses.keys())
            
            keyboard = []
            for status in valid_statuses:
                keyboard.append([InlineKeyboardButton(status, callback_data=f"status_{article}_{status}")])
            
            keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"🔄 **ИЗМЕНЕНИЕ СТАТУСА ПРОДУКТА {article}**\n\nВыберите новый статус:"
            
            await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"❌ Ошибка показа статусов: {e}")
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def _change_product_status(self, query, article: str, new_status: str):
        """Изменить статус продукта"""
        try:
            products = await self._get_products()
            product = None
            
            for p in products:
                if p.get("article", "").upper() == article:
                    product = p
                    break
            
            if not product:
                await query.edit_message_text(f"❌ Продукт с артикулом {article} не найден")
                return
            
            success = await self.lifecycle_manager.update_product_status(
                product["id"],
                new_status,
                f"Изменен через Telegram бот",
                "manual"
            )
            
            if success:
                await query.edit_message_text(f"✅ Статус продукта {article} изменен на '{new_status}'")
            else:
                await query.edit_message_text(f"❌ Ошибка при изменении статуса")
                
        except Exception as e:
            logger.error(f"❌ Ошибка изменения статуса: {e}")
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    async def _get_products(self) -> List[Dict[str, Any]]:
        """Получить продукты с кэшированием"""
        current_time = datetime.now()
        
        # Проверяем кэш
        if (self.cache_timestamp and 
            (current_time - self.cache_timestamp).total_seconds() < self.cache_duration and 
            self.products_cache):
            return self.products_cache
        
        # Обновляем кэш
        self.products_cache = await self.lifecycle_manager.get_all_products()
        self.cache_timestamp = current_time
        
        return self.products_cache

    def _format_date(self, date_str: str) -> str:
        """Форматирование даты"""
        try:
            if not date_str:
                return "Не указана"
            
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%d.%m.%Y")
        except:
            return "Ошибка формата"

    def _update_stats(self, command: str):
        """Обновить статистику использования"""
        self.usage_stats["commands_used"][command] = self.usage_stats["commands_used"].get(command, 0) + 1
        self.usage_stats["total_requests"] += 1
        self.usage_stats["last_activity"] = datetime.now().isoformat()

    def run(self):
        """Запуск бота"""
        if not self.telegram_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")
            return
        
        # Создаем приложение
        application = Application.builder().token(self.telegram_token).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("products", self.products_command))
        application.add_handler(CommandHandler("product", self.product_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("analytics", self.analytics_command))
        application.add_handler(CommandHandler("overdue", self.overdue_command))
        application.add_handler(CommandHandler("attention", self.attention_command))
        application.add_handler(CommandHandler("lifecycle", self.lifecycle_command))
        
        # Добавляем обработчик кнопок
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("🚀 Product Management Bot запущен")
        
        # Запускаем бота
        application.run_polling()

# Функция для запуска из командной строки
def main():
    """Основная функция для запуска бота"""
    bot = ProductManagementBot()
    bot.run()

if __name__ == "__main__":
    main() 