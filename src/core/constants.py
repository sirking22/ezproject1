"""Global constants for the application."""

# Idea stages
IDEA_STAGES = [
    "concept",
    "validation",
    "prototype",
    "development",
    "testing",
    "launch",
    "scaling"
]

# Impact categories
IMPACT_CATEGORIES = [
    "health",
    "education",
    "environment",
    "economic",
    "social",
    "technology",
    "infrastructure",
    "governance"
]

# UN Sustainable Development Goals
SDG_GOALS = [
    "No Poverty",
    "Zero Hunger",
    "Good Health and Well-being",
    "Quality Education",
    "Gender Equality",
    "Clean Water and Sanitation",
    "Affordable and Clean Energy",
    "Decent Work and Economic Growth",
    "Industry, Innovation and Infrastructure",
    "Reduced Inequality",
    "Sustainable Cities and Communities",
    "Responsible Consumption and Production",
    "Climate Action",
    "Life Below Water",
    "Life on Land",
    "Peace, Justice and Strong Institutions",
    "Partnerships for the Goals"
]

# Geographic regions
REGIONS = [
    "North America",
    "South America",
    "Europe",
    "Africa",
    "Asia",
    "Oceania",
    "Global"
]

# Impact levels
IMPACT_LEVELS = [
    "low",
    "medium",
    "high"
]

# Priority levels
PRIORITY_LEVELS = [
    "low",
    "medium",
    "high",
    "urgent"
]

# Status options
STATUS_OPTIONS = [
    "active",
    "on_hold",
    "completed",
    "archived"
]

# Resource types
RESOURCE_TYPES = [
    "technical",
    "financial",
    "human",
    "infrastructure",
    "knowledge",
    "partnerships"
]

# Technology categories
TECH_CATEGORIES = [
    "web",
    "mobile",
    "ai_ml",
    "blockchain",
    "iot",
    "robotics",
    "biotech",
    "cleantech",
    "other"
]

# Maximum values
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 2000
MAX_SUGGESTIONS = 10
MAX_NEXT_STEPS = 5
MAX_CHALLENGES = 10
MAX_SOLUTIONS = 10

# Timeouts (seconds)
API_TIMEOUT = 30
LLM_TIMEOUT = 60
NOTION_TIMEOUT = 30

# Cache settings
CACHE_TTL = 3600  # 1 hour
MAX_CACHE_SIZE = 1000

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Rate limits
MAX_REQUESTS_PER_MINUTE = 60
MAX_TOKENS_PER_REQUEST = 4000 