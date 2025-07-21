# Todo Application - Microservices Project

Two-service todo application: **todo-backend** (REST API) and **todo-app** (Frontend with image caching).

## Architecture

- **todo-backend** (Port 8001): FastAPI REST API for todo CRUD operations
- **todo-app** (Port 8000): FastAPI frontend with HTMX UI, communicates with backend via HTTP

## Quick Start

```bash
# Start both services with one command
./start-services.sh

# Or manually:
cd todo-backend && uv sync && uv run python -m src.main &
cd ../todo-app && uv sync && uv run python -m src.main &
```

Access:
- Frontend: http://localhost:8000
- Backend API docs: http://localhost:8001/docs

## Testing

### Run All Tests
```bash
# All tests with one command
./test-all.sh

# Individual services
./test-be.sh     # Backend tests (27 tests)
./test-fe.sh     # Frontend tests

# Or manually:
cd todo-backend && uv run pytest tests/ -v
cd todo-app && uv run pytest tests/ -v
```

### Test Coverage
- **Backend**: Unit tests, integration tests, API validation
- **Frontend**: Contract tests, service integration, UI components
- **Philosophy**: Each service tested independently for microservice isolation

## CI/CD Pipeline

Sequential testing strategy in `.github/workflows/test.yml`:
1. **Backend Tests**: API contracts and business logic
2. **Frontend Tests**: Service integration with mocked backend
3. **Integration Tests**: Docker containers with real service communication

Local testing with Act: `act --job test-backend` or `act --job test-frontend`

## Features

- Todo CRUD operations with 140-character validation
- Automatic image fetching from picsum.photos
- Health check endpoints for monitoring
- OpenAPI documentation for both services
