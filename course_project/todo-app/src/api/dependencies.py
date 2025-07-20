"""FastAPI dependencies for dependency injection."""

from fastapi.templating import Jinja2Templates

from ..config.settings import settings
from ..core.cache import ImageCacheManager
from ..services.background import BackgroundTaskManager
from ..services.image_service import ImageService

# Global instances - because you apparently can't live without globals
_image_cache_manager: ImageCacheManager = None
_image_service: ImageService = None
_background_task_manager: BackgroundTaskManager = None
_templates: Jinja2Templates = None


def initialize_dependencies():
    """Initialize all dependencies. Call this once at startup."""
    global _image_cache_manager, _image_service, _background_task_manager, _templates

    _image_cache_manager = ImageCacheManager()
    _image_service = ImageService(_image_cache_manager)
    _background_task_manager = BackgroundTaskManager(_image_service)
    _templates = Jinja2Templates(directory=settings.template_directory)


def get_image_cache_manager_instance() -> ImageCacheManager:
    """Get the global image cache manager instance."""
    if _image_cache_manager is None:
        raise RuntimeError("Dependencies not initialized. Call initialize_dependencies() first.")
    return _image_cache_manager


def get_image_service_instance() -> ImageService:
    """Get the global image service instance."""
    if _image_service is None:
        raise RuntimeError("Dependencies not initialized. Call initialize_dependencies() first.")
    return _image_service


def get_background_task_manager_instance() -> BackgroundTaskManager:
    """Get the global background task manager instance."""
    if _background_task_manager is None:
        raise RuntimeError("Dependencies not initialized. Call initialize_dependencies() first.")
    return _background_task_manager


def get_templates_instance() -> Jinja2Templates:
    """Get the global templates instance."""
    if _templates is None:
        raise RuntimeError("Dependencies not initialized. Call initialize_dependencies() first.")
    return _templates
