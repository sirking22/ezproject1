import logging
import logging.config
import os
from pathlib import Path

def setup_logging(
    default_path="logging.conf",
    default_level=logging.INFO,
    env_key="LOG_CFG"
):
    """Setup logging configuration

    Args:
        default_path: Path to logging config file
        default_level: Default logging level
        env_key: Environment variable key for logging config
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
        
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
        
    if os.path.exists(path):
        logging.config.fileConfig(path, disable_existing_loggers=False)
    else:
        logging.basicConfig(level=default_level)
        
    return logging.getLogger("notionBot")

def get_logger(name: str) -> logging.Logger:
    """Get logger by name
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"notionBot.{name}")

# Примеры использования:
"""
from utils.logging_utils import setup_logging, get_logger

# В main.py:
logger = setup_logging()
logger.info("Application started")

# В других модулях:
logger = get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
""" 