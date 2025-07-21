# Todo Backend API

Backend service for the todo application. Provides REST API endpoints for managing todos.

## Features

- **Pydantic Settings**: Environment-based configuration with validation
- **Code Quality**: Black formatting and Flake8 linting
- **REST API**: FastAPI with automatic OpenAPI documentation
- **CORS Support**: Configurable cross-origin resource sharing
- **Health Checks**: Built-in health endpoint for monitoring

## Endpoints

- `GET /health` - Health check with todo count
- `GET /todos` - List all todos (JSON)
- `POST /todos` - Create new todo (JSON)
- `GET /todos/{id}` - Get specific todo (JSON)
- `PUT /todos/{id}` - Update todo (JSON)  
- `DELETE /todos/{id}` - Delete todo

## Configuration

Environment variables (all optional with defaults):

- `PORT`: Server port (default: 8001)
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
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
