"""Todo service for managing todo items with database backend."""

from ..database.operations import TodoDatabase
from ..models.todo import Todo, TodoCreate, TodoStatus


class TodoService:
    """Database-backed todo service."""

    def __init__(self, nats_service=None):
        """Initialize the database backend."""
        self._db = TodoDatabase()
        self.nats_service = nats_service

    async def get_all_todos(self) -> list[Todo]:
        """Get all todos."""
        return await self._db.get_all_todos()

    async def get_todo_by_id(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        return await self._db.get_todo(todo_id)

    async def create_todo(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo."""
        # Create todo in database first
        todo = await self._db.create_todo(todo_data.text)
        
        # Publish NATS event after successful database operation
        if self.nats_service:
            await self.nats_service.publish_todo_event(
                todo_data={
                    "id": todo.id,
                    "text": todo.text,
                    "status": todo.status,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat() if todo.updated_at else todo.created_at.isoformat(),
                },
                action="created"
            )
        
        return todo

    async def update_todo(self, todo_id: str, text: str | None = None, status: TodoStatus | None = None) -> Todo | None:
        """Update an existing todo."""
        # Update todo in database first
        todo = await self._db.update_todo(todo_id, text, status)
        
        # Publish NATS event after successful database operation
        if todo and self.nats_service:
            await self.nats_service.publish_todo_event(
                todo_data={
                    "id": todo.id,
                    "text": todo.text,
                    "status": todo.status,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat() if todo.updated_at else todo.created_at.isoformat(),
                },
                action="updated"
            )
        
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
