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

### Template Development

The application uses Jinja2 templating for clean separation between backend logic and frontend presentation:

- **base.html**: Contains common HTML structure, CSS, and template blocks
- **index.html**: Extends base template with page-specific content
- **Template Variables**: Passed from FastAPI endpoints to templates
- **Template Inheritance**: Modular design for easy maintenance and extension

### Adding New Features

The refactored architecture makes it easy to add new functionality:

1. **New Todo Operations**: Add CRUD endpoints in `src/api/routes/images.py` or create `src/api/routes/todos.py`
2. **Todo Business Logic**: Extend `TodoService` in `src/services/todo_service.py`
3. **Data Models**: Add fields to `Todo` model or create new models in `src/models/`
4. **Configuration**: Add todo-related settings to `src/config/settings.py`
5. **Templates**: Extend `index.html` with HTMX attributes for dynamic todo interactions

Example todo CRUD endpoint:
```python
# src/api/routes/todos.py (planned)
@router.post("/todos")
async def create_todo(
    todo_data: TodoCreate, 
    todo_service: TodoService = Depends(get_todo_service)
):
    return await todo_service.create_todo(todo_data)

@router.put("/todos/{todo_id}")
async def update_todo_status(
    todo_id: str,
    status: TodoStatus,
    todo_service: TodoService = Depends(get_todo_service)
):
    return await todo_service.update_status(todo_id, status)
```

Example HTMX integration:
```html
<!-- Planned HTMX enhancement for templates/index.html -->
<form hx-post="/todos" hx-target="#todo-list" hx-swap="beforeend">
    <input name="text" maxlength="140" placeholder="What needs to be done?">
    <button type="submit">Add Todo</button>
</form>
```

## Summary

This application demonstrates modern Python web development best practices with a **properly refactored, modular architecture** for a todo application with integrated image caching:

### Core Application Features
- **Todo Management**: Complete data models and service layer for todo operations
- **Image Integration**: Background image caching system with manual controls
- **Hybrid Interface**: Single page displaying both todo list and current image

### Technical Excellence
- **Modular Design**: Clean separation of todo logic, image logic, configuration, and API routes
- **Dependency Injection**: Proper service layer with dependency injection for TodoService and ImageService
- **SOLID Principles**: Single Responsibility, proper abstractions, and clean interfaces
- **FastAPI**: Modern async web framework with automatic OpenAPI generation
- **Pydantic Models**: Type-safe data validation for todos and image metadata
- **Jinja2 Templating**: Professional separation of HTML templates from Python logic  
- **Async Operations**: Non-blocking file I/O and HTTP requests
- **Background Tasks**: Automatic image fetching with proper lifecycle management
- **Error Handling**: Graceful degradation when services are unavailable
- **Code Quality**: Black formatting, flake8 linting, 120-character line limits
- **Comprehensive Documentation**: OpenAPI specification, project specs, and testing plans
- **Kubernetes Ready**: Complete manifest files for container orchestration
- **Testing Features**: Manual controls and container resilience testing
- **Maintainable Architecture**: Easy to test, extend, and modify individual components

### Development Status
- **Current**: Display-only todo interface with full image caching functionality
- **Next Steps**: Implement todo CRUD endpoints and HTMX integration per PROJECT_SPECIFICATION.md
