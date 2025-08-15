"""API dependencies for dependency injection. Yeah!"""

from ..services.todo_service import TodoService

# Global service instances
_todo_service_instance = None


def get_todo_service() -> TodoService:
    """Dependency to get todo service instance."""
    global _todo_service_instance
    if _todo_service_instance is None:
        _todo_service_instance = TodoService()
    return _todo_service_instance


def initialize_dependencies():
    """Initialize all dependencies."""
    # Initialize any startup dependencies here
    pass
