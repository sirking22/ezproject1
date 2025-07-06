"""
Конфигурация логирования и вывода в консоль.
Этот модуль инициализирует глобальные настройки логирования при импорте.
"""

import logging
import sys
from utils.console_helpers import (
    ColorFormatter,
    SUCCESS, ERROR, INFO, WARNING, PROCESS, TIMER,
    DATABASE, FIELD, RECORD, PROGRESS, LINK
)

# Настройки по умолчанию
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DEFAULT_DATE_FORMAT = '%H:%M:%S'

def configure_logging(
    level: int = DEFAULT_LOG_LEVEL,
    log_file: str = None,
    console: bool = True
) -> logging.Logger:
    """
    Настройка глобального логгера
    Args:
        level: Уровень логирования
        log_file: Путь к файлу для записи логов (опционально)
        console: Включить вывод в консоль
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Очищаем существующие обработчики
    logger.handlers = []
    
    # Настраиваем вывод в консоль
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColorFormatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Настраиваем вывод в файл
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Глобальные настройки стиля вывода
CONSOLE_STYLES = {
    'separators': {
        'header': "="*50,
        'section': "-"*30,
        'footer': "="*50
    },
    'progress_bar': {
        'length': 50,
        'fill': '█',
        'empty': '-',
        'decimals': 1
    },
    'timing': {
        'show_ms': False,
        'format': '.2f'
    }
}

# Инициализируем логирование при импорте модуля
logger = configure_logging()

# Экспортируем эмодзи для использования в других модулях
EMOJI = {
    'success': SUCCESS,
    'error': ERROR,
    'info': INFO,
    'warning': WARNING,
    'process': PROCESS,
    'timer': TIMER,
    'database': DATABASE,
    'field': FIELD,
    'record': RECORD,
    'progress': PROGRESS,
    'link': LINK
}

def format_header(title: str) -> str:
    """Форматирование заголовка"""
    sep = CONSOLE_STYLES['separators']['header']
    return f"\n{sep}\n{title.upper()}\n{sep}\n"

def format_footer(total_time: float) -> str:
    """Форматирование подвала"""
    sep = CONSOLE_STYLES['separators']['footer']
    time_format = CONSOLE_STYLES['timing']['format']
    return f"\n{sep}\nИТОГИ (общее время: {total_time:{time_format}} сек)\n{sep}"

def format_section(title: str) -> str:
    """Форматирование секции"""
    sep = CONSOLE_STYLES['separators']['section']
    return f"\n{sep}\n{title}\n{sep}\n" 