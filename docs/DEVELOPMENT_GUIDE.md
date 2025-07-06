# Development Guide

## Overview

This guide covers development best practices, architecture patterns, and guidelines for extending the Notion-Telegram-LLM integration system.

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Notion-Telegram-LLM System              │
├─────────────────────────────────────────────────────────────┤
│  Telegram Bot Layer                                        │
│  ├── simple_bot.py (Main bot)                             │
│  ├── handlers/ (Command handlers)                         │
│  └── middleware/ (Authentication, logging)                │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                              │
│  ├── notion_service.py (Core Notion operations)           │
│  ├── llm_service.py (AI processing)                       │
│  ├── advanced_notion_service.py (Bulk operations)         │
│  └── checklist_service.py (Task management)               │
├─────────────────────────────────────────────────────────────┤
│  Repository Layer                                           │
│  ├── notion_repository.py (Data access)                   │
│  ├── base.py (Abstract repository)                        │
│  └── models/ (Data models)                                │
├─────────────────────────────────────────────────────────────┤
│  Utility Layer                                             │
│  ├── console_helpers.py (Logging, monitoring)             │
│  ├── notion_database_schemas.py (Schema management)       │
│  └── file_processors/ (Upload, video processing)          │
├─────────────────────────────────────────────────────────────┤
│  External APIs                                             │
│  ├── Notion API                                           │
│  ├── OpenRouter/LLM APIs                                  │
│  ├── Telegram Bot API                                     │
│  └── Yandex.Disk API                                      │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

1. **Repository Pattern**: Data access abstraction
2. **Service Layer**: Business logic encapsulation
3. **Factory Pattern**: Object creation
4. **Observer Pattern**: Event handling
5. **Strategy Pattern**: Algorithm selection

## Development Setup

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd notion-telegram-llm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install pre-commit hooks
pre-commit install
```

### 2. Development Dependencies

```bash
# requirements-dev.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0
isort>=5.0.0
coverage>=7.0.0
bandit>=1.7.0
```

### 3. IDE Configuration

#### VS Code Settings
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

#### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
```

## Code Standards

### 1. Code Style

Follow **PEP 8** with these specific guidelines:

```python
# Good: Clear, descriptive names
async def create_task_with_checklist(
    task_data: TaskDTO, 
    checklist_items: List[str]
) -> Tuple[str, int]:
    """
    Create a task with associated checklist items.
    
    Args:
        task_data: Task information
        checklist_items: List of checklist descriptions
        
    Returns:
        Tuple of (task_id, checklist_count)
        
    Raises:
        NotionError: If task creation fails
        ValidationError: If task data is invalid
    """
    pass

# Bad: Unclear names and no documentation
def create(t, c):
    pass
```

### 2. Type Hints

Use comprehensive type hints:

```python
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

# Good: Complete type annotations
async def process_database_records(
    database_id: str,
    filters: Optional[List[NotionFilter]] = None,
    batch_size: int = 100
) -> Dict[str, Union[int, List[str]]]:
    """Process database records with optional filtering."""
    pass

# Bad: No type hints
async def process_database_records(database_id, filters=None, batch_size=100):
    pass
```

### 3. Error Handling

Implement comprehensive error handling:

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass

class NotionServiceError(ServiceError):
    """Notion-specific service errors."""
    pass

async def safe_notion_operation(
    operation: str, 
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Safely execute Notion operation with error handling.
    
    Args:
        operation: Operation name for logging
        **kwargs: Operation parameters
        
    Returns:
        Operation result or None if failed
    """
    try:
        logger.info(f"Starting {operation}", extra=kwargs)
        
        # Perform operation
        result = await execute_operation(**kwargs)
        
        logger.info(f"Completed {operation} successfully")
        return result
        
    except NotionAPIError as e:
        logger.error(f"Notion API error in {operation}: {e}")
        raise NotionServiceError(f"Operation {operation} failed: {str(e)}")
        
    except Exception as e:
        logger.exception(f"Unexpected error in {operation}")
        return None
```

### 4. Logging Standards

Consistent logging across the system:

```python
import logging
from typing import Dict, Any

class ContextualLogger:
    """Logger with automatic context injection."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set logging context."""
        self.context.update(kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info with context."""
        extra = {**self.context, **kwargs}
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, exc_info=True, **kwargs):
        """Log error with context."""
        extra = {**self.context, **kwargs}
        self.logger.error(message, exc_info=exc_info, extra=extra)

# Usage
logger = ContextualLogger(__name__)
logger.set_context(user_id="123", operation="create_task")
logger.info("Task creation started")
```

## Testing Guidelines

### 1. Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── services/
│   ├── repositories/
│   └── utils/
├── integration/            # Integration tests
│   ├── notion/
│   ├── telegram/
│   └── llm/
├── e2e/                   # End-to-end tests
├── fixtures/              # Test data
└── conftest.py           # Pytest configuration
```

### 2. Unit Testing

```python
# tests/unit/services/test_notion_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from src.services.notion_service import NotionService, NotionError

class TestNotionService:
    """Test suite for NotionService."""
    
    @pytest.fixture
    async def notion_service(self):
        """Create NotionService instance for testing."""
        service = NotionService()
        service.client = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_get_database_success(self, notion_service):
        """Test successful database retrieval."""
        # Arrange
        expected_db = {"id": "test_id", "title": "Test DB"}
        notion_service.client.databases.retrieve.return_value = expected_db
        
        # Act
        result = await notion_service.get_database("test_id")
        
        # Assert
        assert result.id == "test_id"
        notion_service.client.databases.retrieve.assert_called_once_with(
            database_id="test_id"
        )
    
    @pytest.mark.asyncio
    async def test_get_database_not_found(self, notion_service):
        """Test database not found error handling."""
        # Arrange
        notion_service.client.databases.retrieve.side_effect = Exception("Not found")
        
        # Act & Assert
        with pytest.raises(NotionError, match="Not found"):
            await notion_service.get_database("invalid_id")
```

### 3. Integration Testing

```python
# tests/integration/test_task_workflow.py
import pytest
import os
from src.services.notion_service import NotionService
from src.repositories.notion_repository import NotionTaskRepository
from src.models.base import TaskDTO

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_task_workflow():
    """Test complete task creation and management workflow."""
    
    # Skip if no credentials
    if not os.getenv("NOTION_TOKEN"):
        pytest.skip("Notion credentials not available")
    
    # Initialize services
    notion_service = NotionService()
    await notion_service.initialize()
    
    task_repo = NotionTaskRepository(
        notion_service.client, 
        os.getenv("NOTION_TASKS_DB_ID")
    )
    
    try:
        # Test task creation
        task_data = TaskDTO(
            title="Integration Test Task",
            description="Test task for integration testing",
            status="To Do",
            priority="Medium"
        )
        
        created_task = await task_repo.create(task_data)
        assert created_task.title == "Integration Test Task"
        
        # Test task update
        created_task.status = "In Progress"
        updated_task = await task_repo.update(created_task.id, created_task)
        assert updated_task.status == "In Progress"
        
        # Test task retrieval
        retrieved_task = await task_repo.get(created_task.id)
        assert retrieved_task.status == "In Progress"
        
    finally:
        # Cleanup
        if 'created_task' in locals():
            await task_repo.delete(created_task.id)
        await notion_service.cleanup()
```

### 4. Test Configuration

```python
# tests/conftest.py
import pytest
import asyncio
import os
from unittest.mock import AsyncMock

# Test environment setup
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_notion_client():
    """Mock Notion client for testing."""
    client = AsyncMock()
    return client

@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "Test description",
        "status": "To Do",
        "priority": "High"
    }

# Test markers
pytest_plugins = ["pytest_asyncio"]

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
```

## Extension Guidelines

### 1. Adding New Services

```python
# src/services/new_service.py
from .base_service import BaseService
from typing import Dict, Any, Optional

class NewService(BaseService):
    """New service implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.client = None
    
    async def initialize(self) -> None:
        """Initialize service resources."""
        await super().initialize()
        # Service-specific initialization
        self.client = create_client(self.config)
        
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        if self.client:
            await self.client.close()
        await super().cleanup()
    
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with proper error handling."""
        try:
            self.log_operation("process_data", {"data_size": len(data)})
            
            result = await self._perform_processing(data)
            
            self.log_operation("process_data_success", {"result_size": len(result)})
            return result
            
        except Exception as e:
            await self.handle_error(e, {"operation": "process_data", "data": data})
            raise
```

### 2. Adding New Repositories

```python
# src/repositories/new_repository.py
from .base import Repository
from ..models.new_model import NewModel
from typing import List, Optional, Dict, Any

class NewRepository(Repository[NewModel]):
    """Repository for new model operations."""
    
    def __init__(self, client, database_id: str):
        self.client = client
        self.database_id = database_id
    
    async def get(self, id: str) -> Optional[NewModel]:
        """Get model by ID."""
        try:
            data = await self.client.get(id)
            return self._to_model(data)
        except Exception as e:
            logger.error(f"Error getting model {id}: {e}")
            return None
    
    async def create(self, model: NewModel) -> NewModel:
        """Create new model."""
        try:
            data = self._from_model(model)
            result = await self.client.create(data)
            return self._to_model(result)
        except Exception as e:
            logger.error(f"Error creating model: {e}")
            raise
    
    async def list(self, params: Optional[Dict] = None) -> List[NewModel]:
        """List models with optional filtering."""
        try:
            data = await self.client.list(params or {})
            return [self._to_model(item) for item in data]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def _to_model(self, data: Dict[str, Any]) -> NewModel:
        """Convert API data to model."""
        return NewModel(**data)
    
    def _from_model(self, model: NewModel) -> Dict[str, Any]:
        """Convert model to API data."""
        return model.dict()
```

### 3. Adding New Telegram Handlers

```python
# src/services/telegram/handlers/new_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from ...base_service import BaseService

class NewHandler(BaseService):
    """Handler for new functionality."""
    
    def __init__(self, dependencies):
        super().__init__()
        self.dependencies = dependencies
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new command."""
        try:
            self.log_operation("new_command", {
                "user_id": update.effective_user.id,
                "chat_id": update.effective_chat.id
            })
            
            # Process command
            result = await self._process_command(update, context)
            
            # Send response
            await update.message.reply_text(result)
            
        except Exception as e:
            await self.handle_error(e, {
                "command": "new_command",
                "user_id": update.effective_user.id
            })
            await update.message.reply_text(
                "⚠️ Произошла ошибка. Попробуйте позже."
            )
    
    async def _process_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Process the command logic."""
        # Implementation here
        pass
```

### 4. Adding New Models

```python
# src/models/new_model.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NewModel(BaseModel):
    """Model for new entity."""
    
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: str = Field(..., regex="^(active|inactive|pending)$")
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        """Model configuration."""
        validate_assignment = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def __str__(self) -> str:
        return f"NewModel(id={self.id}, name='{self.name}')"
```

## Performance Optimization

### 1. Database Query Optimization

```python
# Efficient database queries
class OptimizedNotionService:
    """Optimized Notion service with caching and batching."""
    
    def __init__(self):
        self.cache = {}
        self.batch_queue = []
        self.batch_size = 10
    
    async def query_with_cache(self, db_id: str, cache_key: str) -> List[Dict]:
        """Query with caching."""
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = await self.query_database(db_id)
        self.cache[cache_key] = result
        return result
    
    async def batch_updates(self, updates: List[Tuple[str, Dict]]):
        """Batch multiple updates for efficiency."""
        for i in range(0, len(updates), self.batch_size):
            batch = updates[i:i + self.batch_size]
            await self._process_batch(batch)
            await asyncio.sleep(0.1)  # Rate limiting
```

### 2. Memory Management

```python
import gc
import psutil
from typing import Iterator, List

def process_large_dataset(items: List[Any]) -> Iterator[Any]:
    """Process large datasets efficiently."""
    
    chunk_size = 1000
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        
        for item in chunk:
            yield process_item(item)
        
        # Memory cleanup
        if i % (chunk_size * 10) == 0:
            gc.collect()
            
            # Memory monitoring
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
            if memory_usage > 500:  # 500MB threshold
                logger.warning(f"High memory usage: {memory_usage:.1f}MB")
```

### 3. Async Optimization

```python
import asyncio
from typing import List, Awaitable, TypeVar

T = TypeVar('T')

async def concurrent_execution(
    tasks: List[Awaitable[T]], 
    max_concurrent: int = 10
) -> List[T]:
    """Execute tasks concurrently with limits."""
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_task(task: Awaitable[T]) -> T:
        async with semaphore:
            return await task
    
    return await asyncio.gather(*[
        limited_task(task) for task in tasks
    ])

# Usage
tasks = [
    notion_service.get_page(page_id)
    for page_id in page_ids
]

results = await concurrent_execution(tasks, max_concurrent=5)
```

## Security Guidelines

### 1. Secure Configuration

```python
# src/core/security.py
import os
from cryptography.fernet import Fernet
from typing import Optional

class SecureConfig:
    """Secure configuration management."""
    
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        self.cipher = Fernet(self.encryption_key) if self.encryption_key else None
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get encrypted secret."""
        encrypted_value = os.getenv(f"{key}_ENCRYPTED")
        if encrypted_value and self.cipher:
            return self.cipher.decrypt(encrypted_value.encode()).decode()
        return os.getenv(key)
    
    def validate_token(self, token: str) -> bool:
        """Validate API token format."""
        if not token:
            return False
        
        # Basic token validation
        if len(token) < 10:
            return False
        
        # Additional validation logic
        return True
```

### 2. Input Validation

```python
from pydantic import BaseModel, validator
import re

class SecureUserInput(BaseModel):
    """Secure user input validation."""
    
    message: str
    user_id: int
    
    @validator('message')
    def validate_message(cls, v):
        """Validate message content."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        
        if len(v) > 4000:
            raise ValueError('Message too long')
        
        # Remove potential harmful content
        cleaned = re.sub(r'[<>\"\'&]', '', v)
        return cleaned
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user ID."""
        if v <= 0:
            raise ValueError('Invalid user ID')
        return v
```

### 3. Rate Limiting

```python
import time
from collections import defaultdict
from typing import Dict

class RateLimiter:
    """Rate limiting for API calls."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if timestamp > window_start
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
```

## Deployment Guidelines

### 1. Environment Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  notion-bot:
    build: .
    environment:
      - NOTION_TOKEN=${NOTION_TOKEN}
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 2. Production Configuration

```python
# src/core/config.py
from pydantic import BaseSettings
from typing import Dict, Any

class ProductionSettings(BaseSettings):
    """Production environment settings."""
    
    # Required settings
    NOTION_TOKEN: str
    TELEGRAM_TOKEN: str
    OPENROUTER_API_KEY: str
    
    # Optional settings
    LOG_LEVEL: str = "INFO"
    MAX_WORKERS: int = 4
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    # Database settings
    REDIS_URL: str = "redis://localhost:6379"
    DATABASE_URL: str = "postgresql://localhost/notion_bot"
    
    class Config:
        env_file = ".env.production"
        case_sensitive = True
```

### 3. Monitoring and Logging

```python
# src/monitoring/metrics.py
import time
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any

# Metrics
request_count = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration')
active_connections = Gauge('active_connections', 'Active connections')

class MetricsCollector:
    """Collect application metrics."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def record_request(self, method: str, endpoint: str, duration: float):
        """Record request metrics."""
        request_count.labels(method=method, endpoint=endpoint).inc()
        request_duration.observe(duration)
    
    def record_error(self, error_type: str, context: Dict[str, Any]):
        """Record error metrics."""
        error_count.labels(type=error_type).inc()
        logger.error(f"Error: {error_type}", extra=context)
```

## Contributing Guidelines

### 1. Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes**
   - Follow code standards
   - Add tests
   - Update documentation

3. **Run Tests**
   ```bash
   pytest tests/
   coverage run -m pytest
   coverage report
   ```

4. **Create Pull Request**
   - Clear title and description
   - Link to related issues
   - Include test results

### 2. Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Error handling implemented
- [ ] Performance considerations
- [ ] Security implications reviewed

### 3. Release Process

```bash
# 1. Update version
bump2version minor  # or major/patch

# 2. Update changelog
git add CHANGELOG.md

# 3. Create release
git tag v1.0.0
git push origin main --tags

# 4. Deploy to production
docker build -t notion-bot:v1.0.0 .
docker push notion-bot:v1.0.0
```

## Best Practices Summary

### 1. Code Quality
- Use type hints everywhere
- Write comprehensive tests
- Follow SOLID principles
- Implement proper error handling

### 2. Performance
- Use async/await properly
- Implement caching strategies
- Batch operations when possible
- Monitor resource usage

### 3. Security
- Validate all inputs
- Use secure configuration
- Implement rate limiting
- Log security events

### 4. Maintainability
- Clear documentation
- Consistent naming conventions
- Modular architecture
- Regular refactoring

---

This development guide provides the foundation for building robust, scalable, and maintainable extensions to the Notion-Telegram-LLM integration system. Follow these guidelines to ensure code quality and system reliability.