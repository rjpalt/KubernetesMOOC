"""API dependencies for dependency injection. Yeah! Very dependable！"""

from ..services.nats_service import NATSService
from ..services.todo_service import TodoService

# Global service instances
_todo_service_instance = None


def get_todo_service() -> TodoService:
    """Dependency to get todo service instance."""
    global _todo_service_instance
    if _todo_service_instance is None:
        # Create TodoService without NATS service initially
        # NATS service will be resolved dynamically at request time
        _todo_service_instance = TodoService(nats_service=None)
    return _todo_service_instance


def get_nats_service() -> NATSService | None:
    """Dependency to get NATS service instance - resolve at request time."""
    # Import here and check if service is available at request time
    try:
        import src.main as main_module

        return getattr(main_module, "nats_service_instance", None)
    except (ImportError, AttributeError):
        return None


def initialize_dependencies():
    """Initialize all dependencies - now simplified since NATS is resolved lazily."""
    # TodoService will be created on first request with lazy NATS resolution
    # This prevents the race condition during app startup
    pass
