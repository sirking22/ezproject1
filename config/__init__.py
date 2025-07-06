"""
Инициализация конфигурации приложения.
При импорте этого модуля автоматически настраивается логирование.
"""

from .logging_config import (
    logger,
    EMOJI,
    format_header,
    format_section,
    format_footer,
    CONSOLE_STYLES
)

# Настраиваем уровень логирования для сторонних библиотек
import logging
logging.getLogger('aiohttp').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

# Экспортируем основные компоненты
__all__ = [
    'logger',
    'EMOJI',
    'format_header',
    'format_section',
    'format_footer',
    'CONSOLE_STYLES'
] 