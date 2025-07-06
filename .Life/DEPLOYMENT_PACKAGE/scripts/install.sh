#!/bin/bash

# 🚀 Скрипт автоматической установки Quick Voice Assistant
# Автор: AI Assistant
# Версия: 1.0.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo "🚀 QUICK VOICE ASSISTANT INSTALLER"
    echo "=================================="
    echo -e "${NC}"
}

# Проверка требований
check_requirements() {
    print_info "Проверка системных требований..."
    
    # Проверка Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION найден"
    else
        print_error "Python 3 не найден. Установите Python 3.8+"
        exit 1
    fi
    
    # Проверка Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION найден"
    else
        print_warning "Node.js не найден. Установите Node.js 16+"
    fi
    
    # Проверка Git
    if command -v git &> /dev/null; then
        print_success "Git найден"
    else
        print_warning "Git не найден. Установите Git"
    fi
}

# Создание структуры директорий
create_directories() {
    print_info "Создание структуры директорий..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p cache
    mkdir -p models
    
    print_success "Структура директорий создана"
}

# Настройка виртуального окружения Python
setup_python_env() {
    print_info "Настройка виртуального окружения Python..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Виртуальное окружение создано"
    else
        print_info "Виртуальное окружение уже существует"
    fi
    
    # Активация виртуального окружения
    source venv/bin/activate
    
    # Обновление pip
    pip install --upgrade pip
    
    print_success "Виртуальное окружение настроено"
}

# Установка Python зависимостей
install_python_deps() {
    print_info "Установка Python зависимостей..."
    
    if [ -f "server/requirements.txt" ]; then
        pip install -r server/requirements.txt
        print_success "Python зависимости установлены"
    else
        print_error "Файл requirements.txt не найден"
        exit 1
    fi
}

# Настройка конфигурации
setup_config() {
    print_info "Настройка конфигурации..."
    
    # Создание .env файла если не существует
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Конфигурация сервера
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True
RELOAD=False

# Конфигурация LLM
USE_LOCAL_LLM=False
LLM_MODEL_PATH=
LLM_MODEL_TYPE=llama
LLM_CONTEXT_LENGTH=4096
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512
FALLBACK_TO_OPENAI=True

# Конфигурация Notion
NOTION_ENABLED=True
NOTION_TOKEN=
NOTION_TASKS_DB=
NOTION_REFLECTIONS_DB=
NOTION_HABITS_DB=
NOTION_IDEAS_DB=
NOTION_MATERIALS_DB=

# Конфигурация Telegram
TELEGRAM_ENABLED=True
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Конфигурация голоса
VOICE_SAMPLE_RATE=16000
VOICE_CHUNK_SIZE=1024
VOICE_MAX_DURATION=30
VOICE_LANGUAGE=ru
VOICE_MODEL=whisper

# Конфигурация производительности
MAX_WORKERS=4
REQUEST_TIMEOUT=30
CACHE_SIZE=1000
ENABLE_COMPRESSION=True
ENABLE_CACHING=True

# Конфигурация безопасности
ALLOWED_HOSTS=192.168.1.0/24
RATE_LIMIT=100
ENABLE_LOGGING=True
API_KEY=

# Конфигурация мониторинга
ENABLE_METRICS=True
LOG_LEVEL=INFO
SAVE_LOGS=True
LOG_FILE=logs/server.log

# Конфигурация кэширования
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
EOF
        print_success "Файл .env создан"
    else
        print_info "Файл .env уже существует"
    fi
    
    # Настройка прав доступа
    chmod 600 .env
}

# Получение IP адреса
get_ip_address() {
    print_info "Получение IP адреса..."
    
    if command -v ipconfig &> /dev/null; then
        # Windows
        IP_ADDRESS=$(ipconfig | grep "IPv4 Address" | head -1 | awk '{print $NF}')
    else
        # Linux/macOS
        IP_ADDRESS=$(hostname -I | awk '{print $1}')
    fi
    
    if [ -n "$IP_ADDRESS" ]; then
        print_success "IP адрес: $IP_ADDRESS"
        
        # Обновление конфигурации часов
        if [ -f "watch_app/app_config.json" ]; then
            sed -i "s/192.168.1.100/$IP_ADDRESS/g" watch_app/app_config.json
            print_success "Конфигурация часов обновлена с IP: $IP_ADDRESS"
        fi
    else
        print_warning "Не удалось получить IP адрес"
    fi
}

# Создание скриптов запуска
create_startup_scripts() {
    print_info "Создание скриптов запуска..."
    
    # Скрипт запуска сервера
    cat > start_server.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
cd server
python llm_api_server.py
EOF
    
    # Скрипт тестирования
    cat > test_system.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
cd scripts
python test_system.py
EOF
    
    # Скрипт остановки
    cat > stop_server.sh << 'EOF'
#!/bin/bash
pkill -f "llm_api_server.py"
echo "Сервер остановлен"
EOF
    
    # Установка прав доступа
    chmod +x start_server.sh
    chmod +x test_system.sh
    chmod +x stop_server.sh
    
    print_success "Скрипты запуска созданы"
}

# Тестирование установки
test_installation() {
    print_info "Тестирование установки..."
    
    # Проверка виртуального окружения
    if [ -d "venv" ]; then
        print_success "Виртуальное окружение работает"
    else
        print_error "Виртуальное окружение не найдено"
        return 1
    fi
    
    # Проверка зависимостей
    source venv/bin/activate
    if python -c "import fastapi, uvicorn" 2>/dev/null; then
        print_success "Основные зависимости установлены"
    else
        print_error "Основные зависимости не установлены"
        return 1
    fi
    
    # Проверка конфигурации
    if [ -f ".env" ]; then
        print_success "Конфигурация создана"
    else
        print_error "Конфигурация не найдена"
        return 1
    fi
    
    print_success "Тестирование завершено успешно"
}

# Основная функция установки
main() {
    print_header
    
    print_info "Начинаем установку Quick Voice Assistant..."
    
    # Проверка требований
    check_requirements
    
    # Создание директорий
    create_directories
    
    # Настройка Python
    setup_python_env
    install_python_deps
    
    # Настройка конфигурации
    setup_config
    
    # Получение IP адреса
    get_ip_address
    
    # Создание скриптов запуска
    create_startup_scripts
    
    # Тестирование
    test_installation
    
    print_header
    print_success "🎉 Установка завершена успешно!"
    echo ""
    print_info "Следующие шаги:"
    echo "1. Отредактируйте файл .env и добавьте свои токены"
    echo "2. Запустите сервер: ./start_server.sh"
    echo "3. Протестируйте систему: ./test_system.sh"
    echo "4. Установите приложение на часы"
    echo ""
    print_info "Документация: INSTALLATION_GUIDE.md"
    echo ""
}

# Запуск установки
main "$@" 