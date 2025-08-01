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
