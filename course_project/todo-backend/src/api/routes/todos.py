"""Todo CRUD endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ...api.dependencies import get_todo_service
from ...models.todo import Todo, TodoCreate, TodoUpdate
from ...services.todo_service import TodoService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/todos", response_model=list[Todo])
async def get_todos(todo_service: TodoService = Depends(get_todo_service)):
    """Get all todos."""
    logger.info("Fetching all todos")
    todos = await todo_service.get_all_todos()
    logger.info(f"Returning {len(todos)} todos")
    return todos


@router.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(todo_data: TodoCreate, todo_service: TodoService = Depends(get_todo_service)):
    """Create a new todo."""
    logger.info(f"Creating new todo: {todo_data.text}")
    new_todo = await todo_service.create_todo(todo_data)
    logger.info(f"Created todo with ID: {new_todo.id}")
    return new_todo


@router.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: str, todo_service: TodoService = Depends(get_todo_service)):
    """Get a specific todo by ID."""
    logger.info(f"Fetching todo with ID: {todo_id}")
    todo = await todo_service.get_todo_by_id(todo_id)
    if not todo:
        logger.warning(f"Todo not found: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: str, todo_update: TodoUpdate, todo_service: TodoService = Depends(get_todo_service)):
    """Update an existing todo."""
    logger.info(f"Updating todo: {todo_id}")
    updated_todo = await todo_service.update_todo(todo_id, text=todo_update.text, status=todo_update.status)
    if not updated_todo:
        logger.warning(f"Todo not found for update: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info(f"Updated todo: {todo_id}")
    return updated_todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str, todo_service: TodoService = Depends(get_todo_service)):
    """Delete a todo."""
    logger.info(f"Deleting todo: {todo_id}")
    deleted = await todo_service.delete_todo(todo_id)
    if not deleted:
        logger.warning(f"Todo not found for deletion: {todo_id}")
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info(f"Deleted todo: {todo_id}")
