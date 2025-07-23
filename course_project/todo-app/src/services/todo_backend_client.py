"""HTTP client for communicating with todo-backend service."""

import logging
from typing import List

import httpx
from fastapi import HTTPException

from ..config.settings import settings
from ..models.todo import Todo, TodoStatus

logger = logging.getLogger(__name__)


class TodoBackendClient:
    """HTTP client for todo-backend service."""

    def __init__(self, backend_url: str = None):
        """Initialize with backend service URL from settings or override."""
        self.backend_url = (backend_url or settings.todo_backend_url).rstrip("/")
        self.timeout = settings.todo_backend_timeout
        logger.info(f"TodoBackendClient configured for: {self.backend_url}")

    async def get_all_todos(self) -> List[Todo]:
        """Fetch all todos from backend service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.backend_url}/todos")
                response.raise_for_status()

                # Convert response to Todo objects
                todos_data = response.json()
                return [Todo.model_validate(todo_data) for todo_data in todos_data]

        except httpx.RequestError as e:
            logger.error(f"Request error when fetching todos: {e}")
            raise HTTPException(status_code=503, detail="Todo backend service unavailable")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when fetching todos: {e}")
            raise HTTPException(status_code=e.response.status_code, detail="Error fetching todos from backend")

    async def create_todo(self, text: str) -> Todo:
        """Create a new todo via backend service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.backend_url}/todos", json={"text": text})
                response.raise_for_status()

                todo_data = response.json()
                return Todo.model_validate(todo_data)

        except httpx.RequestError as e:
            logger.error(f"Request error when creating todo: {e}")
            raise HTTPException(status_code=503, detail="Todo backend service unavailable")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when creating todo: {e}")
            raise HTTPException(status_code=e.response.status_code, detail="Error creating todo in backend")

    async def update_todo(self, todo_id: str, text: str = None, status: TodoStatus = None) -> Todo:
        """Update a todo via backend service."""
        try:
            update_data = {}
            if text is not None:
                update_data["text"] = text
            if status is not None:
                update_data["status"] = status.value

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(f"{self.backend_url}/todos/{todo_id}", json=update_data)
                response.raise_for_status()

                todo_data = response.json()
                return Todo.model_validate(todo_data)

        except httpx.RequestError as e:
            logger.error(f"Request error when updating todo {todo_id}: {e}")
            raise HTTPException(status_code=503, detail="Todo backend service unavailable")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when updating todo {todo_id}: {e}")
            raise HTTPException(status_code=e.response.status_code, detail="Error updating todo in backend")

    async def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo via backend service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(f"{self.backend_url}/todos/{todo_id}")

                if response.status_code == 404:
                    return False

                response.raise_for_status()
                return True

        except httpx.RequestError as e:
            logger.error(f"Request error when deleting todo {todo_id}: {e}")
            raise HTTPException(status_code=503, detail="Todo backend service unavailable")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error when deleting todo {todo_id}: {e}")
            raise HTTPException(status_code=e.response.status_code, detail="Error deleting todo in backend")

    async def health_check(self) -> dict:
        """Check backend service health."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.backend_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Backend health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
