"""Todo service for managing todo items in memory."""

from ..models.todo import Todo, TodoCreate, TodoStatus


class TodoService:
    """In-memory todo service."""

    def __init__(self):
        """Initialize with some sample todos for demo purposes."""
        self._todos: list[Todo] = [
            Todo.create_new("Learn Kubernetes service discovery"),
            Todo.create_new("Implement REST API endpoints"),
            Todo.create_new("Test inter-service communication"),
        ]
        # Mark first todo as done for demo
        self._todos[1].mark_done()

    def get_all_todos(self) -> list[Todo]:
        """Get all todos."""
        return self._todos.copy()

    def get_todo_by_id(self, todo_id: str) -> Todo | None:
        """Get a todo by ID."""
        return next((todo for todo in self._todos if todo.id == todo_id), None)

    def create_todo(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo."""
        new_todo = Todo.create_new(todo_data.text)
        self._todos.append(new_todo)
        return new_todo

    def update_todo(self, todo_id: str, text: str = None, status: TodoStatus = None) -> Todo | None:
        """Update an existing todo."""
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            return None

        if text is not None:
            todo.update_text(text)

        if status is not None:
            if status == TodoStatus.DONE:
                todo.mark_done()
            else:
                todo.mark_not_done()

        return todo

    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo by ID."""
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            return False

        self._todos.remove(todo)
        return True

    def get_todo_count(self) -> int:
        """Get total number of todos."""
        return len(self._todos)
