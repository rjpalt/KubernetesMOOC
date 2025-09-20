"""Todo service for managing todo items with database backend."""

from ..database.operations import TodoDatabase
from ..models.todo import Todo, TodoCreate, TodoStatus


class TodoService:
    """Database-backed todo service."""

    def __init__(self, nats_service=None):
        """Initialize the database backend."""
        self._db = TodoDatabase()
        self.nats_service = nats_service

    def _get_current_nats_service(self):
        """Get the current NATS service instance - support dynamic resolution."""
        if self.nats_service:
            return self.nats_service

        # Try to get current NATS service instance from dependencies
        try:
            from ..api.dependencies import get_nats_service

            return get_nats_service()
        except ImportError:
            return None

    async def get_all_todos(self) -> list[Todo]:
        """Get all todos."""
        return await self._db.get_all_todos()

    async def get_todo_by_id(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        return await self._db.get_todo(todo_id)

    async def create_todo(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo."""
        import logging

        logger = logging.getLogger(__name__)

        # Create todo in database first
        todo = await self._db.create_todo(todo_data.text)
        logger.info(f"Created todo with ID: {todo.id}")

        # Attempt NATS publishing with dynamic service resolution
        current_nats = self._get_current_nats_service()
        if current_nats:
            try:
                await current_nats.publish_todo_event(
                    todo_data={
                        "id": todo.id,
                        "text": todo.text,
                        "status": todo.status,
                        "created_at": todo.created_at.isoformat(),
                        "updated_at": todo.updated_at.isoformat() if todo.updated_at else todo.created_at.isoformat(),
                    },
                    action="created",
                )
                logger.info(f"Successfully published NATS event for todo creation: {todo.id}")
            except Exception as e:
                # Log the error but don't fail the todo creation
                logger.warning(f"Failed to publish NATS event for todo creation {todo.id}: {e}")
        else:
            logger.debug("NATS service not available, skipping event publishing")

        return todo

    async def update_todo(self, todo_id: str, text: str | None = None, status: TodoStatus | None = None) -> Todo | None:
        """Update an existing todo."""
        import logging

        logger = logging.getLogger(__name__)

        # Update todo in database first
        todo = await self._db.update_todo(todo_id, text, status)

        if todo:
            logger.info(f"Updated todo with ID: {todo.id}")

            # Attempt NATS publishing with dynamic service resolution
            current_nats = self._get_current_nats_service()
            if current_nats:
                try:
                    await current_nats.publish_todo_event(
                        todo_data={
                            "id": todo.id,
                            "text": todo.text,
                            "status": todo.status,
                            "created_at": todo.created_at.isoformat(),
                            "updated_at": todo.updated_at.isoformat()
                            if todo.updated_at
                            else todo.created_at.isoformat(),
                        },
                        action="updated",
                    )
                    logger.info(f"Successfully published NATS event for todo update: {todo.id}")
                except Exception as e:
                    # Log the error but don't fail the todo update
                    logger.warning(f"Failed to publish NATS event for todo update {todo.id}: {e}")
            else:
                logger.debug("NATS service not available, skipping event publishing")

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
