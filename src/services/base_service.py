"""Base service class with common functionality."""
from typing import Dict, Any
import logging
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Base class for all services."""

    def log_operation(self, operation: str, details: Dict[str, Any]) -> None:
        """Log service operation with details."""
        logger.info(
            f"Service operation: {operation}",
            extra={
                "operation": operation,
                "details": details,
                "service": self.__class__.__name__
            }
        )

    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle and log service error."""
        error_details = {
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "context": context,
            "service": self.__class__.__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.error(
            f"Service error: {error_details}",
            exc_info=True
        )
        raise error  # Re-raise for higher-level handling

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize service resources."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        pass 