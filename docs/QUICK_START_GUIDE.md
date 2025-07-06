# Quick Start Guide

## Overview

This guide will help you get the Notion-Telegram-LLM integration system up and running in less than 15 minutes.

## Prerequisites

- Python 3.8 or higher
- Notion account with API access
- Telegram Bot Token
- OpenRouter API key for LLM features
- Yandex.Disk account (for file uploads)

## Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd notion-telegram-llm
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Core API Keys
NOTION_TOKEN=secret_xxxxxxxxxxxx
TELEGRAM_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
YA_ACCESS_TOKEN=y0_xxxxxxxxxxxx

# Database IDs (get from Notion URLs)
NOTION_TASKS_DB_ID=12345678-1234-1234-1234-123456789abc
NOTION_IDEAS_DB_ID=12345678-1234-1234-1234-123456789abc
NOTION_MATERIALS_DB_ID=12345678-1234-1234-1234-123456789abc
NOTION_PROJECTS_DB_ID=12345678-1234-1234-1234-123456789abc

# Optional: LLM Configuration
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 3. Notion Setup

#### Create Required Databases

1. **Tasks Database**
   - Create a new database in Notion
   - Add these properties:
     - `Задача` (Title)
     - `Статус` (Status: To do, In Progress, Done)
     - `Участники` (People)
     - `Проект` (Relation to Projects)
     - `Категория` (Multi-select)
     - `Приоритет` (Select: High, Medium, Low)
   - Copy the database ID from the URL

2. **Ideas Database**
   - Create database with properties:
     - `Name` (Title)
     - `Статус` (Status)
     - `Теги` (Multi-select)
     - `Описание` (Rich text)
     - `URL` (URL)

3. **Materials Database**
   - Create database with properties:
     - `Name` (Title)
     - `Статус` (Status)
     - `URL` (URL)
     - `Описание` (Rich text)

#### Setup Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Create a new integration
3. Copy the integration token
4. Share your databases with the integration

## Basic Usage

### 1. Start the Telegram Bot

```bash
python simple_bot.py
```

### 2. Test Basic Commands

Send these commands to your bot:

- `/start` - Initialize the bot
- `/task` - Task management menu
- `/stats` - View usage statistics
- Send any file - Auto-upload to Yandex.Disk + create Notion record

### 3. Test Core Services

```python
# Test Notion Service
from src.services.notion_service import NotionService

async def test_notion():
    service = NotionService()
    await service.initialize()
    
    # List tasks
    tasks = await service.query_database("your_tasks_db_id")
    print(f"Found {len(tasks)} tasks")
    
    await service.cleanup()

# Run test
import asyncio
asyncio.run(test_notion())
```

### 4. Test LLM Service

```python
# Test LLM Analysis
from services.llm_service import AdvancedLLMService

async def test_llm():
    llm_service = AdvancedLLMService()
    
    # Analyze a database
    analysis = await llm_service.analyze_database_with_llm(
        db_name="tasks",
        analysis_type="summary",
        limit=10
    )
    
    print(f"Analysis: {analysis}")

asyncio.run(test_llm())
```

## Common Operations

### Create a Task

```python
from src.repositories.notion_repository import NotionTaskRepository
from src.models.base import TaskDTO
from notion_client import AsyncClient

async def create_task():
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    repo = NotionTaskRepository(client, os.getenv("NOTION_TASKS_DB_ID"))
    
    task = TaskDTO(
        title="Test Task",
        description="Testing the API",
        status="To Do",
        priority="High"
    )
    
    created = await repo.create(task)
    print(f"Created task: {created.id}")

asyncio.run(create_task())
```

### Upload File and Create Material

```python
from simple_bot import YandexUploader, NotionManager

async def upload_and_save():
    uploader = YandexUploader()
    notion_manager = NotionManager()
    
    # Upload file
    result = await uploader.upload_file(
        "https://example.com/document.pdf",
        "test_document.pdf"
    )
    
    if result['success']:
        # Create material record
        material = await notion_manager.create_material(
            fields={
                "name": "Test Document",
                "description": "Sample document upload"
            },
            file_url=result['url'],
            file_name="test_document.pdf"
        )
        print(f"Created material: {material}")

asyncio.run(upload_and_save())
```

### Bulk Operations

```python
from services.advanced_notion_service import AdvancedNotionService, NotionUpdate

async def bulk_update():
    service = AdvancedNotionService()
    
    # Update multiple pages
    updates = [
        ("page_id_1", [NotionUpdate("Status", "Done", "select")]),
        ("page_id_2", [NotionUpdate("Priority", "High", "select")])
    ]
    
    results = await service.update_pages_bulk(updates)
    print(f"Updated {len(results)} pages")

asyncio.run(bulk_update())
```

## Troubleshooting

### Common Issues

1. **Database not found**
   - Check database ID in .env
   - Ensure integration has access to database
   - Verify database exists and isn't archived

2. **Authentication errors**
   - Check API tokens are correct
   - Verify tokens have proper permissions
   - Check token expiration

3. **Rate limiting**
   - Notion API: 3 requests/second
   - Add delays between requests
   - Use bulk operations when possible

4. **Import errors**
   - Check Python path
   - Verify all dependencies installed
   - Check file structure

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check

```python
async def health_check():
    """Check all services are working"""
    
    # Test Notion connection
    try:
        from src.services.notion_service import NotionService
        service = NotionService()
        await service.initialize()
        databases = await service.query_database("your_db_id")
        print(f"✅ Notion: {len(databases)} records")
        await service.cleanup()
    except Exception as e:
        print(f"❌ Notion: {e}")
    
    # Test LLM service
    try:
        from services.llm_service import AdvancedLLMService
        llm = AdvancedLLMService()
        result = await llm._call_llm("Test message", "general")
        print(f"✅ LLM: Response received")
    except Exception as e:
        print(f"❌ LLM: {e}")
    
    # Test file upload
    try:
        from simple_bot import YandexUploader
        uploader = YandexUploader()
        print(f"✅ Yandex.Disk: Uploader ready")
    except Exception as e:
        print(f"❌ Yandex.Disk: {e}")

asyncio.run(health_check())
```

## Next Steps

1. **Read the Full API Documentation** - `docs/API_DOCUMENTATION.md`
2. **Explore Examples** - Check the `examples/` directory
3. **Set up Development Environment** - See `docs/DEVELOPMENT_GUIDE.md`
4. **Configure Advanced Features** - Database schemas, custom LLM prompts
5. **Deploy to Production** - See deployment guides

## Getting Help

- **Documentation**: Complete API reference in `docs/`
- **Issues**: Check existing issues and common problems
- **Code Examples**: Browse the codebase for patterns
- **Schema Reference**: Check `notion_database_schemas.py` for database structure

## Performance Tips

1. **Use bulk operations** for multiple records
2. **Implement caching** for frequently accessed data
3. **Batch API calls** to respect rate limits
4. **Monitor token usage** for LLM calls
5. **Use async/await** properly for concurrent operations

## Security Best Practices

1. **Never commit tokens** to version control
2. **Use environment variables** for sensitive data
3. **Validate input data** before processing
4. **Implement proper error handling**
5. **Log security events** appropriately

---

You're now ready to start building with the Notion-Telegram-LLM integration system! 🚀