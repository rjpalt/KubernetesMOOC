"""Database operations for todos. Compliant with PSQL."""

from sqlalchemy import delete, func, select, update

from ..models.todo import Todo, TodoStatus
from .connection import db_manager
from .models import TodoDB


class TodoDatabase:
    """Database operations for Todo entities.
    
    All operations are async and handle database sessions with proper rollback on errors.
    Uses SQLAlchemy async sessions for PostgreSQL compatibility.
    """

    async def create_todo(self, text: str) -> Todo:
        """Create a new todo item."""
        session = db_manager.get_session()
        async with session as s:
            try:
                todo_db = TodoDB(text=text, completed=False)
                s.add(todo_db)
                await s.commit()
                await s.refresh(todo_db)

                # Convert database model to Pydantic model
                return self._db_to_pydantic(todo_db)
            except Exception:
                await s.rollback()
                raise

    async def get_todo(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        try:
            todo_id_int = int(todo_id)
        except ValueError:
            return None

        session = db_manager.get_session()
        async with session as s:
            try:
                result = await s.execute(select(TodoDB).where(TodoDB.id == todo_id_int))
                todo_db = result.scalar_one_or_none()

                if todo_db:
                    return self._db_to_pydantic(todo_db)
                return None
            except Exception:
                await s.rollback()
                raise

    async def get_all_todos(self) -> list[Todo]:
        """Get all todos ordered by creation date."""
        session = db_manager.get_session()
        async with session as s:
            try:
                result = await s.execute(select(TodoDB).order_by(TodoDB.created_at.desc()))
                todo_dbs = list(result.scalars().all())

                return [self._db_to_pydantic(todo_db) for todo_db in todo_dbs]
            except Exception:
                await s.rollback()
                raise

    async def update_todo(self, todo_id: str, text: str | None = None, status: TodoStatus | None = None) -> Todo | None:
        """Update a todo item."""
        try:
            todo_id_int = int(todo_id)
        except ValueError:
            return None

        session = db_manager.get_session()
        async with session as s:
            try:
                # Build update values
                update_values = {}
                if text is not None:
                    update_values["text"] = text
                if status is not None:
                    update_values["completed"] = status == TodoStatus.DONE

                if not update_values:
                    return await self.get_todo(todo_id)

                # Perform update
                result = await s.execute(update(TodoDB).where(TodoDB.id == todo_id_int).values(**update_values))
                await s.commit()

                if result.rowcount == 0:
                    return None

                # Return updated todo
                return await self.get_todo(todo_id)
            except Exception:
                await s.rollback()
                raise

    async def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo item. Returns True if deleted, False if not found."""
        try:
            todo_id_int = int(todo_id)
        except ValueError:
            return False

        session = db_manager.get_session()
        async with session as s:
            try:
                result = await s.execute(delete(TodoDB).where(TodoDB.id == todo_id_int))
                await s.commit()
                return result.rowcount > 0
            except Exception:
                await s.rollback()
                raise

    async def count_todos(self) -> int:
        """Count total number of todos."""
        session = db_manager.get_session()
        async with session as s:
            try:
                result = await s.execute(select(func.count(TodoDB.id)))
                return result.scalar() or 0
            except Exception:
                await s.rollback()
                raise

    def _db_to_pydantic(self, todo_db: TodoDB) -> Todo:
        """Convert database model to Pydantic model."""
        status = TodoStatus.DONE if todo_db.completed else TodoStatus.NOT_DONE

        return Todo(
            id=str(todo_db.id),
            text=todo_db.text,
            status=status,
            created_at=todo_db.created_at,
            updated_at=todo_db.updated_at,
        )
