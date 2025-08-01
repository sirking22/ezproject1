#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для полного логирования всех компонентов системы
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.DEBUG,
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) -> logging.Logger:
    """
    Настройка логгера с файловым и консольным выводом
    
    Args:
        name: Имя логгера
        log_file: Путь к файлу лога
        level: Уровень логирования
        format: Формат сообщений
    """
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Форматтер для сообщений
    formatter = logging.Formatter(format)
    
    # Консольный вывод с кодировкой
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setStream(open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace'))
    logger.addHandler(console_handler)
    
    # Файловый вывод с кодировкой
    if log_file:
        # Создаем директорию для логов если нужно
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8', errors='replace')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None):
    """
    Логирование ошибки с контекстом
    
    Args:
        logger: Логгер
        error: Исключение
        context: Дополнительный контекст
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Базовое сообщение
    msg = f"❌ {error_type}: {error_msg}"
    
    # Добавляем контекст
    if context:
        msg += "\n🔍 Контекст:"
        for key, value in context.items():
            msg += f"\n  • {key}: {value}"
    
    # Добавляем стек вызовов
    import traceback
    stack = traceback.format_exc()
    msg += f"\n📚 Стек вызовов:\n{stack}"
    
    logger.error(msg)

def log_function_call(logger: logging.Logger, func_name: str, args: tuple = None, kwargs: dict = None):
    """
    Логирование вызова функции с аргументами
    
    Args:
        logger: Логгер
        func_name: Имя функции
        args: Позиционные аргументы
        kwargs: Именованные аргументы
    """
    msg = f"📡 Вызов функции: {func_name}"
    
    if args:
        msg += f"\n📥 Аргументы: {args}"
    if kwargs:
        msg += f"\n🔑 Параметры: {kwargs}"
        
    logger.debug(msg)

def log_api_request(logger: logging.Logger, method: str, url: str, params: dict = None, data: dict = None):
    """
    Логирование API запроса
    
    Args:
        logger: Логгер
        method: HTTP метод
        url: URL запроса
        params: Query параметры
        data: Тело запроса
    """
    msg = f"🌐 API запрос: {method} {url}"
    
    if params:
        msg += f"\n📝 Параметры: {params}"
    if data:
        msg += f"\n📦 Данные: {data}"
        
    logger.debug(msg)

def log_api_response(logger: logging.Logger, status_code: int, response_data: dict = None, error: Exception = None):
    """
    Логирование ответа API
    
    Args:
        logger: Логгер
        status_code: HTTP статус
        response_data: Данные ответа
        error: Ошибка если есть
    """
    if 200 <= status_code < 300:
        msg = f"✅ API ответ: {status_code}"
        if response_data:
            msg += f"\n📦 Данные: {response_data}"
        logger.debug(msg)
    else:
        msg = f"❌ API ошибка: {status_code}"
        if error:
            msg += f"\n💥 Ошибка: {error}"
        if response_data:
            msg += f"\n📦 Данные: {response_data}"
        logger.error(msg)

def log_bot_command(logger: logging.Logger, command: str, user_id: int, username: str = None):
    """
    Логирование команды бота
    
    Args:
        logger: Логгер
        command: Команда
        user_id: ID пользователя
        username: Имя пользователя
    """
    msg = f"🤖 Команда бота: {command}"
    msg += f"\n👤 Пользователь: {username or 'Неизвестно'} (ID: {user_id})"
    logger.info(msg)

def log_notion_operation(logger: logging.Logger, operation: str, database_id: str, data: dict = None):
    """
    Логирование операции с Notion
    
    Args:
        logger: Логгер
        operation: Тип операции
        database_id: ID базы данных
        data: Данные операции
    """
    msg = f"📚 Notion операция: {operation}"
    msg += f"\n🗄️ База данных: {database_id}"
    
    if data:
        msg += f"\n📦 Данные: {data}"
        
    logger.debug(msg)

def log_mcp_operation(logger: logging.Logger, method: str, params: dict = None):
    """
    Логирование операции MCP
    
    Args:
        logger: Логгер
        method: Метод MCP
        params: Параметры вызова
    """
    msg = f"🔄 MCP операция: {method}"
    
    if params:
        msg += f"\n📦 Параметры: {params}"
        
    logger.debug(msg)

# Создаем директорию для логов
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Текущая дата для имени файла
date_str = datetime.now().strftime("%Y%m%d")

# Настраиваем основные логгеры
bot_logger = setup_logger(
    "bot",
    log_file=f"logs/bot_{date_str}.log"
)

notion_logger = setup_logger(
    "notion",
    log_file=f"logs/notion_{date_str}.log"
)

mcp_logger = setup_logger(
    "mcp",
    log_file=f"logs/mcp_{date_str}.log"
)

llm_logger = setup_logger(
    "llm",
    log_file=f"logs/llm_{date_str}.log"
) 