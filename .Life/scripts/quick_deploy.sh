#!/bin/bash

# 🚀 Быстрый деплой Life System Bots на Railway
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

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 RAILWAY DEPLOY                        ║"
    echo "║                Life System Bots + DeepSea LLM               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Проверка зависимостей
check_dependencies() {
    print_info "Проверка зависимостей..."
    
    # Проверка Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js не установлен. Установите Node.js 16+"
        exit 1
    fi
    
    # Проверка npm
    if ! command -v npm &> /dev/null; then
        print_error "npm не установлен"
        exit 1
    fi
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 не установлен"
        exit 1
    fi
    
    print_success "Все зависимости установлены"
}

# Установка Railway CLI
install_railway_cli() {
    print_info "Установка Railway CLI..."
    
    if command -v railway &> /dev/null; then
        print_info "Railway CLI уже установлен"
    else
        npm install -g @railway/cli
        print_success "Railway CLI установлен"
    fi
}

# Создание конфигурационных файлов
create_config_files() {
    print_info "Создание конфигурационных файлов..."
    
    # Запуск Python скрипта для создания файлов
    python3 scripts/deploy_to_railway.py
    
    print_success "Конфигурационные файлы созданы"
}

# Проверка переменных окружения
check_env_vars() {
    print_info "Проверка переменных окружения..."
    
    required_vars=(
        "TELEGRAM_BOT_TOKEN"
        "NOTION_TOKEN"
        "OPENROUTER_API_KEY"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_warning "Отсутствуют переменные окружения:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        
        print_info "Создайте файл .env на основе .env.template"
        print_info "Или установите переменные в Railway Dashboard"
    else
        print_success "Все необходимые переменные окружения установлены"
    fi
}

# Инициализация Railway проекта
init_railway_project() {
    print_info "Инициализация Railway проекта..."
    
    if [ -f ".railway" ]; then
        print_info "Проект уже инициализирован"
    else
        print_info "Создание нового Railway проекта..."
        railway init
        
        if [ $? -eq 0 ]; then
            print_success "Railway проект создан"
        else
            print_error "Ошибка создания Railway проекта"
            print_info "Убедитесь, что вы вошли в Railway: railway login"
            exit 1
        fi
    fi
}

# Деплой на Railway
deploy_to_railway() {
    print_info "Деплой на Railway..."
    
    railway up
    
    if [ $? -eq 0 ]; then
        print_success "Деплой завершен успешно!"
        
        # Получение URL
        print_info "Получение URL приложения..."
        app_url=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
        
        if [ -n "$app_url" ]; then
            print_success "Приложение доступно по адресу: $app_url"
            print_info "Health check: $app_url/health"
            print_info "API docs: $app_url/docs"
        fi
    else
        print_error "Ошибка деплоя"
        exit 1
    fi
}

# Настройка автодеплоя через GitHub
setup_github_deploy() {
    print_info "Настройка автодеплоя через GitHub..."
    
    if [ -d ".git" ]; then
        print_info "Git репозиторий найден"
        
        # Проверка наличия GitHub remote
        if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
            print_info "GitHub remote найден"
            
            # Получение Railway token
            print_warning "Для автодеплоя нужно добавить RAILWAY_TOKEN в GitHub Secrets"
            print_info "1. Получите токен: railway whoami --json"
            print_info "2. Добавьте в GitHub: Settings > Secrets > New repository secret"
            print_info "3. Название: RAILWAY_TOKEN"
            print_info "4. Значение: ваш_railway_token"
            
        else
            print_warning "GitHub remote не найден"
            print_info "Добавьте GitHub remote для автодеплоя"
        fi
    else
        print_warning "Git репозиторий не найден"
        print_info "Инициализируйте git для автодеплоя"
    fi
}

# Основная функция
main() {
    print_header
    
    # Проверка зависимостей
    check_dependencies
    
    # Установка Railway CLI
    install_railway_cli
    
    # Создание конфигурационных файлов
    create_config_files
    
    # Проверка переменных окружения
    check_env_vars
    
    # Инициализация Railway проекта
    init_railway_project
    
    # Деплой
    deploy_to_railway
    
    # Настройка автодеплоя
    setup_github_deploy
    
    print_header
    print_success "🎉 Деплой завершен!"
    echo ""
    print_info "Следующие шаги:"
    echo "1. Проверьте работу ботов в Telegram"
    echo "2. Настройте автодеплой через GitHub (опционально)"
    echo "3. Мониторьте логи в Railway Dashboard"
    echo ""
    print_info "Полезные команды:"
    echo "• railway logs - просмотр логов"
    echo "• railway status - статус приложения"
    echo "• railway open - открыть в браузере"
    echo ""
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "Использование: $0 [опции]"
        echo ""
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --config-only  Только создать конфигурационные файлы"
        echo "  --deploy-only  Только деплой (без создания файлов)"
        echo ""
        exit 0
        ;;
    --config-only)
        print_header
        create_config_files
        print_success "Конфигурационные файлы созданы"
        exit 0
        ;;
    --deploy-only)
        print_header
        deploy_to_railway
        exit 0
        ;;
esac

# Запуск основной функции
main "$@" 