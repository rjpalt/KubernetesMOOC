"""API dependencies for dependency injection. Squirts!!"""

from fastapi import Request

from ..services.nats_service import NATSService
from ..services.todo_service import TodoService

# Global service instances
_todo_service_instance = None


def get_nats_service(request: Request) -> NATSService | None:
    """Dependency to get NATS service instance from app state."""
    import logging

    logger = logging.getLogger(__name__)

    nats_service = getattr(request.app.state, "nats_service", None)

    if nats_service:
        logger.debug(f"NATS service resolved from app.state: {type(nats_service)}")
    else:
        logger.debug("NATS service is None in app.state")

    return nats_service


def get_todo_service() -> TodoService:
    """Dependency to get todo service instance."""
    global _todo_service_instance
    if _todo_service_instance is None:
        # Create TodoService without NATS - it will be injected per request
        _todo_service_instance = TodoService()
    return _todo_service_instance
