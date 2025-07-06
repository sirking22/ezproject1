"""Base repository interface."""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, TypeVar, Generic

T = TypeVar('T')


class Repository(Generic[T], ABC):
    """Base repository interface."""
    
    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """Get item by ID."""
        pass
        
    @abstractmethod
    async def list(self, params: Optional[Dict] = None) -> List[T]:
        """List items with optional filtering."""
        pass
        
    @abstractmethod
    async def create(self, item: T) -> T:
        """Create new item."""
        pass
        
    @abstractmethod
    async def update(self, id: str, item: T) -> Optional[T]:
        """Update existing item."""
        pass
        
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete item by ID."""
        pass 