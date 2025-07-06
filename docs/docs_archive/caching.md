# Caching System Documentation

## Overview

The caching system provides an in-memory caching mechanism with TTL (Time To Live) support for optimizing database operations and reducing API calls to external services like Notion.

## Components

### Cache Class

The base `Cache` class provides core caching functionality:

```python
from src.utils.cache import Cache

# Create cache instance with default TTL of 5 minutes
cache = Cache(default_ttl=300)

# Basic operations
cache.set("key", "value")  # Set with default TTL
cache.set("key", "value", ttl=60)  # Set with custom TTL
value = cache.get("key")  # Get value
cache.delete("key")  # Delete value
cache.clear()  # Clear all entries

# Get cache statistics
stats = cache.stats  # Returns hits, misses, size, hit rate
```

### Cached Decorator

The `@cached` decorator provides function-level caching:

```python
from src.utils.cache import cached

@cached(ttl=300)
async def expensive_operation(arg1, arg2):
    # ... some expensive computation
    return result

# First call executes the function
result1 = await expensive_operation(1, 2)

# Second call returns cached result
result2 = await expensive_operation(1, 2)

# Access cache statistics
stats = expensive_operation.cache.stats
```

### Cached Repositories

The cached repository implementations provide transparent caching for Notion operations:

```python
from src.repositories.cached_notion import CachedNotionTaskRepository

# Create cached repository
repo = CachedNotionTaskRepository(notion_repo, cache_ttl=300)

# Operations are automatically cached
task = await repo.get("task_id")  # First call hits Notion API
same_task = await repo.get("task_id")  # Second call uses cache

# Cache is automatically invalidated on updates
await repo.update("task_id", updated_task)  # Invalidates cache
```

## Best Practices

1. **Choose Appropriate TTL**
   - Short TTL (seconds) for frequently changing data
   - Longer TTL (minutes) for relatively static data
   - Consider data consistency requirements

2. **Monitor Cache Performance**
   - Use `cache.stats` to monitor hit rates
   - Adjust TTL based on hit/miss ratios
   - Clear cache if memory usage is high

3. **Cache Invalidation**
   - Cached repositories automatically handle invalidation
   - Manually invalidate cache when data changes externally
   - Use `cache.clear()` for full cache reset

4. **Error Handling**
   - Cache operations never throw exceptions
   - Failed cache operations fall back to source data
   - Log cache errors for monitoring

## Example Usage

```python
from src.repositories.cached_notion import CachedNotionTaskRepository
from src.models.base import TaskDTO

# Create repository
repo = CachedNotionTaskRepository(notion_repo, cache_ttl=300)

# Create task (bypasses cache)
task = TaskDTO(id="1", title="Test", status="TODO")
created = await repo.create(task)

# Get task (uses cache)
cached_task = await repo.get("1")

# Update task (invalidates cache)
task.status = "DONE"
updated = await repo.update("1", task)

# Delete task (invalidates cache)
deleted = await repo.delete("1")

# Check cache performance
print(repo.stats)
```

## Implementation Details

The caching system uses Python's built-in dictionary for storage and includes:

- Thread-safe operations
- Automatic TTL expiration
- Cache statistics tracking
- Memory usage optimization
- Automatic cache invalidation
- Type hints for better IDE support

## Future Improvements

1. Add distributed caching support (Redis/Memcached)
2. Implement cache size limits
3. Add cache preloading capabilities
4. Support for cache tags/groups
5. Add cache compression for large objects 