# Todo Backend API

Backend service for the todo application. Provides REST API endpoints for managing todos with PostgreSQL database persistence.

## Features

- **PostgreSQL Database**: Async SQLAlchemy with connection pooling
- **NATS Event Publishing**: Publishes todo creation/update events to message broker
- **Pydantic Settings**: Environment-based configuration with validation
- **Code Quality**: Ruff formatting and linting for Python 3.13+
- **REST API**: FastAPI with automatic OpenAPI documentation
- **CORS Support**: Configurable cross-origin resource sharing
- **Health Checks**: Built-in health endpoint for monitoring
- **Database Migration**: Automatic table creation and sample data
- **Graceful Degradation**: Operates normally even if NATS is unavailable

## Endpoints

- `GET /health` - Health check with todo count
- `GET /todos` - List all todos (JSON)
- `POST /todos` - Create new todo (JSON)
- `GET /todos/{id}` - Get specific todo (JSON)
- `PUT /todos/{id}` - Update todo (JSON)  
- `DELETE /todos/{id}` - Delete todo

Important deployment note - routing expectations
-------------------------------------------------

- The backend expects to receive API calls in JSON format on its `/todos` endpoints. Browser form submissions for creating todos are handled by the frontend service and are sent to the frontend `/todos` route as `application/x-www-form-urlencoded`.
- The frontend converts the form data to JSON and then calls the backend's `POST /todos` endpoint internally. Therefore, any gateway/ingress/HTTPRoute must route browser requests for `/todos` to the **frontend** service, not directly to the backend. Routing `/todos` directly to the backend will bypass the frontend's conversion step and can result in request parsing errors.


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
   cd .. && ./test-be.sh
   ```

The test database (`todoapp_test` on port 5433) is automatically cleaned between tests.

See `tests/TEST_PLAN.md` for comprehensive testing documentation.

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

### NATS Configuration

Event publishing to NATS message broker (optional - service degrades gracefully if unavailable):

- `NATS_URL`: NATS server URL (default: auto-detected based on environment)
  - **Kubernetes**: `nats://nats:4222` (service discovery)
  - **Local/Docker**: `nats://localhost:4222`
- `NATS_TOPIC`: Topic for todo events (default: `todos.events`)
- `NATS_CONNECT_TIMEOUT`: Connection timeout in seconds (default: 10)
- `NATS_MAX_RECONNECT_ATTEMPTS`: Reconnection attempts (default: 5)

**Event Publishing Behavior**:
- Creates events on todo creation and updates
- Non-blocking: NATS failures don't affect todo operations
- JSON message format with action type (`created`, `updated`)
- Automatic service discovery in Kubernetes environments

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
cd .. && ./test-be.sh
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
