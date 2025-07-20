# Todo Application with Image Integration

A FastAPI-based todo application that combines task management with background image caching functionality. **Features a properly refactored, modular architecture** following software engineering best practices with clean separation of concerns, dependency injection, and maintainable code structure.

## Features

### Todo Management
- **Todo Display**: View all todos with status indicators (done/not-done)
- **Todo Models**: Structured todo items with text (max 140 chars), status, timestamps, and unique IDs
- **Read-Only Interface**: Display todos from service layer (CRUD operations planned for future implementation)
- **Character Counter**: Real-time validation for todo text input

### Image Integration
- **Automatic Image Refresh**: Downloads new images every 10 minutes (configurable)
- **Manual Image Fetching**: Button to immediately fetch new images for testing
- **Persistent Image Caching**: Images survive application restarts via volume mounts
- **Image Metadata**: Track when images were fetched, file sizes, etc.
- **Container Testing**: Built-in shutdown endpoint for testing container resilience

### Architecture
- **Modern UI**: Jinja2 templated responsive web interface with proper separation of concerns
- **Modular Architecture**: Clean separation between configuration, business logic, API routes, and data models
- **Dependency Injection**: Proper service layer with dependency injection instead of global variables
- **Template Inheritance**: Modular HTML templates for maintainable code
- **Testable Design**: Each component can be tested in isolation
- **SOLID Principles**: Single Responsibility, proper abstractions, and clean interfaces

## Quick Start (Local Development)

```bash
# Install dependencies
uv sync

# Start the application (using refactored structure)
python -m src.main

# Or with uvicorn directly
uvicorn src.main:app --reload --port 8000
```

The application will be available at http://localhost:8000

**Note**: FastAPI automatically generates interactive API documentation at `/docs` and `/redoc` endpoints.

### Dependencies

- Python 3.13+
- FastAPI - Modern web framework
- Pydantic - Data validation and settings management
- Jinja2 - Template engine for clean HTML rendering
- httpx - Async HTTP client for image fetching
- aiofiles - Async file operations
- uvicorn - ASGI server

## Configuration

Environment variables:

- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)
- `DEBUG` - Enable debug mode (default: false)
- `IMAGE_CACHE_PATH` - Directory for cached images (default: ./images)
- `IMAGE_UPDATE_INTERVAL_MINUTES` - How often to auto-fetch images (default: 10)
- `PICSUM_URL` - Lorem Picsum URL (default: https://picsum.photos/1200)
- `HTTP_TIMEOUT` - HTTP client timeout (default: 30.0)
- `LOG_LEVEL` - Logging level (default: INFO)
- `TEMPLATE_DIRECTORY` - Template directory (default: templates)

## API Endpoints

### Main Application
- `GET /` - Main UI displaying todo list and image with management controls
- `GET /health` - Health check with cache status and application state

### Todo Endpoints (Currently Read-Only)
- Todo data is served via the main page template
- Todo models support full CRUD structure (create, update, delete operations planned)
- Current implementation shows sample todos from `TodoService`

### Image Management
- `GET /image` - Serve current cached image
- `GET /image/info` - Image metadata (JSON)
- `POST /fetch-image` - Manually trigger image fetch
- `POST /fetch-image?force=true` - Force fetch (bypass cache timing)
- `POST /shutdown` - Shutdown container (for testing)

## API Documentation

### OpenAPI Specification

The application includes a comprehensive OpenAPI 3.1 specification in `openapi.yaml`. You can:

1. **View Interactive Docs**: Visit http://localhost:8000/docs (FastAPI auto-generated)
2. **View ReDoc**: Visit http://localhost:8000/redoc (alternative documentation UI)
3. **Use Standalone Spec**: Import `openapi.yaml` into API tools like Postman, Insomnia, or OpenAPI generators

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Get image metadata  
curl http://localhost:8000/image/info

# Manual image fetch
curl -X POST http://localhost:8000/fetch-image

# Force image fetch
curl -X POST "http://localhost:8000/fetch-image?force=true"

# Test container shutdown
curl -X POST http://localhost:8000/shutdown

# Note: Todo CRUD endpoints are planned but not yet implemented
# Current todo functionality is display-only via the main page
```

## Testing Features

The application includes several features for testing and development:

### Todo Application Testing
1. **Sample Data**: Pre-loaded with example todos for development
2. **Status Display**: Visual indication of todo completion status
3. **Character Validation**: Real-time character count for 140-char limit
4. **Template Testing**: Todo list rendering and status indicators

### Image System Testing  
1. **Manual Fetch Button**: Test image downloading without waiting
2. **Force Fetch**: Bypass cache timing to get new images immediately  
3. **Image Info Endpoint**: Inspect cache status and metadata
4. **Configurable Interval**: Set to 30 seconds for rapid testing
5. **Shutdown Endpoint**: Test container restart behavior
6. **Detailed Logging**: All operations are logged for debugging

## Current Implementation Status

### ✅ Completed Features
- **Todo Models**: Full Pydantic models with validation
- **Todo Service**: Service layer with sample data management
- **Todo Display**: UI showing todo list with status indicators  
- **Image Caching**: Complete background image fetch and caching system
- **Template System**: Modular Jinja2 templates with inheritance
- **Dependency Injection**: Clean service layer architecture
- **API Documentation**: OpenAPI spec with interactive docs

### 🔄 Planned Features (Per PROJECT_SPECIFICATION.md)
- **Todo CRUD Operations**: POST/PUT/DELETE endpoints for todo management
- **HTMX Integration**: Dynamic UI updates without page reloads
- **Persistent Storage**: File-based or database persistence
- **Real Todo Interactions**: Functional add/edit/delete operations

## Architecture

- **Todo Management**: Service-based architecture for todo operations with Pydantic models
- **Dual Purpose Design**: Combines todo application logic with background image caching
- **Modular Design**: Proper separation of concerns with dedicated modules for configuration, services, API routes, and data models
- **Dependency Injection**: Clean dependency management through FastAPI's dependency injection system
- **Service Layer Pattern**: Business logic separated from API endpoints (TodoService, ImageService)
- **Configuration Management**: Centralized settings with environment variable support
- **Data Models**: Type-safe Pydantic models for todos and image metadata
- **Background Task Management**: Proper lifecycle management for image fetch processes
- **FastAPI Framework**: Modern async web framework with automatic OpenAPI documentation
- **Jinja2 Templating**: Professional template engine for clean HTML rendering with todo list integration
- **Atomic Operations**: Images written to temp files then renamed (prevents corruption)
- **Graceful Error Handling**: Network issues don't crash the application
- **Metadata Tracking**: Timestamp, file size, and source URL stored separately

## Code Structure

```
todo-app/
├── src/                       # Complete application source
│   ├── main.py               # Application entry point (FastAPI app with todo+image routes)
│   ├── config/
│   │   └── settings.py       # Centralized configuration management
│   ├── models/
│   │   ├── todo.py           # Todo data models (Todo, TodoStatus)
│   │   └── image.py          # Image metadata models
│   ├── services/
│   │   ├── todo_service.py   # Todo business logic and sample data
│   │   ├── image_service.py  # Image fetch and caching logic
│   │   └── background.py     # Background task management
│   ├── api/
│   │   ├── dependencies.py   # Dependency injection setup
│   │   └── routes/
│   │       ├── images.py     # Image + main page endpoints (includes todo display)
│   │       └── health.py     # Health/system endpoints
│   └── core/
│       ├── cache.py          # Image cache management
│       └── lifespan.py       # Application lifespan management
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Base template with common structure
│   └── index.html            # Main page template (todo list + image display)
├── manifests/                 # Kubernetes deployment manifests
│   ├── deployment.yaml       # Pod deployment configuration
│   ├── service.yaml          # Service configuration
│   ├── ingress.yaml          # Ingress configuration
│   ├── persistentvolume.yaml # Storage configuration
│   └── persistentvolumeclaim.yaml
├── pyproject.toml            # Dependencies and project config
├── Dockerfile                # Container configuration
├── PROJECT_SPECIFICATION.md  # Complete project requirements
├── TESTING_PLAN.md          # Testing strategy and procedures
└── images/                   # Image cache directory (created at runtime)
    ├── current.jpg           # Currently displayed image
    └── metadata.txt          # Image fetch timestamp and metadata
```

## Development

### Code Quality Tools

```bash
# Format code
black .

# Lint code
flake8

# Both checks (configured for 120-character line length)
black --check . && flake8
```

### Testing

The application includes a comprehensive test suite covering current functionality:

```bash
# Install test dependencies
uv sync --group test

# Run all tests with coverage
uv run pytest

# Run specific test categories
uv run pytest tests/unit/           # Unit tests only
uv run pytest tests/integration/    # Integration tests only

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_models.py -v
```

**Test Structure:**
- `tests/unit/` - Unit tests for models, services, and business logic
- `tests/integration/` - Integration tests for API endpoints and templates
- `tests/fixtures/` - Shared test data and utilities

**Current Test Coverage:**
- ✅ Todo models validation (character limits, status validation) - **12 tests**
- ✅ Todo service functionality (sample data, business logic) - **10 tests**  
- ✅ Image service regression prevention (basic functionality) - **5 tests**
- ✅ Health check endpoints (monitoring and shutdown) - **7 tests**
- ✅ HTML template rendering with todo/image data - **8 tests**
- ✅ Dependency injection and service layer

**Test Metrics:**
- **37 passing tests** with 0 failures
- **75.78% code coverage** on business logic
- **Fast execution** (<1 second total)
- **No external dependencies** (mocked HTTP calls, file I/O)

**Test Requirements:**
- Maintains >75% code coverage on business logic  
- Fast execution (<10 seconds total for unit tests)
- Uses mocked dependencies to prevent external API calls
- Validates both happy path and error conditions
- Excludes `__init__.py` files from coverage metrics

## CI/CD Pipeline

The application includes a comprehensive CI/CD pipeline using GitHub Actions with support for local testing via Act.

### GitHub Actions Workflow

The pipeline consists of three main jobs:

1. **Unit Tests** (`test-unit`): Runs unit tests with coverage reporting
2. **Integration Tests** (`test-integration`): Runs integration tests for API endpoints
3. **Container Tests** (`test-container`): Builds and validates Docker container

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` branch

**Pipeline Features:**
- Uses Python 3.13 and `uv` package manager
- Parallel job execution for faster feedback
- Coverage reporting without failure thresholds
- Docker build validation and basic health checks

### Local Testing with Act

[Act](https://github.com/nektos/act) allows you to run GitHub Actions locally:

```bash
# Install act (macOS)
brew install act

# Run all jobs
act

# Run specific jobs
act --job test-unit           # Unit tests only
act --job test-integration    # Integration tests only  
act --job test-container      # Container tests only

# Run with verbose output
act --verbose

# List available jobs
act --list
```

**Act Configuration:**
- Uses `.actrc` for default settings
- Configured for `ubuntu-latest` platform
- Supports Docker-in-Docker for container tests

### Container Testing

Basic container validation tests verify:
- Docker image builds successfully
- Container starts and responds to health checks
- Required dependencies are available
- Application environment is correctly configured

```bash
# Run container tests locally
uv run pytest tests/container/ -v

# Test Docker build manually
docker build -t todo-app:test .
docker run -d --name todo-test -p 8080:8080 todo-app:test
curl http://localhost:8080/health
docker stop todo-test && docker rm todo-test
```

### Pipeline Commands

```bash
# Commands used in CI/CD pipeline:

# Install dependencies
uv sync --group test

# Run tests by category
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
uv run pytest tests/container/ -v

# Generate coverage
uv run pytest --cov=src --cov-report=xml --cov-report=term-missing

# Build container
docker build -t todo-app:test .

# Container health check
curl -f http://localhost:8080/health
```
