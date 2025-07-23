"""Todo service for managing todo items."""

import uuid
from datetime import datetime
from typing import List

from ..models.todo import Todo, TodoStatus


class TodoService:
    """Service for managing todo items."""

    def __init__(self):
        """Initialize with some sample todos because apparently you need examples."""
        self._todos: List[Todo] = [
            Todo(
                id=str(uuid.uuid4()),
                text="Learn Kubernetes because containers are the future",
                status=TodoStatus.NOT_DONE,
                created_at=datetime.now(),
            ),
            Todo(
                id=str(uuid.uuid4()),
                text="Deploy FastAPI app to cluster",
                status=TodoStatus.DONE,
                created_at=datetime.now(),
            ),
            Todo(
                id=str(uuid.uuid4()),
                text="Write proper documentation (ha!)",
                status=TodoStatus.NOT_DONE,
                created_at=datetime.now(),
            ),
            Todo(
                id=str(uuid.uuid4()),
                text="Stop procrastinating on code reviews",
                status=TodoStatus.NOT_DONE,
                created_at=datetime.now(),
            ),
            Todo(
                id=str(uuid.uuid4()),
                text="Actually read the requirements before asking questions",
                status=TodoStatus.DONE,
                created_at=datetime.now(),
            ),
        ]

    def get_all_todos(self) -> List[Todo]:
        """Get all todos. Rocket science, I know."""
        return self._todos
