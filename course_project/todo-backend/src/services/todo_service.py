"""Todo service for managing todo items with database backend."""

from ..database.operations import TodoDatabase
from ..models.todo import Todo, TodoCreate, TodoStatus
from .nats_client import get_nats_client


class TodoService:
    """Database-backed todo service."""

    def __init__(self):
        """Initialize the database backend and NATS client."""
        self._db = TodoDatabase()
        self._nats_client = get_nats_client()

    async def get_all_todos(self) -> list[Todo]:
        """Get all todos."""
        return await self._db.get_all_todos()

    async def get_todo_by_id(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        return await self._db.get_todo(todo_id)

    async def create_todo(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo and publish NATS event."""
        todo = await self._db.create_todo(todo_data.text)
        
        # Publish NATS event (fire-and-forget, non-blocking)
        await self._publish_todo_event("created", todo)
        
        return todo

    async def update_todo(self, todo_id: str, text: str | None = None, status: TodoStatus | None = None) -> Todo | None:
        """Update an existing todo and publish NATS event."""
        todo = await self._db.update_todo(todo_id, text, status)
        
        if todo:
            # Publish NATS event (fire-and-forget, non-blocking)
            await self._publish_todo_event("updated", todo)
        
        return todo

    async def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo by ID."""
        return await self._db.delete_todo(todo_id)

    async def get_todo_count(self) -> int:
        """Get total number of todos."""
        return await self._db.count_todos()

    async def initialize_with_sample_data(self) -> None:
        """Initialize database with sample todos if empty."""
        count = await self.get_todo_count()
        if count == 0:
            # Create sample todos
            todo1 = await self.create_todo(TodoCreate(text="Learn Kubernetes service discovery"))
            await self.create_todo(TodoCreate(text="Implement REST API endpoints"))
            await self.create_todo(TodoCreate(text="Test inter-service communication"))

            # Mark first todo as done for demo
            await self.update_todo(todo1.id, status=TodoStatus.DONE)

    async def _publish_todo_event(self, event_type: str, todo: Todo) -> None:
        """Publish a todo event to NATS (non-blocking, fire-and-forget)."""
        try:
            # Convert todo to dict for JSON serialization
            todo_data = {
                "id": todo.id,
                "text": todo.text,
                "status": todo.status.value,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
            }
            
            # Fire-and-forget publishing (doesn't block todo operations)
            await self._nats_client.publish_todo_event(event_type, todo_data)
            
        except Exception:
            # Silently ignore NATS publishing errors to ensure todo operations continue
            pass
