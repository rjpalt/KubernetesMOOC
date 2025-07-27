# Todo Backend API

Backend service for the todo application. Provides REST API endpoints for managing todos with PostgreSQL database persistence.

## Features

- **PostgreSQL Database**: Async SQLAlchemy with connection pooling
- **Pydantic Settings**: Environment-based configuration with validation
- **Code Quality**: Black formatting and Flake8 linting
- **REST API**: FastAPI with automatic OpenAPI documentation
- **CORS Support**: Configurable cross-origin resource sharing
- **Health Checks**: Built-in health endpoint for monitoring
- **Database Migration**: Automatic table creation and sample data

## Endpoints

- `GET /health` - Health check with todo count
- `GET /todos` - List all todos (JSON)
- `POST /todos` - Create new todo (JSON)
- `GET /todos/{id}` - Get specific todo (JSON)
- `PUT /todos/{id}` - Update todo (JSON)  
- `DELETE /todos/{id}` - Delete todo

## Database Setup

### Local Development

1. **Start PostgreSQL containers:**
   ```bash
   ./start-db.sh
   ```

2. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

4. **Run the application:**
   ```bash
   uv run python -m src.main
   ```

### Database Configuration

Environment variables for database connection:

- `DATABASE_URL`: Full PostgreSQL connection string (recommended)
  - Development: `postgresql+asyncpg://todouser:todopass@localhost:5432/todoapp`
  - Test: `postgresql+asyncpg://todouser:todopass@localhost:5433/todoapp_test`

**Or use individual components:**
- `POSTGRES_HOST`: Database host (default: localhost)
- `POSTGRES_PORT`: Database port (default: 5432)
- `POSTGRES_DB`: Database name (default: todoapp)
- `POSTGRES_USER`: Database user (default: todouser)
- `POSTGRES_PASSWORD`: Database password (default: todopass)

### Testing

1. **Start test database:**
   ```bash
   ./start-db.sh  # Starts both dev and test databases
   ```

2. **Run tests:**
   ```bash
   uv run pytest
   ```

The test database (`todoapp_test` on port 5433) is automatically cleaned between tests.

## Testing Strategy

### Overview
Production-ready test suite with **39 tests** covering unit and integration layers. Designed for Kubernetes CI/CD pipelines with zero failing tests and container-based database lifecycle management.

### Test Structure
```
tests/
├── unit/                      # 32 tests - Core business logic
│   ├── test_models.py         # 20 tests - Pydantic models & validation
│   └── test_todo_service.py   # 12 tests - Service layer with async DB
├── integration/               # 7 tests - API contract validation
│   └── test_todo_api_structure.py
└── conftest.py               # Test fixtures & DB lifecycle
```

### What's Tested

**Unit Tests (32/39)**
- **Model Layer**: Pydantic schema validation, serialization, business methods
- **Service Layer**: Async database operations (CRUD), transaction handling, error cases
- **Database Layer**: SQLAlchemy async patterns, connection management, data persistence

**Integration Tests (7/39)**
- **API Structure**: Route existence, HTTP status codes, error handling
- **Input Validation**: Schema enforcement, malformed requests
- **Service Contracts**: OpenAPI specification, documentation availability
- **Application Lifecycle**: FastAPI initialization, middleware configuration

### Testing Approach

**Container-Based Database Testing**
- PostgreSQL 17 containers managed via Docker Compose
- Automatic container startup with health checks
- Function-scoped database engines (fresh DB per test)
- Complete schema recreation for test isolation

**Async Testing Patterns**
- pytest-asyncio with `mode=auto` configuration
- Function-scoped async fixtures to avoid event loop conflicts
- Proper async/await patterns throughout test suite
- SQLAlchemy 2.0+ async session management

**Dependency Injection**
- Global database manager replacement for tests
- Module-level dependency overrides
- Clean fixture lifecycle with proper teardown

### Test Execution
```bash
# Full test suite (CI/CD ready)
./test-pipeline.sh

# Unit tests only (fast feedback)
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# With coverage
uv run pytest --cov=src tests/
```

### Known Limitations & Blind Spots

**Integration Test Constraints**
- TestClient async limitations prevent full end-to-end database integration
- Some API endpoints tested for structure only (not full database persistence)
- Event loop isolation between TestClient and async database connections

**Coverage Gaps**
- No end-to-end workflow tests through full request lifecycle
- Limited error condition testing for database connection failures
- No performance/load testing for concurrent async operations
- Authentication/authorization not implemented (out of scope)

**Infrastructure Dependencies**
- Requires Docker for database containers
- PostgreSQL-specific async patterns (not database-agnostic)
- Local development environment assumptions

### Quality Gates
- **Zero failing tests** (enforced in CI/CD)
- **Container startup verification** before test execution
- **Database isolation** between test runs
- **Async pattern compliance** throughout codebase

### Future Testing Enhancements
- Add AsyncClient-based integration tests for full async workflows
- Implement database connection failure simulation
- Add performance benchmarks for async operations
- Container security scanning integration

## Configuration

### Application Settings

Environment variables (all optional with defaults):

- `PORT`: Server port (default: 8001)
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `SQL_DEBUG`: Enable SQL query logging (default: false)
- `CORS_ORIGINS`: Comma-separated CORS origins (default: *)
- `API_TITLE`: API title (default: Todo Backend API)
- `API_DESCRIPTION`: API description
- `API_VERSION`: API version (default: 1.0.0)

## Development

### Install Dependencies
```bash
uv sync --group dev
```

### Code Quality
```bash
# Check formatting and linting
./lint.sh

# Fix formatting
./lint.sh --fix

# Manual commands
uv run black src/
uv run flake8 src/
```

### Running Locally
```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Testing
```bash
uv run pytest
```

## Building

```bash
./build.sh
```

## Deployment

The service is designed to run in Kubernetes as a backend API service for the todo-app frontend.

```bash
kubectl apply -f manifests/
```

## API Documentation

When running, visit:
- `http://localhost:8001/docs` - Swagger UI
- `http://localhost:8001/redoc` - ReDoc
