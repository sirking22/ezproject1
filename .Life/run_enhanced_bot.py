#!/usr/bin/env python3
"""
Запуск расширенного Telegram бота с локальной LLM интеграцией
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from src.telegram.enhanced_bot import EnhancedTelegramBot
from src.utils.config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска"""
    try:
        # Загружаем конфигурацию
        config = Config()
        
        # Создаем и запускаем бота
        bot = EnhancedTelegramBot(config)
        
        logger.info("🚀 Запуск расширенного Telegram бота с локальной LLM...")
        logger.info("📱 Доступные команды:")
        logger.info("  /start - начало работы")
        logger.info("  /help - справка")
        logger.info("  /todo [задача] - добавить задачу")
        logger.info("  /habit [название] - добавить привычку")
        logger.info("  /reflection [текст] - добавить рефлексию")
        logger.info("  /insight [тема] - глубокий анализ")
        logger.info("  /predict [привычка] - предсказание")
        logger.info("  /optimize [область] - оптимизация")
        logger.info("  /chat - свободный диалог с AI")
        logger.info("  /context [work/home] - переключение контекста")
        
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 