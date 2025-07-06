#!/usr/bin/env python3
"""
Главный файл для запуска Life Management System
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path

# Добавляем src в путь
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.life_management_system import life_system
from src.config.environment import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('life_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Главная функция"""
    try:
        logger.info("🚀 Запуск Life Management System...")
        
        # Проверяем конфигурацию
        validation = config.validate()
        missing_configs = config.get_missing_configs()
        
        if missing_configs:
            logger.warning(f"⚠️ Отсутствуют конфигурации: {', '.join(missing_configs)}")
            logger.info("Система будет работать в ограниченном режиме")
        
        # Инициализируем систему
        await life_system.initialize()
        
        # Запускаем Telegram бота
        await life_system.run_telegram_bot()
        
        # Держим систему запущенной
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        # Очистка ресурсов
        await life_system.cleanup()
        logger.info("✅ Система остановлена")

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    logger.info(f"Получен сигнал {signum}")
    sys.exit(0)

if __name__ == "__main__":
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Запускаем главную функцию
    asyncio.run(main()) 