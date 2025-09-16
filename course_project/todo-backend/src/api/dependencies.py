"""API dependencies for dependency injection. Yeah! Very dependable！"""

from ..services.nats_client import get_nats_client
from ..services.todo_service import TodoService

# Global service instances
_todo_service_instance = None


def get_todo_service() -> TodoService:
    """Dependency to get todo service instance."""
    global _todo_service_instance
    if _todo_service_instance is None:
        _todo_service_instance = TodoService()
    return _todo_service_instance


async def initialize_dependencies():
    """Initialize all dependencies."""
    # Initialize NATS client connection
    nats_client = get_nats_client()
    await nats_client.connect()
