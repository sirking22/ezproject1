#!/bin/bash

# 🚀 Скрипт запуска Quick Voice Assistant Server
# Автор: AI Assistant
# Версия: 1.0.0

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Функции для вывода
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка виртуального окружения
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Виртуальное окружение не найдено. Запустите install.sh"
        exit 1
    fi
}

# Проверка конфигурации
check_config() {
    if [ ! -f ".env" ]; then
        print_warning "Файл .env не найден. Создайте конфигурацию."
    fi
    
    if [ ! -f "server/config.py" ]; then
        print_error "Файл server/config.py не найден"
        exit 1
    fi
}

# Проверка порта
check_port() {
    PORT=${1:-8000}
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Порт $PORT уже занят"
        read -p "Остановить процесс на порту $PORT? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:$PORT | xargs kill -9
            print_success "Процесс остановлен"
        else
            exit 1
        fi
    fi
}

# Создание логов
setup_logs() {
    mkdir -p logs
    touch logs/server.log
    touch logs/error.log
    touch logs/access.log
}

# Запуск сервера
start_server() {
    print_info "Запуск Quick Voice Assistant Server..."
    
    # Переход в директорию проекта
    cd "$(dirname "$0")"
    
    # Проверки
    check_venv
    check_config
    check_port 8000
    setup_logs
    
    # Активация виртуального окружения
    source venv/bin/activate
    
    # Переход в папку сервера
    cd server
    
    print_info "Сервер запускается на http://0.0.0.0:8000"
    print_info "Для остановки нажмите Ctrl+C"
    print_info "Логи: logs/server.log"
    
    # Запуск сервера
    python llm_api_server.py
}

# Обработка сигналов
trap 'print_info "Получен сигнал остановки. Завершение работы..."; exit 0' SIGINT SIGTERM

# Запуск
start_server 