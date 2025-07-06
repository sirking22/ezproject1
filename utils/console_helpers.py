import logging
import time
import sys
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from contextlib import contextmanager
import threading
import requests
from functools import wraps

# Константы для форматирования
SUCCESS = "✅"
ERROR = "❌"
INFO = "ℹ️"
WARNING = "⚠️"
PROCESS = "⚙️"
TIMER = "⏱️"
DATABASE = "📚"
FIELD = "📝"
RECORD = "📄"
PROGRESS = "📊"
LINK = "🔗"

class ColorFormatter(logging.Formatter):
    """Форматтер с цветным выводом для разных уровней логирования"""
    
    COLORS = {
        'DEBUG': '\033[0;36m',  # Cyan
        'INFO': '\033[0;32m',   # Green
        'WARNING': '\033[0;33m', # Yellow
        'ERROR': '\033[0;31m',  # Red
        'CRITICAL': '\033[0;35m',# Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Добавляем цвет к уровню логирования
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Настройка логирования с цветным выводом в консоль и опциональной записью в файл
    Args:
        level: Уровень логирования
        log_file: Путь к файлу для записи логов (опционально)
    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger('notion_tools')
    logger.setLevel(level)
    
    # Очищаем существующие обработчики
    logger.handlers = []
    
    # Форматтер для консоли (с цветами)
    console_formatter = ColorFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Обработчик для файла (если указан)
    if log_file:
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def print_header(title: str) -> None:
    """Печать заголовка с разделителями"""
    print("\n" + "="*50)
    print(title.upper())
    print("="*50 + "\n")

def print_footer(total_time: float) -> None:
    """Печать подвала с общим временем выполнения"""
    print("\n" + "="*50)
    print(f"ИТОГИ (общее время: {total_time:.2f} сек)")
    print("="*50)

class ProcessTracker:
    """Класс для отслеживания длительных процессов"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.processes: Dict[str, datetime] = {}
    
    def start_process(self, name: str):
        """Начало отслеживания процесса"""
        self.processes[name] = datetime.now()
        self.logger.info(f"{PROCESS} Начало процесса: {name}")
    
    def end_process(self, name: str):
        """Завершение отслеживания процесса"""
        if name in self.processes:
            duration = datetime.now() - self.processes[name]
            self.logger.info(f"{SUCCESS} Завершен процесс: {name} ({duration.total_seconds():.2f} сек)")
            del self.processes[name]
    
    def get_active_processes(self) -> List[str]:
        """Получение списка активных процессов"""
        return list(self.processes.keys())
    
    @contextmanager
    def track(self, name: str):
        """Контекстный менеджер для отслеживания процесса"""
        self.start_process(name)
        try:
            yield
        finally:
            self.end_process(name)

class Timer:
    """Контекстный менеджер для измерения времени выполнения"""
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.start_time = None
        self.logger = logger or logging.getLogger('notion_tools')
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"{TIMER} Начало операции: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"{SUCCESS} {self.operation_name} завершена за {duration:.2f} сек")
        else:
            self.logger.error(f"{ERROR} {self.operation_name} прервана с ошибкой: {str(exc_val)} ({duration:.2f} сек)")

class ProgressBar:
    """Класс для отображения прогресс-бара в консоли"""
    def __init__(self, total: int, prefix: str = '', suffix: str = '', decimals: int = 1, length: int = 50):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.current = 0
        self.start_time = time.time()
    
    def update(self, current: int):
        """Обновление прогресс-бара"""
        self.current = current
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (current / float(self.total)))
        filled_length = int(self.length * current // self.total)
        bar = '█' * filled_length + '-' * (self.length - filled_length)
        elapsed_time = time.time() - self.start_time
        
        sys.stdout.write(f'\r{self.prefix} |{bar}| {percent}% {self.suffix} ({elapsed_time:.1f}s)')
        sys.stdout.flush()
        
        if current == self.total:
            sys.stdout.write('\n')
            sys.stdout.flush()

def with_timeout(timeout_seconds: int):
    """Декоратор для ограничения времени выполнения функции"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            error = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    error[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Функция {func.__name__} превысила таймаут {timeout_seconds} сек")
            
            if error[0] is not None:
                raise error[0]
            
            return result[0]
        return wrapper
    return decorator

def safe_request(url: str, method: str = 'GET', timeout: int = 30, **kwargs) -> requests.Response:
    """Безопасный HTTP-запрос с таймаутом и обработкой ошибок"""
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except requests.Timeout:
        logger.error(f"{ERROR} Таймаут запроса ({timeout} сек): {url}")
        raise
    except requests.RequestException as e:
        logger.error(f"{ERROR} Ошибка запроса: {str(e)}")
        raise

def print_results(results: Dict[str, bool], logger: Optional[logging.Logger] = None) -> None:
    """Печать результатов операций"""
    logger = logger or logging.getLogger('notion_tools')
    for name, success in results.items():
        status = SUCCESS if success else ERROR
        logger.info(f"{status} {name}")

def format_error(error: Exception, duration: Optional[float] = None) -> str:
    """Форматирование сообщения об ошибке"""
    time_info = f" ({duration:.2f} сек)" if duration is not None else ""
    return f"{ERROR} Ошибка: {str(error)}{time_info}"

# Глобальный логгер и трекер процессов
logger = setup_logging()
process_tracker = ProcessTracker(logger)

# Пример использования:
if __name__ == "__main__":
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Пример использования таймера
    print_header("Тестирование консольных хелперов")
    
    start_time = time.time()
    
    # Пример с таймером
    with Timer("Тестовая операция"):
        time.sleep(1)  # Имитация работы
        
    # Пример обработки ошибки
    try:
        raise ValueError("Тестовая ошибка")
    except Exception as e:
        print(format_error(e, time.time() - start_time))
    
    # Пример вывода результатов
    results = {
        "Операция 1": True,
        "Операция 2": False,
        "Операция 3": True
    }
    
    print_footer(time.time() - start_time)
    print_results(results) 