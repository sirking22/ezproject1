import os
from dotenv import load_dotenv
from pathlib import Path
from src.config import settings

# Загружаем переменные окружения из .env файла
env_path = Path(__file__).parent.parent / '.env'
print(f"Loading .env from: {env_path.absolute()}")
load_dotenv(env_path)

# Базовый URL API
NOTION_API_BASE_URL = "https://api.notion.com/v1/"

# Получаем API ключ из переменных окружения
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
if not NOTION_API_KEY:
    raise ValueError("NOTION_API_KEY не найден в переменных окружения")

# Заголовки для Notion API
NOTION_VERSION = "2022-06-28"
NOTION_HEADERS = {
    "Authorization": f"Bearer {settings.NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

# Все ID баз данных из переменных окружения
NOTION_DATABASE_IDS = {
    # Основные рабочие базы
    'tasks': os.getenv('NOTION_TASKS_DB_ID'),
    'subtasks': os.getenv('NOTION_SUBTASKS_DB_ID'),
    'projects': os.getenv('NOTION_PROJECTS_DB_ID'),
    'ideas': os.getenv('NOTION_IDEAS_DB_ID'),
    'materials': os.getenv('NOTION_MATERIALS_DB_ID'),
    
    # Маркетинг и соцсети
    'marketing_tasks': os.getenv('NOTION_MARKETING_TASKS_DB_ID'),
    'content_plan': os.getenv('NOTION_CONTENT_PLAN_DB_ID'),
    'platforms': os.getenv('NOTION_PLATFORMS_DB_ID'),
    
    # Управление и аналитика
    'kpi': os.getenv('NOTION_KPI_DB_ID'),
    'teams': os.getenv('NOTION_TEAMS_DB_ID'),
    'rdt': os.getenv('NOTION_RDT_DB_ID'),
    'tasks_templates': os.getenv('NOTION_TASKS_TEMPLATES_DB_ID'),
    
    # Контент и обучение
    'learning': os.getenv('NOTION_LEARNING_DB_ID'),
    'guides': os.getenv('NOTION_GUIDES_DB_ID'),
    'super_guides': os.getenv('NOTION_SUPER_GUIDES_DB_ID'),
    'epics': os.getenv('NOTION_EPICS_DB_ID'),
    'concepts': os.getenv('NOTION_CONCEPTS_DB_ID'),
    'links': os.getenv('NOTION_LINKS_DB_ID'),
    
    # Дополнительные
    'clients': os.getenv('NOTION_CLIENTS_DB_ID'),
    'competitors': os.getenv('NOTION_COMPETITORS_DB_ID'),
    'products': os.getenv('NOTION_PRODUCTS_DB_ID'),
    
    # RAMIT базы данных (созданные на основе совещания)
    'ramit_strengths': os.getenv('NOTION_RAMIT_STRENGTHS_DB_ID'),
    'ramit_competitors': os.getenv('NOTION_RAMIT_COMPETITORS_DB_ID'),
    'ramit_deterministic_rules': os.getenv('NOTION_RAMIT_DETERMINISTIC_RULES_DB_ID'),
    'ramit_design_strategy': os.getenv('NOTION_RAMIT_DESIGN_STRATEGY_DB_ID'),
    'ramit_client_profiles': os.getenv('NOTION_RAMIT_CLIENT_PROFILES_DB_ID'),
    'ramit_revenue_impact': os.getenv('NOTION_RAMIT_REVENUE_IMPACT_DB_ID'),
    'ramit_tech_capabilities': os.getenv('NOTION_RAMIT_TECH_CAPABILITIES_DB_ID'),
    'ramit_market_opportunities': os.getenv('NOTION_RAMIT_MARKET_OPPORTUNITIES_DB_ID'),
    
    # Видео и контент
    'shots': os.getenv('NOTION_SHOTS_DB_ID')  # База кадров для съемок
}

# Категории баз данных для быстрой навигации
DATABASE_CATEGORIES = {
    'marketing': {
        'name': 'Маркетинг и соцсети',
        'databases': [
            'marketing_tasks',      # Маркетинговые задачи
            'content_plan'          # Контент-план
        ],
        'description': 'Маркетинг, контент и соцсети'
    },
    'team': {
        'name': 'Команда и управление',
        'databases': [
            'teams',           # Команды
            'kpi',            # KPI
            'tasks_templates'    # Шаблоны задач
        ],
        'description': 'Управление командой, задачами и KPI'
    },
    'ramit': {
        'name': 'RAMIT аналитика и стратегия',
        'databases': [
            'ramit_strengths',           # Сильные стороны RAMIT
            'ramit_competitors',         # Анализ конкурентов RAMIT
            'ramit_deterministic_rules', # Детерминированные правила RAMIT
            'ramit_design_strategy',     # Стратегия развития дизайн-отдела
            'ramit_client_profiles',     # Клиентские профили RAMIT
            'ramit_revenue_impact',      # Revenue Impact Score
            'ramit_tech_capabilities',   # Технологические возможности
            'ramit_market_opportunities' # Рыночные возможности
        ],
        'description': 'Комплексная аналитика и стратегия развития RAMIT'
    },
    'content': {
        'name': 'Контент и видео',
        'databases': [
            'shots'  # База кадров для съемок
        ],
        'description': 'Управление видео-контентом и съемками'
    }
}

# Связи между базами данных
DATABASE_RELATIONS = {
    'marketing_tasks': ['content_plan'],
    'teams': ['kpi', 'tasks_templates']
}

def get_database_id(db_name: str) -> str:
    """Получить ID базы данных по имени"""
    db_id = NOTION_DATABASE_IDS.get(db_name)
    if not db_id:
        raise ValueError(f"Database ID not found for: {db_name}")
    return db_id

def validate_notion_config():
    """Проверить наличие всех необходимых ID баз данных"""
    required_dbs = [
        'NOTION_TASKS_DB_ID',
        'NOTION_SUBTASKS_DB_ID',
        'NOTION_MATERIALS_DB_ID',
        'NOTION_IDEAS_DB_ID',
        'NOTION_MARKETING_TASKS_DB_ID',
        'NOTION_CONTENT_PLAN_DB_ID'
    ]
    
    missing_dbs = []
    for db_var in required_dbs:
        if not os.getenv(db_var):
            missing_dbs.append(db_var)
    
    if missing_dbs:
        raise ValueError(f"Missing required database IDs: {missing_dbs}")
    
    return True

print("\nСтруктура баз данных по категориям:")
for category, info in DATABASE_CATEGORIES.items():
    print(f"\n{info['name'].upper()} ({category}):")
    print(f"Описание: {info['description']}")
    print("Базы данных:")
    for db_name in info['databases']:
        db_id = get_database_id(db_name)
        status = "✅" if db_id else "⏳"
        print(f"  {status} {db_name}") 