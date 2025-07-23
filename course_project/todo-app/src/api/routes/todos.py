"""Todo-related API routes for frontend app."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ...models.todo import TodoStatus
from ...services.todo_backend_client import TodoBackendClient

router = APIRouter()


def get_todo_backend_client() -> TodoBackendClient:
    """Dependency to get todo backend client."""
    return TodoBackendClient()


def get_templates() -> Jinja2Templates:
    """Dependency to get templates instance."""
    from ...api.dependencies import get_templates_instance

    return get_templates_instance()


@router.get("/todos", response_class=HTMLResponse)
async def get_todos_html(
    request: Request,
    backend_client: TodoBackendClient = Depends(get_todo_backend_client),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Get todos as HTML fragment for HTMX."""
    try:
        todos = await backend_client.get_all_todos()
        return templates.TemplateResponse(request, "components/todo_list.html", {"todos": todos})
    except HTTPException as e:
        return templates.TemplateResponse(request, "components/error.html", {"error": e.detail})


@router.post("/todos", response_class=HTMLResponse)
async def create_todo_html(
    request: Request,
    text: str = Form(..., max_length=140),
    backend_client: TodoBackendClient = Depends(get_todo_backend_client),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Create a new todo and return HTML fragment for HTMX."""
    try:
        # Validate input
        if not text.strip():
            raise HTTPException(status_code=400, detail="Todo text cannot be empty")

        # Create todo via backend
        new_todo = await backend_client.create_todo(text.strip())

        # Return the new todo as HTML fragment
        return templates.TemplateResponse(request, "components/todo_item.html", {"todo": new_todo})
    except HTTPException as e:
        return templates.TemplateResponse(request, "components/error.html", {"error": e.detail})


@router.put("/todos/{todo_id}/toggle", response_class=HTMLResponse)
async def toggle_todo_html(
    todo_id: str,
    request: Request,
    backend_client: TodoBackendClient = Depends(get_todo_backend_client),
    templates: Jinja2Templates = Depends(get_templates),
):
    """Toggle todo status and return updated HTML fragment for HTMX."""
    try:
        # First get the current todo to determine new status
        todos = await backend_client.get_all_todos()
        current_todo = next((t for t in todos if t.id == todo_id), None)

        if not current_todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Toggle status
        new_status = TodoStatus.DONE if current_todo.status == TodoStatus.NOT_DONE else TodoStatus.NOT_DONE
        updated_todo = await backend_client.update_todo(todo_id, status=new_status)

        # Return updated todo as HTML fragment
        return templates.TemplateResponse(request, "components/todo_item.html", {"todo": updated_todo})
    except HTTPException as e:
        return templates.TemplateResponse(request, "components/error.html", {"error": e.detail})


@router.delete("/todos/{todo_id}", response_class=HTMLResponse)
async def delete_todo_html(
    todo_id: str,
    request: Request,
    backend_client: TodoBackendClient = Depends(get_todo_backend_client),
):
    """Delete todo and return empty response for HTMX."""
    try:
        deleted = await backend_client.delete_todo(todo_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Return empty response - HTMX will remove the element
        return HTMLResponse(content="", status_code=200)

    except HTTPException as e:
        # Return error message
        return HTMLResponse(content=f'<div class="error">Error: {e.detail}</div>', status_code=e.status_code)
