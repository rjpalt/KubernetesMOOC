"""API dependencies for dependency injection. Yeah! Very dependable！"""

from ..services.nats_service import NATSService
from ..services.todo_service import TodoService

# Global service instances
_todo_service_instance = None


def get_todo_service() -> TodoService:
    """Dependency to get todo service instance."""
    global _todo_service_instance
    if _todo_service_instance is None:
        # Get NATS service instance
        nats_service = get_nats_service()
        _todo_service_instance = TodoService(nats_service=nats_service)
    return _todo_service_instance


def get_nats_service() -> NATSService | None:
    """Dependency to get NATS service instance."""
    # Import here to avoid circular dependency
    from ..main import nats_service_instance
    return nats_service_instance


def initialize_dependencies():
    """Initialize all dependencies."""
    # Initialize todo service
    get_todo_service()
    # NATS service will be initialized in main.py lifespan handler
