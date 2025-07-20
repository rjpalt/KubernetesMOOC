"""Image-related API routes."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from ...models.image import FetchResult, ImageInfo
from ...services.image_service import ImageService
from ...services.todo_service import TodoService

router = APIRouter()


def get_image_service() -> ImageService:
    """Dependency to get image service instance."""
    from ...api.dependencies import get_image_service_instance

    return get_image_service_instance()


def get_templates() -> Jinja2Templates:
    """Dependency to get templates instance."""
    from ...api.dependencies import get_templates_instance

    return get_templates_instance()


def get_todo_service() -> TodoService:
    """Dependency to get todo service instance."""
    from ...api.dependencies import get_todo_service_instance

    return get_todo_service_instance()


@router.get("/")
async def read_root(
    request: Request,
    image_service: ImageService = Depends(get_image_service),
    todo_service: TodoService = Depends(get_todo_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Root endpoint - returns HTML page with current image and controls."""
    image_info = await image_service.get_image_info()
    image_status = image_service.format_image_status(image_info)
    config = image_service.get_config_for_template()
    todos = todo_service.get_all_todos()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_info": image_info.dict(),
            "image_status": image_status,
            "config": config,
            "todos": todos,
        },
    )


@router.get("/image")
async def get_current_image(image_service: ImageService = Depends(get_image_service)):
    """Serve the current cached image."""
    image_path = image_service.get_image_path()
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="No image available. Fetch one first.")

    return FileResponse(image_path, media_type="image/jpeg")


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
