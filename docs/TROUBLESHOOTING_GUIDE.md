# Troubleshooting Guide

## Overview

This guide covers common issues, error messages, and solutions for the Notion-Telegram-LLM integration system.

## Common Issues

### Authentication & API Keys

#### ❌ `HTTPException: 401 Unauthorized`

**Cause**: Invalid or expired API tokens

**Solutions**:
1. **Check Notion Token**:
   ```bash
   # Test Notion token
   curl -H "Authorization: Bearer YOUR_NOTION_TOKEN" \
        -H "Notion-Version: 2022-06-28" \
        https://api.notion.com/v1/users/me
   ```

2. **Verify Environment Variables**:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   # Check all required tokens
   required_tokens = [
       'NOTION_TOKEN', 'TELEGRAM_TOKEN', 
       'OPENROUTER_API_KEY', 'YA_ACCESS_TOKEN'
   ]
   
   for token in required_tokens:
       value = os.getenv(token)
       if not value:
           print(f"❌ Missing: {token}")
       else:
           print(f"✅ Found: {token} ({len(value)} chars)")
   ```

3. **Regenerate Tokens**:
   - Notion: https://www.notion.so/my-integrations
   - Telegram: @BotFather
   - OpenRouter: https://openrouter.ai/keys

#### ❌ `Database not found` or `object_not_found`

**Cause**: Database ID incorrect or integration lacks access

**Solutions**:
1. **Verify Database ID**:
   ```python
   # Extract ID from Notion URL
   # https://notion.so/username/DATABASE_NAME-32_CHAR_ID?v=...
   # Use the 32-character ID with dashes
   
   def extract_database_id(url):
       # Extract from URL like: .../Database-abc123def456?v=...
       import re
       match = re.search(r'([a-f0-9]{32})', url.replace('-', ''))
       if match:
           id_str = match.group(1)
           # Add dashes: 8-4-4-4-12
           return f"{id_str[:8]}-{id_str[8:12]}-{id_str[12:16]}-{id_str[16:20]}-{id_str[20:]}"
       return None
   ```

2. **Check Integration Access**:
   - Open database in Notion
   - Click "Share" → "Add people, emails, or integrations"
   - Add your integration
   - Set appropriate permissions

3. **Test Database Access**:
   ```python
   from notion_client import AsyncClient
   
   async def test_database_access(db_id):
       client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
       try:
           db = await client.databases.retrieve(database_id=db_id)
           print(f"✅ Database: {db['title']}")
           return True
       except Exception as e:
           print(f"❌ Error: {e}")
           return False
   ```

### Database Schema Issues

#### ❌ `Property 'XYZ' not found in database`

**Cause**: Database schema doesn't match expected properties

**Solutions**:
1. **Check Required Properties**:
   ```python
   from notion_database_schemas import get_database_schema
   
   def validate_database_structure(db_name):
       schema = get_database_schema(db_name)
       if not schema:
           print(f"❌ Schema not found for: {db_name}")
           return False
       
       print(f"Required properties for {db_name}:")
       for prop_name, prop_config in schema.properties.items():
           print(f"  - {prop_name}: {prop_config['type']}")
       
       return True
   ```

2. **Auto-Fix Database Schema**:
   ```python
   from src.repositories.notion_repository import NotionTaskRepository
   
   async def validate_and_suggest_fixes(db_id):
       repo = NotionTaskRepository(client, db_id)
       is_valid, message = await repo.validate_database()
       
       if not is_valid:
           print(f"❌ Validation failed: {message}")
           print("\n🔧 Suggested fixes:")
           
           # Parse missing properties from error message
           if "Missing properties:" in message:
               missing = message.split("Missing properties: ")[1].split("\n")[0]
               props = [p.strip() for p in missing.split(",")]
               
               print("Add these properties to your database:")
               for prop in props:
                   print(f"  - {prop}")
       else:
           print("✅ Database schema is valid")
   ```

3. **Create Missing Properties**:
   ```python
   # Use Notion UI to add missing properties:
   # 1. Open database
   # 2. Click "+" next to properties
   # 3. Choose correct type (title, select, multi_select, etc.)
   # 4. Set options for select/multi-select fields
   ```

#### ❌ `Invalid property value` or `Validation failed`

**Cause**: Property values don't match allowed options

**Solutions**:
1. **Check Valid Options**:
   ```python
   from notion_database_schemas import get_status_options, get_select_options
   
   def show_valid_options(db_name):
       # Check status options
       status_opts = get_status_options(db_name, "Status")
       if status_opts:
           print(f"Valid Status options: {status_opts}")
       
       # Check other select options
       schema = get_database_schema(db_name)
       for prop_name, options in schema.select_options.items():
           print(f"Valid {prop_name} options: {options}")
   ```

2. **Validate Before Update**:
   ```python
   from notion_database_schemas import validate_property_value
   
   def safe_update_task(db_name, property_name, value):
       if validate_property_value(db_name, property_name, value):
           print(f"✅ Valid value: {value}")
           # Proceed with update
       else:
           print(f"❌ Invalid value: {value}")
           # Show valid options
           valid_options = get_select_options(db_name, property_name)
           print(f"Valid options: {valid_options}")
   ```

### LLM Service Issues

#### ❌ `LLM API call failed` or `Rate limit exceeded`

**Cause**: LLM API issues or quota limits

**Solutions**:
1. **Check API Key and Credits**:
   ```python
   import httpx
   
   async def test_llm_api():
       api_key = os.getenv("OPENROUTER_API_KEY")
       
       async with httpx.AsyncClient() as client:
           # Test simple request
           response = await client.post(
               "https://openrouter.ai/api/v1/chat/completions",
               headers={"Authorization": f"Bearer {api_key}"},
               json={
                   "model": "deepseek/deepseek-chat",
                   "messages": [{"role": "user", "content": "Hello"}],
                   "max_tokens": 10
               }
           )
           
           if response.status_code == 200:
               print("✅ LLM API working")
           else:
               print(f"❌ LLM API error: {response.status_code}")
               print(response.text)
   ```

2. **Implement Retry Logic**:
   ```python
   import asyncio
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=10)
   )
   async def robust_llm_call(prompt):
       llm_service = AdvancedLLMService()
       return await llm_service._call_llm(prompt, "analyze")
   ```

3. **Monitor Token Usage**:
   ```python
   def monitor_llm_usage():
       llm_service = AdvancedLLMService()
       stats = llm_service.get_stats()
       
       print(f"Total tokens used: {stats['total_tokens']}")
       print(f"Total requests: {stats['total_requests']}")
       print(f"Avg tokens/request: {stats['avg_tokens_per_request']:.1f}")
       
       # Alert if usage is high
       if stats['total_tokens'] > 50000:
           print("⚠️ High token usage - consider optimizing prompts")
   ```

### File Upload Issues

#### ❌ `Yandex.Disk upload failed`

**Cause**: Network issues, token problems, or file size limits

**Solutions**:
1. **Test Yandex.Disk Connection**:
   ```python
   import aiohttp
   
   async def test_yandex_disk():
       token = os.getenv("YA_ACCESS_TOKEN")
       headers = {"Authorization": f"OAuth {token}"}
       
       async with aiohttp.ClientSession() as session:
           # Test API access
           async with session.get(
               "https://cloud-api.yandex.net/v1/disk",
               headers=headers
           ) as resp:
               if resp.status == 200:
                   data = await resp.json()
                   print(f"✅ Yandex.Disk: {data['used_space']} bytes used")
               else:
                   print(f"❌ Yandex.Disk error: {resp.status}")
   ```

2. **Handle Upload Errors**:
   ```python
   from simple_bot import YandexUploader
   
   async def robust_upload(file_url, filename):
       uploader = YandexUploader()
       
       try:
           result = await uploader.upload_file(file_url, filename)
           if result['success']:
               print(f"✅ Uploaded: {result['url']}")
               return result
           else:
               print(f"❌ Upload failed: {result['error']}")
               
               # Try alternative filename
               alt_filename = f"retry_{int(time.time())}_{filename}"
               result = await uploader.upload_file(file_url, alt_filename)
               return result
               
       except Exception as e:
           print(f"❌ Upload exception: {e}")
           return {'success': False, 'error': str(e)}
   ```

### Telegram Bot Issues

#### ❌ `Bot doesn't respond` or `Webhook errors`

**Cause**: Bot token issues, network problems, or handler errors

**Solutions**:
1. **Test Bot Token**:
   ```python
   import requests
   
   def test_bot_token():
       token = os.getenv("TELEGRAM_TOKEN")
       
       response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
       
       if response.status_code == 200:
           bot_info = response.json()
           print(f"✅ Bot: {bot_info['result']['username']}")
       else:
           print(f"❌ Bot token error: {response.status_code}")
   ```

2. **Check Bot Handlers**:
   ```python
   def debug_bot_handlers(application):
       print("Registered handlers:")
       for group_id, handlers in application.handlers.items():
           print(f"  Group {group_id}:")
           for handler in handlers:
               print(f"    - {type(handler).__name__}")
   ```

3. **Add Error Handler**:
   ```python
   import logging
   from telegram.ext import Application
   
   async def error_handler(update, context):
       logger.error(f"Exception while handling update: {context.error}")
       
       # Send error to developer (optional)
       if update and update.effective_chat:
           await context.bot.send_message(
               chat_id=update.effective_chat.id,
               text="⚠️ Произошла ошибка. Попробуйте позже."
           )
   
   # Add to application
   application.add_error_handler(error_handler)
   ```

### Performance Issues

#### ❌ `Slow response times` or `Timeouts`

**Cause**: Inefficient operations, large datasets, or rate limiting

**Solutions**:
1. **Profile Performance**:
   ```python
   import time
   from utils.console_helpers import Timer
   
   async def profile_operations():
       # Test individual operations
       with Timer("Database query"):
           results = await notion_service.query_database("db_id")
       
       with Timer("LLM processing"):
           analysis = await llm_service.analyze_database_with_llm("tasks")
       
       with Timer("Bulk update"):
           updates = [("page_id", [NotionUpdate("Status", "Done")])]
           await notion_service.update_pages_bulk(updates)
   ```

2. **Optimize Database Queries**:
   ```python
   # Use filters to reduce data
   filters = [NotionFilter("Status", "select", {"not_equals": "Done"})]
   
   # Limit results
   results = await notion_service.query_database_bulk(
       db_id="db_id",
       filters=filters,
       limit=50  # Don't fetch everything
   )
   ```

3. **Implement Caching**:
   ```python
   from functools import lru_cache
   import time
   
   class CachedNotionService:
       def __init__(self):
           self.cache = {}
           self.cache_timeout = 300  # 5 minutes
       
       async def get_database_cached(self, db_id):
           cache_key = f"db_{db_id}"
           now = time.time()
           
           if cache_key in self.cache:
               data, timestamp = self.cache[cache_key]
               if now - timestamp < self.cache_timeout:
                   return data
           
           # Fetch fresh data
           data = await self.get_database(db_id)
           self.cache[cache_key] = (data, now)
           return data
   ```

## Error Messages Reference

### Notion API Errors

| Error Code | Message | Solution |
|------------|---------|----------|
| 400 | `invalid_json` | Check request format |
| 401 | `unauthorized` | Verify API token |
| 403 | `restricted_resource` | Check integration permissions |
| 404 | `object_not_found` | Verify database/page ID |
| 409 | `conflict_error` | Check for concurrent updates |
| 429 | `rate_limited` | Implement backoff strategy |
| 500 | `internal_server_error` | Retry with exponential backoff |

### Telegram API Errors

| Error Code | Description | Solution |
|------------|-------------|----------|
| 400 | Bad Request | Check message format |
| 401 | Unauthorized | Verify bot token |
| 403 | Forbidden | Check bot permissions |
| 404 | Not Found | Verify chat/user exists |
| 429 | Too Many Requests | Implement rate limiting |

### LLM API Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `insufficient_quota` | Credits exhausted | Add credits or use different model |
| `model_not_found` | Invalid model name | Check available models |
| `context_length_exceeded` | Prompt too long | Reduce prompt size |
| `rate_limit_exceeded` | Too many requests | Add delays between calls |

## Diagnostic Tools

### Health Check Script

```python
async def comprehensive_health_check():
    """Complete system health check"""
    
    print("🔍 Starting comprehensive health check...\n")
    
    results = {}
    
    # 1. Environment variables
    print("1. Checking environment variables...")
    env_vars = [
        'NOTION_TOKEN', 'TELEGRAM_TOKEN', 
        'OPENROUTER_API_KEY', 'YA_ACCESS_TOKEN'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Present ({len(value)} chars)")
            results[var] = True
        else:
            print(f"   ❌ {var}: Missing")
            results[var] = False
    
    # 2. Database connections
    print("\n2. Testing database connections...")
    db_configs = [
        ('NOTION_TASKS_DB_ID', 'tasks'),
        ('NOTION_IDEAS_DB_ID', 'ideas'),
        ('NOTION_MATERIALS_DB_ID', 'materials')
    ]
    
    for env_var, db_name in db_configs:
        db_id = os.getenv(env_var)
        if db_id:
            try:
                client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
                await client.databases.retrieve(database_id=db_id)
                print(f"   ✅ {db_name}: Connected")
                results[f"db_{db_name}"] = True
            except Exception as e:
                print(f"   ❌ {db_name}: {str(e)}")
                results[f"db_{db_name}"] = False
        else:
            print(f"   ❌ {db_name}: Database ID not set")
            results[f"db_{db_name}"] = False
    
    # 3. LLM service
    print("\n3. Testing LLM service...")
    try:
        llm_service = AdvancedLLMService()
        test_result = await llm_service._call_llm("test", "general")
        print(f"   ✅ LLM: Response received")
        results['llm'] = True
    except Exception as e:
        print(f"   ❌ LLM: {str(e)}")
        results['llm'] = False
    
    # 4. File upload service
    print("\n4. Testing file upload service...")
    try:
        uploader = YandexUploader()
        # Just test initialization
        print(f"   ✅ Yandex.Disk: Service initialized")
        results['upload'] = True
    except Exception as e:
        print(f"   ❌ Yandex.Disk: {str(e)}")
        results['upload'] = False
    
    # 5. Summary
    print("\n📊 Health Check Summary:")
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"   Passed: {passed_checks}/{total_checks}")
    print(f"   Success Rate: {passed_checks/total_checks*100:.1f}%")
    
    if passed_checks == total_checks:
        print("   🎉 All systems operational!")
    else:
        print("   ⚠️ Some issues detected. Check errors above.")
    
    return results

# Run health check
asyncio.run(comprehensive_health_check())
```

### Performance Monitor

```python
import psutil
import time

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.operations = []
    
    def log_operation(self, name, duration, memory_usage=None):
        self.operations.append({
            'name': name,
            'duration': duration,
            'memory': memory_usage or psutil.Process().memory_info().rss / 1024 / 1024,
            'timestamp': time.time()
        })
    
    def get_report(self):
        if not self.operations:
            return "No operations recorded"
        
        total_time = sum(op['duration'] for op in self.operations)
        avg_memory = sum(op['memory'] for op in self.operations) / len(self.operations)
        
        report = f"""
Performance Report:
- Total operations: {len(self.operations)}
- Total time: {total_time:.2f}s
- Average memory: {avg_memory:.1f}MB
- Slowest operation: {max(self.operations, key=lambda x: x['duration'])['name']}

Operation Details:
"""
        
        for op in sorted(self.operations, key=lambda x: x['duration'], reverse=True):
            report += f"  {op['name']}: {op['duration']:.2f}s ({op['memory']:.1f}MB)\n"
        
        return report

# Usage
monitor = PerformanceMonitor()

with Timer("Database query") as timer:
    results = await notion_service.query_database("db_id")
    monitor.log_operation("Database query", timer.duration)

print(monitor.get_report())
```

## Getting Additional Help

### 1. Enable Debug Logging

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Enable specific loggers
logging.getLogger('notion_client').setLevel(logging.DEBUG)
logging.getLogger('telegram').setLevel(logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.DEBUG)
```

### 2. Check System Resources

```python
import psutil

def check_system_resources():
    print(f"CPU usage: {psutil.cpu_percent()}%")
    print(f"Memory usage: {psutil.virtual_memory().percent}%")
    print(f"Disk usage: {psutil.disk_usage('/').percent}%")
    
    # Network connectivity
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("✅ Internet connectivity: OK")
    except:
        print("❌ Internet connectivity: Failed")
```

### 3. Common Fix Commands

```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Reset environment
python -m venv venv_new
source venv_new/bin/activate  # Linux/Mac
# or venv_new\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 4. Contact Support

When reporting issues, include:

1. **Error message** (full traceback)
2. **Environment details** (Python version, OS)
3. **Configuration** (sanitized .env file)
4. **Steps to reproduce**
5. **Health check results**
6. **Debug logs** (last 50 lines)

---

This troubleshooting guide should help you resolve most common issues. For persistent problems, consider reviewing the full API documentation and example code.