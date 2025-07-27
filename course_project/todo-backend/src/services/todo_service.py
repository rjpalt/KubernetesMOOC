"""Todo service for managing todo items with database backend."""

from ..models.todo import Todo, TodoCreate, TodoStatus
from ..database.operations import TodoDatabase


class TodoService:
    """Database-backed todo service."""

    def __init__(self):
        """Initialize the database backend."""
        self._db = TodoDatabase()

    async def get_all_todos(self) -> list[Todo]:
        """Get all todos."""
        return await self._db.get_all_todos()

    async def get_todo_by_id(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        return await self._db.get_todo(todo_id)

    async def create_todo(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo."""
        return await self._db.create_todo(todo_data.text)

    async def update_todo(self, todo_id: str, text: str = None, status: TodoStatus = None) -> Todo | None:
        """Update an existing todo."""
        return await self._db.update_todo(todo_id, text, status)

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
