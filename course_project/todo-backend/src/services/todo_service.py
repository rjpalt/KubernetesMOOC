"""Todo service for managing todo items with database backend."""

from ..database.operations import TodoDatabase
from ..models.todo import Todo, TodoCreate, TodoStatus


class TodoService:
    """Database-backed todo service."""

    def __init__(self):
        """Initialize the database backend."""
        self._db = TodoDatabase()
        # Remove nats_service from constructor - injected per request

    async def get_all_todos(self) -> list[Todo]:
        """Get all todos."""
        return await self._db.get_all_todos()

    async def get_todo_by_id(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        return await self._db.get_todo(todo_id)

    async def create_todo(self, todo_data: TodoCreate, nats_service=None) -> Todo:
        """Create a new todo."""
        import logging

        logger = logging.getLogger(__name__)

        logger.info(f"Creating todo: {todo_data.text}")

        # Create todo in database first
        todo = await self._db.create_todo(todo_data.text)
        logger.info(f"Todo created in database with ID: {todo.id}")

        # Publish NATS event if service is available
        if nats_service:
            logger.info(f"NATS service available: {type(nats_service)}")
            try:
                todo_data_dict = {
                    "id": todo.id,
                    "text": todo.text,
                    "status": todo.status,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat() if todo.updated_at else todo.created_at.isoformat(),
                }

                await nats_service.publish_todo_event(
                    todo_data=todo_data_dict,
                    action="created",
                )
                logger.info(f"✅ Published NATS event for todo creation: {todo.id}")
            except Exception as e:
                logger.error(f"❌ Failed to publish NATS event: {e}")
        else:
            logger.info("No NATS service provided, skipping event publishing")

        return todo

    async def update_todo(
        self, todo_id: str, text: str | None = None, status: TodoStatus | None = None, nats_service=None
    ) -> Todo | None:
        """Update an existing todo."""
        import logging

        logger = logging.getLogger(__name__)

        logger.info(f"Updating todo: {todo_id}")

        # Update todo in database first
        todo = await self._db.update_todo(todo_id, text, status)

        if todo and nats_service:
            logger.info(f"NATS service available for update: {type(nats_service)}")
            try:
                todo_data_dict = {
                    "id": todo.id,
                    "text": todo.text,
                    "status": todo.status,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat() if todo.updated_at else todo.created_at.isoformat(),
                }

                await nats_service.publish_todo_event(
                    todo_data=todo_data_dict,
                    action="updated",
                )
                logger.info(f"✅ Published NATS event for todo update: {todo.id}")
            except Exception as e:
                logger.error(f"❌ Failed to publish NATS event: {e}")
        elif todo and not nats_service:
            logger.info("No NATS service provided for update, skipping event publishing")

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
            # Create sample todos (without NATS during initialization)
            todo1 = await self.create_todo(TodoCreate(text="Learn Kubernetes service discovery"), nats_service=None)
            await self.create_todo(TodoCreate(text="Implement REST API endpoints"), nats_service=None)
            await self.create_todo(TodoCreate(text="Test inter-service communication"), nats_service=None)

            # Mark first todo as done for demo
            await self.update_todo(todo1.id, status=TodoStatus.DONE, nats_service=None)
