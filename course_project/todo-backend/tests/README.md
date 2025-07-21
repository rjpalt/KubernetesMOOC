# Todo Backend - Testing Guide

This guide explains how to run tests for the todo-backend microservice.

## Test Structure

The backend tests are organized by scope and purpose:

```
tests/
├── unit/                     # Fast, isolated tests
│   ├── test_todo_service.py  # Business logic tests
│   └── test_models.py        # Data model tests (TODO)
├── integration/              # API endpoint tests  
│   ├── test_todo_endpoints.py # REST API tests
│   └── test_health_checks.py  # Health endpoint tests (TODO)
├── fixtures/                 # Shared test data
│   └── todo_fixtures.py      # Todo test fixtures
└── conftest.py              # Test configuration
```

## Running Tests

### Prerequisites
```bash
cd course_project/todo-backend
uv sync --group dev  # Install test dependencies
```

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only (fast)
uv run pytest tests/unit/ -v

# Integration tests only  
uv run pytest tests/integration/ -v

# Specific test file
uv run pytest tests/unit/test_todo_service.py -v
```

### Run with Coverage
```bash
uv run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Test Types Explained

### Unit Tests (`tests/unit/`)
- **Purpose**: Test business logic in isolation
- **Speed**: Very fast (< 1 second)
- **Dependencies**: None (no HTTP, no external services)
- **Example**: Testing TodoService.create_todo() method

```python
def test_create_todo_adds_new_todo():
    service = TodoService()
    todo_data = TodoCreate(text="Test todo")
    new_todo = service.create_todo(todo_data)
    assert new_todo.text == "Test todo"
```

### Integration Tests (`tests/integration/`)
- **Purpose**: Test HTTP API endpoints
- **Speed**: Fast (< 5 seconds)
- **Dependencies**: FastAPI test client
- **Example**: Testing POST /todos endpoint

```python
def test_create_todo_returns_created_todo(test_client):
    response = test_client.post("/todos", json={"text": "API test"})
    assert response.status_code == 201
```

## Microservice Testing Principles

### What Backend Tests Focus On
✅ **Business Logic**: Todo CRUD operations  
✅ **API Contracts**: HTTP endpoints return correct formats  
✅ **Data Validation**: Input validation and error handling  
✅ **Service Independence**: Backend works without frontend  

### What Backend Tests DON'T Test
❌ **Frontend Concerns**: How todos are displayed  
❌ **Inter-Service Communication**: HTTP calls to other services  
❌ **Kubernetes Deployment**: Pod/service configuration  

### Schema Consistency
The backend tests use fixtures that match the exact format the backend returns:

```python
# In conftest.py - matches real backend response
@pytest.fixture
def sample_todo_data():
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "text": "Learn Kubernetes testing patterns", 
        "status": "not_done",
        "created_at": "2025-07-21T10:00:00Z"
    }
```

This ensures:
- Frontend mocks use the same format
- API contracts remain consistent
- Changes to backend models are caught in tests

## Debugging Tests

### Verbose Output
```bash
uv run pytest tests/ -v -s  # Show print statements
```

### Run Single Test
```bash
uv run pytest tests/unit/test_todo_service.py::TestTodoService::test_create_todo_adds_new_todo -v
```

### Debug Test Failures
```bash
uv run pytest tests/ --pdb  # Drop into debugger on failure
```

## Development Workflow

### Before Making Changes
```bash
uv run pytest tests/  # Ensure all tests pass
```

### After Making Changes
```bash
# Run affected tests
uv run pytest tests/unit/test_todo_service.py  # If you changed TodoService
uv run pytest tests/integration/test_todo_endpoints.py  # If you changed API routes

# Run full suite before committing
uv run pytest tests/ --cov=src
```

### Adding New Features
1. **Write unit tests first** for business logic
2. **Write integration tests** for new API endpoints  
3. **Update fixtures** if data formats change
4. **Run all tests** to ensure no regressions

## CI/CD Integration

Tests run automatically on:
- Pull requests to main branch
- Changes to `course_project/todo-backend/**`

Local CI testing:
```bash
# Test what CI will run
act --job test-backend  # Requires 'act' to be installed
```

## Common Issues

### Import Errors
```bash
# If you see "ModuleNotFoundError: No module named 'src'"
cd course_project/todo-backend  # Run from correct directory
```

### Async Test Issues  
```python
# Tests with async endpoints should work automatically
# Thanks to pytest-asyncio configuration in pyproject.toml
```

### Test Isolation
Each test runs with a fresh TodoService instance, so tests don't interfere with each other.

## Next Steps

- [ ] Add model validation tests (`test_models.py`)
- [ ] Add health endpoint tests (`test_health_checks.py`) 
- [ ] Add settings configuration tests (`test_settings.py`)
- [ ] Add contract tests with frontend
- [ ] Add performance/load testing
