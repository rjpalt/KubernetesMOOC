# Todo App with Hourly Images (Refactored)

A FastAPI application that displays random images from Lorem Picsum with caching and automatic refresh functionality. **Now featuring a properly refactored, modular architecture** following software engineering best practices with clean separation of concerns, dependency injection, and maintainable code structure.

## Features

- **Automatic Image Refresh**: Downloads new images every 10 minutes (configurable)
- **Manual Image Fetching**: Button to immediately fetch new images for testing
- **Persistent Image Caching**: Images survive application restarts via volume mounts
- **Image Metadata**: Track when images were fetched, file sizes, etc.
- **Container Testing**: Built-in shutdown endpoint for testing container resilience
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

- `GET /` - Main UI with image display and test controls
- `GET /health` - Health check with cache status
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
```

## Testing Features

The application includes several features specifically for testing:

1. **Manual Fetch Button**: Test image downloading without waiting
2. **Force Fetch**: Bypass cache timing to get new images immediately  
3. **Image Info Endpoint**: Inspect cache status and metadata
4. **Configurable Interval**: Set to 30 seconds for rapid testing
5. **Shutdown Endpoint**: Test container restart behavior
6. **Detailed Logging**: All operations are logged for debugging

## Architecture

- **Modular Design**: Proper separation of concerns with dedicated modules for configuration, services, API routes, and data models
- **Dependency Injection**: Clean dependency management through FastAPI's dependency injection system
- **Service Layer Pattern**: Business logic separated from API endpoints
- **Configuration Management**: Centralized settings with environment variable support
- **Data Models**: Type-safe Pydantic models for all data structures
- **Background Task Management**: Proper lifecycle management for background processes
- **FastAPI Framework**: Modern async web framework with automatic OpenAPI documentation
- **Jinja2 Templating**: Professional template engine for clean HTML rendering
- **Atomic Operations**: Images written to temp files then renamed (prevents corruption)
- **Graceful Error Handling**: Network issues don't crash the application
- **Metadata Tracking**: Timestamp, file size, and source URL stored separately

## Code Structure

```
todo-app/
├── src/                       # Complete application source
│   ├── main.py               # Application entry point
│   ├── config/
│   │   └── settings.py       # Centralized configuration management
│   ├── models/
│   │   └── image.py          # Pydantic data models
│   ├── services/
│   │   ├── image_service.py  # Business logic for image operations
│   │   └── background.py     # Background task management
│   ├── api/
│   │   ├── dependencies.py   # Dependency injection setup
│   │   └── routes/
│   │       ├── images.py     # Image-related endpoints
│   │       └── health.py     # Health/system endpoints
│   └── core/
│       ├── cache.py          # Image cache management
│       └── lifespan.py       # Application lifespan management
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Base template with common structure
│   └── index.html            # Main page template
├── pyproject.toml            # Dependencies and project config
├── Dockerfile                # Container configuration
├── REFACTORING_README.md     # Detailed refactoring documentation
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

### Template Development

The application uses Jinja2 templating for clean separation between backend logic and frontend presentation:

- **base.html**: Contains common HTML structure, CSS, and template blocks
- **index.html**: Extends base template with page-specific content
- **Template Variables**: Passed from FastAPI endpoints to templates
- **Template Inheritance**: Modular design for easy maintenance and extension

### Adding New Features

The refactored architecture makes it easy to add new functionality:

1. **New API Endpoints**: Add routes in `src/api/routes/`
2. **Business Logic**: Implement in service classes in `src/services/`
3. **Data Models**: Define Pydantic models in `src/models/`
4. **Configuration**: Add settings to `src/config/settings.py`
5. **Templates**: Create new Jinja2 templates extending `base.html`

Example service:
```python
# src/services/new_service.py
class NewService:
    def __init__(self, dependency: SomeDependency):
        self.dependency = dependency
    
    async def do_something(self) -> SomeModel:
        # Business logic here
        pass
```

Example route:
```python
# src/api/routes/new_routes.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/new-endpoint")
async def new_endpoint(service: NewService = Depends(get_new_service)):
    return await service.do_something()
```

## Summary

This application demonstrates modern Python web development best practices with a **properly refactored, modular architecture**:

- **Modular Design**: Clean separation of configuration, services, API routes, models, and core functionality
- **Dependency Injection**: Proper service layer with dependency injection instead of global variables
- **SOLID Principles**: Single Responsibility, proper abstractions, and clean interfaces
- **FastAPI**: Modern async web framework with automatic OpenAPI generation
- **Pydantic Models**: Type-safe data validation and serialization
- **Jinja2 Templating**: Professional separation of HTML templates from Python logic  
- **Async Operations**: Non-blocking file I/O and HTTP requests
- **Background Tasks**: Automatic image fetching with proper lifecycle management
- **Error Handling**: Graceful degradation when services are unavailable
- **Code Quality**: Black formatting, flake8 linting, 120-character line limits
- **Comprehensive Documentation**: OpenAPI specification and interactive docs
- **Testing Features**: Manual controls and container resilience testing
- **Maintainable Architecture**: Easy to test, extend, and modify individual components

## Refactoring Benefits

The application has been completely refactored from a monolithic `main.py` file to a proper modular architecture:

- **Before**: 311 lines of mixed responsibilities in a single file
- **After**: Clean, modular structure with proper separation of concerns
- **Testability**: Each component can be unit tested in isolation
- **Maintainability**: Changes to one component don't affect others
- **Scalability**: Easy to add new features without modifying existing code
- **Developer Experience**: Much easier to understand and work with

See `REFACTORING_README.md` for detailed information about the refactoring process and architectural improvements.