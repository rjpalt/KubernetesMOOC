"""Image-related API routes."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from ...config.settings import settings
from ...models.image import FetchResult, ImageInfo
from ...services.image_service import ImageService
from ...services.todo_backend_client import TodoBackendClient

logger = logging.getLogger(__name__)
router = APIRouter()


def get_image_service() -> ImageService:
    """Dependency to get image service instance."""
    from ...api.dependencies import get_image_service_instance

    return get_image_service_instance()


def get_templates() -> Jinja2Templates:
    """Dependency to get templates instance."""
    from ...api.dependencies import get_templates_instance

    return get_templates_instance()


def get_todo_backend_client() -> TodoBackendClient:
    """Dependency to get todo backend client."""
    return TodoBackendClient()


@router.get("/")
async def read_root(
    request: Request,
    image_service: ImageService = Depends(get_image_service),
    backend_client: TodoBackendClient = Depends(get_todo_backend_client),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Root endpoint - returns HTML page with current image and controls."""
    image_info = await image_service.get_image_info()
    image_status = image_service.format_image_status(image_info)
    config = image_service.get_config_for_template()

    # Fetch todos from backend service
    try:
        todos = await backend_client.get_all_todos()
    except Exception as e:
        # If backend is unavailable, show empty list with error
        todos = []
        logger.warning(f"Could not fetch todos from backend: {e}")

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "image_info": image_info.model_dump(),
            "image_status": image_status,
            "config": config,
            "todos": todos,
            "base_path": settings.api_base_path,
        },
    )


@router.get("/image")
async def get_current_image(image_service: ImageService = Depends(get_image_service)):
    """Serve the current cached image."""
    image_path = image_service.get_image_path()
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="No image available. Fetch one first.")

    return FileResponse(
        image_path,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"},
    )


@router.get("/image/info", response_model=ImageInfo)
async def get_image_info(image_service: ImageService = Depends(get_image_service)):
    """Get detailed information about the current cached image."""
    return await image_service.get_image_info()


@router.post("/fetch-image", response_model=FetchResult)
async def fetch_new_image_endpoint(
    force: bool = False,
    background_tasks: BackgroundTasks = None,
    image_service: ImageService = Depends(get_image_service),
):
    """Manually trigger a new image fetch."""
    return await image_service.fetch_new_image(force=force)
