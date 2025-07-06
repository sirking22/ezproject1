# Notion-Telegram-LLM Integration API Documentation

## Overview

This documentation covers all public APIs, functions, and components for the Notion-Telegram-LLM integration system. The system provides automated task management, content generation, file handling, and intelligent processing capabilities.

## Table of Contents

1. [Core Services](#core-services)
2. [Data Models](#data-models)
3. [Repositories](#repositories)
4. [Telegram Bot Handlers](#telegram-bot-handlers)
5. [Utilities](#utilities)
6. [Database Schemas](#database-schemas)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)

---

## Core Services

### Advanced LLM Service

**Location**: `services/llm_service.py`

The Advanced LLM Service provides intelligent processing capabilities using large language models for Notion operations.

#### `AdvancedLLMService`

**Constructor**
```python
def __init__(self):
    """Initialize LLM service with OpenRouter API configuration."""
```

**Methods**

##### `analyze_database_with_llm(db_name, analysis_type="comprehensive", limit=None)`
Analyzes a Notion database using LLM intelligence.

**Parameters:**
- `db_name` (str): Name of the database to analyze
- `analysis_type` (str): Type of analysis ("comprehensive", "summary", "detailed")
- `limit` (int, optional): Maximum number of records to analyze

**Returns:** `Dict[str, Any]` - Analysis results with insights and recommendations

**Example:**
```python
llm_service = AdvancedLLMService()
analysis = await llm_service.analyze_database_with_llm(
    db_name="tasks",
    analysis_type="comprehensive",
    limit=50
)
print(f"Analysis: {analysis['llm_analysis']}")
```

##### `bulk_categorize_pages(db_name, category_property, criteria, limit=None)`
Performs mass categorization of pages using LLM.

**Parameters:**
- `db_name` (str): Database name
- `category_property` (str): Property to update with categories
- `criteria` (str): Categorization criteria
- `limit` (int, optional): Maximum pages to process

**Returns:** `Dict[str, Any]` - Results with success/failure counts

**Example:**
```python
result = await llm_service.bulk_categorize_pages(
    db_name="ideas",
    category_property="Категория",
    criteria="Categorize by technology type",
    limit=100
)
print(f"Categorized {result['categorized_pages']} pages")
```

##### `intelligent_data_extraction(source_text, target_db, extraction_schema)`
Extracts structured data from text and creates Notion records.

**Parameters:**
- `source_text` (str): Source text to extract from
- `target_db` (str): Target database name
- `extraction_schema` (Dict[str, str]): Schema for extraction

**Returns:** `Dict[str, Any]` - Extraction results

**Example:**
```python
result = await llm_service.intelligent_data_extraction(
    source_text="Meeting notes: Discuss new project timeline...",
    target_db="tasks",
    extraction_schema={"title": "task_name", "description": "details"}
)
```

##### `smart_relation_builder(source_db, target_db, relation_criteria)`
Intelligently creates relationships between database records.

**Parameters:**
- `source_db` (str): Source database name
- `target_db` (str): Target database name  
- `relation_criteria` (str): Criteria for creating relations

**Returns:** `Dict[str, Any]` - Relationship creation results

**Example:**
```python
result = await llm_service.smart_relation_builder(
    source_db="tasks",
    target_db="projects",
    relation_criteria="Link tasks to relevant projects"
)
```

##### `bulk_content_generation(db_name, template_field, target_field, generation_prompt, limit=None)`
Generates content for multiple database records.

**Parameters:**
- `db_name` (str): Database name
- `template_field` (str): Field containing template data
- `target_field` (str): Field to update with generated content
- `generation_prompt` (str): Prompt for content generation
- `limit` (int, optional): Maximum records to process

**Returns:** `Dict[str, Any]` - Generation results

**Example:**
```python
result = await llm_service.bulk_content_generation(
    db_name="ideas",
    template_field="Name",
    target_field="Описание",
    generation_prompt="Create detailed description based on the idea name",
    limit=50
)
```

---

### Advanced Notion Service

**Location**: `services/advanced_notion_service.py`

Provides advanced Notion operations with mass editing and bulk operations.

#### `AdvancedNotionService`

**Constructor**
```python
def __init__(self):
    """Initialize with Notion token and database configuration."""
```

**Methods**

##### `get_database_schema(db_id)`
Retrieves database schema information.

**Parameters:**
- `db_id` (str): Database ID

**Returns:** `Dict[str, Any]` - Database schema

**Example:**
```python
notion_service = AdvancedNotionService()
schema = await notion_service.get_database_schema("database_id")
```

##### `query_database_bulk(db_id, filters=None, sorts=None, limit=None)`
Performs bulk database queries with filtering and sorting.

**Parameters:**
- `db_id` (str): Database ID
- `filters` (List[NotionFilter], optional): Query filters
- `sorts` (List[Dict], optional): Sort options
- `limit` (int, optional): Result limit

**Returns:** `List[Dict]` - Query results

**Example:**
```python
from services.advanced_notion_service import NotionFilter

filters = [
    NotionFilter("Status", "select", {"equals": "In Progress"})
]
results = await notion_service.query_database_bulk(
    db_id="database_id",
    filters=filters,
    limit=100
)
```

##### `update_pages_bulk(page_updates)`
Performs bulk page updates.

**Parameters:**
- `page_updates` (List[Tuple[str, List[NotionUpdate]]]): List of page updates

**Returns:** `List[Dict]` - Update results

**Example:**
```python
from services.advanced_notion_service import NotionUpdate

updates = [
    ("page_id_1", [NotionUpdate("Status", "Done", "select")]),
    ("page_id_2", [NotionUpdate("Priority", "High", "select")])
]
results = await notion_service.update_pages_bulk(updates)
```

##### `create_relations_bulk(relations)`
Creates multiple relationships between pages.

**Parameters:**
- `relations` (List[NotionRelation]): List of relations to create

**Returns:** `List[Dict]` - Creation results

**Example:**
```python
from services.advanced_notion_service import NotionRelation

relations = [
    NotionRelation("source_page_id", "target_page_id", "relation_property")
]
results = await notion_service.create_relations_bulk(relations)
```

##### `analyze_database_content(db_id, analysis_type="summary")`
Analyzes database content and structure.

**Parameters:**
- `db_id` (str): Database ID
- `analysis_type` (str): Analysis type ("summary", "detailed")

**Returns:** `Dict` - Analysis results

**Example:**
```python
analysis = await notion_service.analyze_database_content(
    db_id="database_id",
    analysis_type="detailed"
)
```

##### `smart_search(query, databases=None)`
Performs intelligent search across databases.

**Parameters:**
- `query` (str): Search query
- `databases` (List[str], optional): Database names to search

**Returns:** `Dict` - Search results by database

**Example:**
```python
results = await notion_service.smart_search(
    query="design task",
    databases=["tasks", "projects"]
)
```

---

### Notion Service

**Location**: `src/services/notion_service.py`

Core Notion service for standard operations.

#### `NotionService`

**Constructor**
```python
def __init__(self):
    """Initialize with settings and Notion client."""
```

**Methods**

##### `initialize()`
Initializes the Notion client session.

**Returns:** `None`

**Example:**
```python
notion_service = NotionService()
await notion_service.initialize()
```

##### `get_database(database_id)`
Retrieves database metadata.

**Parameters:**
- `database_id` (str): Database ID

**Returns:** `NotionDatabase` - Database model

**Example:**
```python
database = await notion_service.get_database("database_id")
```

##### `query_database(database_id, filter_conditions=None, sorts=None)`
Queries database with optional filters and sorting.

**Parameters:**
- `database_id` (str): Database ID
- `filter_conditions` (Dict, optional): Filter conditions
- `sorts` (List[Dict], optional): Sort options

**Returns:** `List[NotionPage]` - Query results

**Example:**
```python
pages = await notion_service.query_database(
    database_id="database_id",
    filter_conditions={
        "property": "Status",
        "select": {"equals": "In Progress"}
    }
)
```

##### `create_page(database_id, properties, content=None)`
Creates a new page in the specified database.

**Parameters:**
- `database_id` (str): Database ID
- `properties` (Dict[str, Any]): Page properties
- `content` (List[Dict], optional): Page content blocks

**Returns:** `NotionPage` - Created page

**Example:**
```python
properties = {
    "Name": {"title": [{"text": {"content": "New Task"}}]},
    "Status": {"select": {"name": "To Do"}}
}
page = await notion_service.create_page("database_id", properties)
```

##### `update_page(page_id, properties, archived=False)`
Updates an existing page.

**Parameters:**
- `page_id` (str): Page ID
- `properties` (Dict[str, Any]): Updated properties
- `archived` (bool): Whether to archive the page

**Returns:** `NotionPage` - Updated page

**Example:**
```python
properties = {
    "Status": {"select": {"name": "Done"}}
}
page = await notion_service.update_page("page_id", properties)
```

##### `get_page_content(page_id)`
Retrieves page content blocks.

**Parameters:**
- `page_id` (str): Page ID

**Returns:** `List[Union[TextBlock, TodoBlock, HeadingBlock]]` - Content blocks

**Example:**
```python
content = await notion_service.get_page_content("page_id")
```

##### `search(query, filter_params=None)`
Searches pages and databases.

**Parameters:**
- `query` (str): Search query
- `filter_params` (Dict, optional): Filter parameters

**Returns:** `List[NotionPage]` - Search results

**Example:**
```python
results = await notion_service.search("design task")
```

---

## Data Models

### Notion Models

**Location**: `src/models/notion_models.py`

#### `NotionPage`
Represents a Notion page.

**Fields:**
- `id` (str): Page ID
- `created_time` (datetime): Creation timestamp
- `last_edited_time` (datetime): Last edit timestamp
- `archived` (bool): Archive status
- `properties` (Dict): Page properties

**Example:**
```python
page = NotionPage(
    id="page_id",
    created_time=datetime.now(),
    last_edited_time=datetime.now(),
    properties={"Name": {"title": [{"text": {"content": "Task Name"}}]}}
)
```

#### `NotionDatabase`
Represents a Notion database.

**Fields:**
- `id` (str): Database ID
- `created_time` (datetime): Creation timestamp
- `last_edited_time` (datetime): Last edit timestamp
- `title` (List[Dict]): Database title
- `properties` (Dict): Database properties
- `archived` (bool): Archive status

#### Block Models

##### `TextBlock`
Text paragraph block.

**Fields:**
- `type` (str): Block type ("paragraph")
- `paragraph` (Dict): Paragraph content

##### `TodoBlock`
Todo/checklist block.

**Fields:**
- `type` (str): Block type ("to_do")
- `to_do` (Dict): Todo content
- `checked` (bool): Completion status

##### `HeadingBlock`
Heading block (H1, H2, H3).

**Fields:**
- `type` (str): Block type ("heading_1", "heading_2", "heading_3")
- `heading_1/2/3` (Dict): Heading content

### Base Models

**Location**: `src/models/base.py`

#### `Task`
Task data model.

**Fields:**
- `id` (str): Task ID
- `title` (str): Task title
- `description` (str): Task description
- `status` (str): Task status
- `priority` (str): Task priority
- `tags` (List[str]): Task tags
- `due_date` (datetime): Due date
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Update timestamp
- `completed_at` (datetime): Completion timestamp

**Example:**
```python
task = Task(
    id="task_id",
    title="Complete documentation",
    description="Write comprehensive API docs",
    status="In Progress",
    priority="High",
    tags=["documentation", "api"],
    due_date=datetime.now() + timedelta(days=7)
)
```

---

## Repositories

### Notion Repository

**Location**: `src/repositories/notion_repository.py`

#### `NotionTaskRepository`
Repository for task operations.

**Constructor**
```python
def __init__(self, client: AsyncClient, database_id: str):
    """Initialize with Notion client and database ID."""
```

**Methods**

##### `validate_database()`
Validates database connection and structure.

**Returns:** `Tuple[bool, str]` - Success status and message

**Example:**
```python
repo = NotionTaskRepository(client, "database_id")
is_valid, message = await repo.validate_database()
```

##### `get(id)`
Retrieves task by ID.

**Parameters:**
- `id` (str): Task ID

**Returns:** `Optional[TaskDTO]` - Task data

**Example:**
```python
task = await repo.get("task_id")
```

##### `create(task)`
Creates new task.

**Parameters:**
- `task` (TaskDTO): Task data

**Returns:** `TaskDTO` - Created task

**Example:**
```python
task_data = TaskDTO(title="New Task", status="To Do")
created_task = await repo.create(task_data)
```

##### `update(id, task)`
Updates existing task.

**Parameters:**
- `id` (str): Task ID
- `task` (TaskDTO): Updated task data

**Returns:** `Optional[TaskDTO]` - Updated task

**Example:**
```python
updated_task = await repo.update("task_id", task_data)
```

##### `delete(id)`
Deletes (archives) task.

**Parameters:**
- `id` (str): Task ID

**Returns:** `bool` - Success status

**Example:**
```python
success = await repo.delete("task_id")
```

##### `list(params=None)`
Lists tasks with optional filtering.

**Parameters:**
- `params` (Dict, optional): Filter parameters

**Returns:** `List[TaskDTO]` - Task list

**Example:**
```python
# Get all active tasks
tasks = await repo.list({
    "status": {"not_equals": "Completed"}
})

# Get high priority tasks
high_priority_tasks = await repo.list({
    "priority": "High"
})
```

#### `NotionRepository`
General purpose Notion repository.

**Constructor**
```python
def __init__(self, settings: Settings):
    """Initialize with application settings."""
```

**Methods**

##### `create_idea(idea_data)`
Creates new idea record.

**Parameters:**
- `idea_data` (Dict[str, Any]): Idea data

**Returns:** `Dict[str, Any]` - Created idea

**Example:**
```python
idea_data = {
    "name": "New App Idea",
    "description": "Mobile app for task management",
    "status": "To Do",
    "tags": ["mobile", "productivity"]
}
idea = await repo.create_idea(idea_data)
```

##### `get_ideas(sort_by=None, limit=100)`
Retrieves ideas with optional sorting.

**Parameters:**
- `sort_by` (str, optional): Sort field
- `limit` (int): Result limit

**Returns:** `List[Dict[str, Any]]` - Ideas list

**Example:**
```python
ideas = await repo.get_ideas(sort_by="created_time", limit=50)
```

---

## Telegram Bot Handlers

### Task Handler

**Location**: `src/services/telegram/handlers/tasks.py`

#### `TaskHandler`
Handles Telegram task-related commands.

**Constructor**
```python
def __init__(self, task_repository: NotionTaskRepository):
    """Initialize with task repository."""
```

**Methods**

##### `task_command(update, context)`
Handles /task command.

**Parameters:**
- `update` (Update): Telegram update
- `context` (ContextTypes.DEFAULT_TYPE): Bot context

**Returns:** `None`

**Example:**
```python
handler = TaskHandler(task_repository)
await handler.task_command(update, context)
```

##### `list_tasks(update, context)`
Lists user's tasks.

**Parameters:**
- `update` (Update): Telegram update
- `context` (ContextTypes.DEFAULT_TYPE): Bot context

**Returns:** `None`

**Example:**
```python
await handler.list_tasks(update, context)
```

##### `update_task_status(update, context)`
Handles task status updates.

**Parameters:**
- `update` (Update): Telegram update
- `context` (ContextTypes.DEFAULT_TYPE): Bot context

**Returns:** `None`

**Example:**
```python
await handler.update_task_status(update, context)
```

### Main Bot

**Location**: `simple_bot.py`

#### `LLMProcessor`
Processes natural language using LLM.

**Constructor**
```python
def __init__(self):
    """Initialize with LLM configuration."""
```

**Methods**

##### `parse_natural_language(text)`
Parses natural language text into structured data.

**Parameters:**
- `text` (str): Natural language text

**Returns:** `Dict[str, Any]` - Parsed data

**Example:**
```python
processor = LLMProcessor()
result = await processor.parse_natural_language(
    "Create a high priority task for designing the new website"
)
```

##### `analyze_design(image_url, context="")`
Analyzes design images using AI.

**Parameters:**
- `image_url` (str): Image URL
- `context` (str): Additional context

**Returns:** `Dict[str, Any]` - Analysis results

**Example:**
```python
analysis = await processor.analyze_design(
    image_url="https://example.com/design.png",
    context="Website mockup"
)
```

#### `YandexUploader`
Handles file uploads to Yandex.Disk.

**Constructor**
```python
def __init__(self):
    """Initialize with Yandex.Disk configuration."""
```

**Methods**

##### `upload_file(file_url, filename)`
Uploads file to Yandex.Disk.

**Parameters:**
- `file_url` (str): Source file URL
- `filename` (str): Target filename

**Returns:** `Dict[str, Any]` - Upload results

**Example:**
```python
uploader = YandexUploader()
result = await uploader.upload_file(
    file_url="https://telegram.org/file.jpg",
    filename="uploaded_image.jpg"
)
```

#### `VideoProcessor`
Processes video files.

**Methods**

##### `extract_frame(video_url)` (static)
Extracts frame from video.

**Parameters:**
- `video_url` (str): Video URL

**Returns:** `Optional[str]` - Frame file path

**Example:**
```python
frame_path = await VideoProcessor.extract_frame("https://example.com/video.mp4")
```

#### `NotionManager`
Manages Notion operations for the bot.

**Constructor**
```python
def __init__(self):
    """Initialize with Notion client."""
```

**Methods**

##### `create_idea(fields, file_url, file_name)`
Creates idea record in Notion.

**Parameters:**
- `fields` (Dict[str, Any]): Idea fields
- `file_url` (str): Associated file URL
- `file_name` (str): File name

**Returns:** `Dict[str, Any]` - Created idea

**Example:**
```python
manager = NotionManager()
idea = await manager.create_idea(
    fields={"name": "App Idea", "description": "Cool app"},
    file_url="https://example.com/file.pdf",
    file_name="idea_doc.pdf"
)
```

##### `create_material(fields, file_url, file_name)`
Creates material record in Notion.

**Parameters:**
- `fields` (Dict[str, Any]): Material fields
- `file_url` (str): File URL
- `file_name` (str): File name

**Returns:** `Dict[str, Any]` - Created material

**Example:**
```python
material = await manager.create_material(
    fields={"name": "Design Asset", "description": "Logo design"},
    file_url="https://example.com/logo.png",
    file_name="company_logo.png"
)
```

---

## Utilities

### Console Helpers

**Location**: `utils/console_helpers.py`

#### `setup_logging(level=logging.INFO, log_file=None)`
Sets up logging with color formatting.

**Parameters:**
- `level` (int): Logging level
- `log_file` (str, optional): Log file path

**Returns:** `logging.Logger` - Configured logger

**Example:**
```python
from utils.console_helpers import setup_logging
logger = setup_logging(level=logging.INFO, log_file="app.log")
```

#### `ProcessTracker`
Tracks long-running processes.

**Constructor**
```python
def __init__(self, logger: logging.Logger):
    """Initialize with logger."""
```

**Methods**

##### `track(name)` (context manager)
Tracks process execution time.

**Parameters:**
- `name` (str): Process name

**Example:**
```python
tracker = ProcessTracker(logger)
with tracker.track("Database operation"):
    # Long running operation
    await process_database()
```

#### `Timer`
Context manager for measuring execution time.

**Constructor**
```python
def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
    """Initialize with operation name and logger."""
```

**Example:**
```python
with Timer("API call"):
    response = await make_api_call()
```

#### `ProgressBar`
Console progress bar.

**Constructor**
```python
def __init__(self, total: int, prefix: str = '', suffix: str = ''):
    """Initialize with total items and labels."""
```

**Methods**

##### `update(current)`
Updates progress bar.

**Parameters:**
- `current` (int): Current progress

**Example:**
```python
progress = ProgressBar(100, prefix="Processing")
for i in range(100):
    # Do work
    progress.update(i + 1)
```

#### Utility Functions

##### `with_timeout(timeout_seconds)`
Decorator for function timeout.

**Parameters:**
- `timeout_seconds` (int): Timeout in seconds

**Example:**
```python
@with_timeout(30)
async def long_running_operation():
    await slow_api_call()
```

##### `safe_request(url, method="GET", timeout=30, **kwargs)`
Safe HTTP request with timeout.

**Parameters:**
- `url` (str): Request URL
- `method` (str): HTTP method
- `timeout` (int): Request timeout
- `**kwargs`: Additional request parameters

**Returns:** `requests.Response` - HTTP response

**Example:**
```python
response = safe_request("https://api.example.com/data", timeout=10)
```

---

## Database Schemas

### Database Schema Management

**Location**: `notion_database_schemas.py`

#### `DatabaseSchema`
Database schema definition.

**Fields:**
- `name` (str): Database name
- `database_id` (str): Notion database ID
- `description` (str): Database description
- `properties` (Dict): Property definitions
- `status_options` (Dict): Status field options
- `select_options` (Dict): Select field options
- `multi_select_options` (Dict): Multi-select field options
- `relations` (Dict): Relationship definitions

**Example:**
```python
schema = DatabaseSchema(
    name="Tasks",
    database_id="database_id",
    description="Project tasks database",
    properties={
        "Name": {"type": "title"},
        "Status": {"type": "status"},
        "Priority": {"type": "select"}
    },
    status_options={
        "Status": ["To Do", "In Progress", "Done"]
    }
)
```

#### Schema Functions

##### `get_database_schema(db_name)`
Retrieves database schema by name.

**Parameters:**
- `db_name` (str): Database name

**Returns:** `Optional[DatabaseSchema]` - Database schema

**Example:**
```python
schema = get_database_schema("tasks")
```

##### `get_database_id(db_name)`
Gets database ID by name.

**Parameters:**
- `db_name` (str): Database name

**Returns:** `str` - Database ID

**Example:**
```python
db_id = get_database_id("tasks")
```

##### `get_status_options(db_name, property_name)`
Gets status options for a property.

**Parameters:**
- `db_name` (str): Database name
- `property_name` (str): Property name

**Returns:** `List[str]` - Status options

**Example:**
```python
statuses = get_status_options("tasks", "Status")
```

##### `validate_property_value(db_name, property_name, value)`
Validates property value against schema.

**Parameters:**
- `db_name` (str): Database name
- `property_name` (str): Property name
- `value` (str): Value to validate

**Returns:** `bool` - Validation result

**Example:**
```python
is_valid = validate_property_value("tasks", "Status", "In Progress")
```

---

## Configuration

### Settings

**Location**: `src/core/config.py`

#### `Settings`
Application configuration.

**Fields:**
- `NOTION_TOKEN` (str): Notion API token
- `TELEGRAM_BOT_TOKEN` (str): Telegram bot token
- `OPENROUTER_API_KEY` (str): OpenRouter API key
- `NOTION_DATABASES` (Dict): Database configurations

**Example:**
```python
settings = Settings(
    NOTION_TOKEN="secret_token",
    TELEGRAM_BOT_TOKEN="bot_token",
    OPENROUTER_API_KEY="api_key"
)
```

---

## Usage Examples

### Complete Task Management Workflow

```python
import asyncio
from src.services.notion_service import NotionService
from src.repositories.notion_repository import NotionTaskRepository
from src.services.telegram.handlers.tasks import TaskHandler
from notion_client import AsyncClient

async def main():
    # Initialize services
    notion_service = NotionService()
    await notion_service.initialize()
    
    # Create task repository
    client = AsyncClient(auth="your_token")
    task_repo = NotionTaskRepository(client, "database_id")
    
    # Validate database
    is_valid, message = await task_repo.validate_database()
    if not is_valid:
        print(f"Database validation failed: {message}")
        return
    
    # Create new task
    from src.models.base import TaskDTO
    task_data = TaskDTO(
        title="Complete API documentation",
        description="Write comprehensive documentation",
        status="In Progress",
        priority="High"
    )
    
    # Save to Notion
    created_task = await task_repo.create(task_data)
    print(f"Created task: {created_task.id}")
    
    # List all tasks
    tasks = await task_repo.list()
    print(f"Total tasks: {len(tasks)}")
    
    # Update task status
    task_data.status = "Done"
    updated_task = await task_repo.update(created_task.id, task_data)
    print(f"Updated task status: {updated_task.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

### LLM-Powered Database Analysis

```python
from services.llm_service import AdvancedLLMService

async def analyze_projects():
    llm_service = AdvancedLLMService()
    
    # Analyze database content
    analysis = await llm_service.analyze_database_with_llm(
        db_name="projects",
        analysis_type="comprehensive",
        limit=100
    )
    
    print("Database Analysis Results:")
    print(f"Total pages: {analysis['data_summary']['total_pages']}")
    print(f"LLM insights: {analysis['llm_analysis']}")
    
    # Categorize projects
    categorization = await llm_service.bulk_categorize_pages(
        db_name="projects",
        category_property="Category",
        criteria="Categorize by project type and complexity",
        limit=50
    )
    
    print(f"Categorized {categorization['categorized_pages']} projects")

# Run analysis
asyncio.run(analyze_projects())
```

### File Upload and Processing

```python
from simple_bot import YandexUploader, LLMProcessor, NotionManager

async def process_uploaded_file():
    # Initialize components
    uploader = YandexUploader()
    processor = LLMProcessor()
    notion_manager = NotionManager()
    
    # Upload file
    file_url = "https://example.com/document.pdf"
    filename = "project_document.pdf"
    
    upload_result = await uploader.upload_file(file_url, filename)
    
    if upload_result['success']:
        # Process with LLM
        analysis = await processor.parse_natural_language(
            "This is a project document containing design specifications"
        )
        
        # Create record in Notion
        material = await notion_manager.create_material(
            fields={
                "name": analysis['name'],
                "description": analysis['description'],
                "tags": analysis.get('tags', [])
            },
            file_url=upload_result['url'],
            file_name=filename
        )
        
        print(f"Created material: {material['id']}")

# Run processing
asyncio.run(process_uploaded_file())
```

### Telegram Bot Integration

```python
from telegram.ext import Application, CommandHandler
from src.services.telegram.handlers.tasks import TaskHandler
from src.repositories.notion_repository import NotionTaskRepository

def setup_bot():
    # Initialize bot
    app = Application.builder().token("your_bot_token").build()
    
    # Setup task handler
    task_repo = NotionTaskRepository(client, "database_id")
    task_handler = TaskHandler(task_repo)
    
    # Add handlers
    app.add_handler(CommandHandler("task", task_handler.task_command))
    app.add_handler(CommandHandler("list", task_handler.list_tasks))
    
    # Start bot
    app.run_polling()

# Setup and run bot
setup_bot()
```

### Database Schema Validation

```python
from notion_database_schemas import get_database_schema, validate_property_value

def validate_task_data(task_data):
    """Validate task data against schema"""
    schema = get_database_schema("tasks")
    
    if not schema:
        return False, "Schema not found"
    
    # Validate status
    if "status" in task_data:
        is_valid = validate_property_value("tasks", "Status", task_data["status"])
        if not is_valid:
            return False, f"Invalid status: {task_data['status']}"
    
    # Validate priority
    if "priority" in task_data:
        is_valid = validate_property_value("tasks", "Priority", task_data["priority"])
        if not is_valid:
            return False, f"Invalid priority: {task_data['priority']}"
    
    return True, "Valid"

# Example usage
task_data = {
    "title": "New Task",
    "status": "In Progress",
    "priority": "High"
}

is_valid, message = validate_task_data(task_data)
print(f"Validation result: {is_valid}, {message}")
```

---

## Error Handling

### Common Error Patterns

```python
from src.services.notion_service import NotionService, NotionError

async def handle_notion_operations():
    notion_service = NotionService()
    
    try:
        await notion_service.initialize()
        
        # Perform operations
        pages = await notion_service.query_database("database_id")
        
    except NotionError as e:
        print(f"Notion API error: {e}")
        
    except Exception as e:
        print(f"General error: {e}")
        
    finally:
        await notion_service.cleanup()
```

### Timeout Handling

```python
from utils.console_helpers import with_timeout

@with_timeout(30)
async def long_running_operation():
    # Operation that might take too long
    await some_slow_api_call()

try:
    await long_running_operation()
except TimeoutError:
    print("Operation timed out")
```

---

## Best Practices

### 1. Always Initialize Services
```python
# Good
notion_service = NotionService()
await notion_service.initialize()

# Use service
await notion_service.query_database("db_id")

# Cleanup
await notion_service.cleanup()
```

### 2. Validate Database Connections
```python
repo = NotionTaskRepository(client, database_id)
is_valid, message = await repo.validate_database()
if not is_valid:
    raise ValueError(f"Database validation failed: {message}")
```

### 3. Use Schema Validation
```python
from notion_database_schemas import validate_property_value

# Validate before creating/updating
if not validate_property_value("tasks", "Status", status_value):
    raise ValueError(f"Invalid status: {status_value}")
```

### 4. Handle Bulk Operations Efficiently
```python
# Process in batches
batch_size = 10
for i in range(0, len(items), batch_size):
    batch = items[i:i + batch_size]
    await process_batch(batch)
    await asyncio.sleep(0.1)  # Rate limiting
```

### 5. Use Progress Tracking
```python
from utils.console_helpers import ProgressBar

progress = ProgressBar(total_items, prefix="Processing")
for i, item in enumerate(items):
    await process_item(item)
    progress.update(i + 1)
```

---

## Rate Limiting and Performance

### Notion API Rate Limits
- Respect 3 requests per second limit
- Use bulk operations when possible
- Implement exponential backoff for retries

### LLM API Optimization
- Cache results when possible
- Use structured prompts for consistent outputs
- Monitor token usage

### Memory Management
- Process large datasets in chunks
- Use generators for large result sets
- Clean up temporary files

---

## Testing

### Unit Tests
```python
import pytest
from src.services.notion_service import NotionService

@pytest.mark.asyncio
async def test_notion_service_initialization():
    service = NotionService()
    await service.initialize()
    assert service.session is not None
    await service.cleanup()
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_task_creation_workflow():
    repo = NotionTaskRepository(client, database_id)
    task = TaskDTO(title="Test Task", status="To Do")
    created = await repo.create(task)
    assert created.title == "Test Task"
    await repo.delete(created.id)
```

---

This documentation provides comprehensive coverage of all public APIs, functions, and components in the system. For additional help or clarification on specific components, refer to the source code or contact the development team.