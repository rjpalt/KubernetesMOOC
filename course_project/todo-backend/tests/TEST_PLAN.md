# Todo Backend - Testing Plan

Testing strategy for the todo-backend microservice with async database integration.

## Test Structure

```
tests/
├── unit/                     # Fast, isolated tests
│   ├── test_todo_service.py  # Business logic tests
│   └── test_models.py        # Data model tests
├── integration/              # API endpoint tests with database
│   ├── test_todo_endpoints.py # REST API tests
│   ├── test_todo_api_structure.py # API structure tests
│   └── test_request_logging.py # Request logging middleware tests
└── conftest.py              # Test configuration with async support
```

**Status**: 66/66 tests passing

## Running Tests

### Prerequisites
```bash
cd course_project/todo-backend
uv sync --group dev
```

### Quick Test Commands
```bash
# Run all tests (recommended)
cd .. && ./test-be.sh

# Or run manually
uv run pytest tests/ -v
```

### Test Categories
```bash
# Unit tests only (fastest - no database)
uv run pytest tests/unit/ -v

# Integration tests only (with PostgreSQL database)
uv run pytest tests/integration/ -v

# Specific test file
uv run pytest tests/integration/test_todo_endpoints.py -v
```

### Coverage Reports
```bash
uv run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Test Architecture

### Unit Tests (`tests/unit/`)
- **Purpose**: Business logic testing in isolation
- **Speed**: < 1 second
- **Dependencies**: None
- **Database**: In-memory TodoService

```python
def test_create_todo_adds_new_todo():
    service = TodoService()
    todo_data = TodoCreate(text="Test todo")
    new_todo = service.create_todo(todo_data)
    assert new_todo.text == "Test todo"
```

### Integration Tests (`tests/integration/`)
- **Purpose**: HTTP API endpoints with database operations
- **Speed**: < 5 seconds total
- **Dependencies**: PostgreSQL container, AsyncClient
- **Database**: Real PostgreSQL with per-test isolation

```python
async def test_create_todo_returns_created_todo(test_client: AsyncClient):
    response = await test_client.post("/todos", json={"text": "API test"})
    assert response.status_code == 201
    created_todo = response.json()
    assert created_todo["text"] == "API test"
```

## Async Testing Implementation

### Event Loop Management
Uses AsyncClient with ASGITransport for proper async integration.

### Database Test Isolation
- PostgreSQL test container auto-started
- Fresh tables created per test
- Dedicated test database connection pool
- Global db_manager replaced for test isolation

```python
@pytest_asyncio.fixture
async def test_client(test_db_manager):
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
```

## Test Scope

### Covered Areas
- Business logic (Todo CRUD operations with async database persistence)
- API contracts (HTTP endpoints, formats, status codes)
- Data validation (Input validation, error handling)
- Database integration (Real PostgreSQL operations)
- Service independence (Backend works without external dependencies)
- Container readiness (Database connectivity, health checks)
- Request logging (Comprehensive request/response monitoring)
- Error monitoring (Structured logging for all HTTP error types)
- Performance metrics (Response time tracking for SLA monitoring)

### Excluded Areas
- Frontend concerns
- Inter-service communication
- Kubernetes deployment
- Infrastructure (Load balancing, ingress, persistent volumes)

## Test Coverage Analysis

### Test Inventory (66 Tests Total)

#### Unit Tests (35 tests)
**test_models.py** - Data Model Validation (18 tests)
- TodoStatus enum validation (3 tests)
- TodoCreate input validation (4 tests)
- TodoUpdate validation (4 tests)  
- Todo model behavior (7 tests)

**test_todo_service.py** - Business Logic (17 tests)
- Service initialization (2 tests)
- CRUD operations (8 tests)
- Edge cases (3 tests)
- Data integrity (4 tests)

#### Integration Tests (31 tests)
**test_todo_api_structure.py** - API Infrastructure (7 tests)
- Health endpoint structure and availability
- API documentation endpoints (/docs, /openapi.json)
- Basic routing and CORS configuration
- Application startup validation

**test_todo_endpoints.py** - Full API Testing (16 tests)
- GET /todos: Empty list handling, data retrieval
- POST /todos: Creation with validation, persistence verification, error handling
- GET /todos/{id}: Individual todo retrieval, 404 handling
- PUT /todos/{id}: Update operations, validation, 404 handling
- DELETE /todos/{id}: Deletion operations, 404 handling
- Integration workflow: Complete CRUD lifecycle testing

**test_request_logging.py** - Request Logging Middleware (8 tests)
- Structured JSON logging for all requests/responses
- Response time monitoring and performance metrics
- Error classification (validation, not found, server errors)
- Client IP extraction and user agent tracking
- Log format validation for Grafana integration

### Test Category Validation

#### Data Model Tests (18 tests)
- Input sanitization
- Business rules validation
- API serialization consistency
- Validation logic

#### Business Logic Tests (17 tests)
- State management
- ID generation
- Data persistence
- Edge case handling

#### API Structure Tests (7 tests)
- Health endpoints (Kubernetes readiness/liveness probe compatibility)
- API documentation
- CORS configuration
- Application bootstrap

#### Request Logging Tests (8 tests)
- Structured JSON logging format verification
- Response time measurement accuracy
- Error classification (validation, not found, client, server errors)
- Request details capturing (method, path, IP, user agent)
- Log output format suitable for Grafana parsing
- Performance impact validation

#### Full API Tests (16 tests)
- HTTP protocol compliance
- Database integration
- Error scenarios
- Workflow validation

## Test Gaps

### Security Testing
- SQL injection prevention
- Input sanitization  
- Rate limiting
- Authentication/authorization

### Database Reliability
- Connection pool exhaustion
- Transaction rollback
- Database downtime scenarios
- Data migration testing

### Performance & Scalability
- Load testing
- Large dataset performance
- Memory usage validation
- Response time SLAs

### Operational Readiness  
- Graceful shutdown
- Resource constraints
- Log format validation
- Monitoring metrics

### Integration Boundaries
- Network failures
- Timeout handling
- Configuration management
- Secret management

## Risk Assessment

| Risk Area | Current Coverage | Impact | Likelihood | Priority |
|-----------|------------------|---------|------------|----------|
| SQL Injection | None | High | Medium | High |
| Database Downtime | None | High | Medium | High |
| Load/Concurrency | None | High | High | High |
| Container Limits | None | Medium | High | Medium |
| Input Sanitization | None | Medium | Medium | Medium |
| Graceful Shutdown | None | Medium | Low | Low |

## Recommended Test Additions

### High Priority
```python
# SQL Injection Prevention
async def test_sql_injection_in_todo_text():
    malicious_input = {"text": "'; DROP TABLE todos; --"}
    response = await test_client.post("/todos", json=malicious_input)
    assert response.status_code == 201

# Database Connection Failure
async def test_database_unavailable_returns_503():
    with patch('src.database.connection.db_manager') as mock_db:
        mock_db.get_session.side_effect = ConnectionError()
        response = await test_client.get("/todos")
        assert response.status_code == 503
```

### Medium Priority
```python
# Load Testing
async def test_concurrent_todo_creation():
    tasks = [test_client.post("/todos", json={"text": f"Todo {i}"}) 
             for i in range(100)]
    responses = await asyncio.gather(*tasks)
    assert all(r.status_code == 201 for r in responses)
```

## Production Readiness

Tests verify Kubernetes deployment requirements:
- Health endpoints (/be-health returns service status + todo count)
- Database connectivity (Async PostgreSQL connection handling)
- Error handling (Proper HTTP status codes and error responses)
- Input validation (Request validation matches OpenAPI schema)
- CORS configuration (Microservice communication headers)
- Container lifecycle (Database startup/shutdown handling)

## Data Contract Consistency

Tests use fixtures matching exact backend response formats:

```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "Learn Kubernetes testing patterns", 
    "status": "not-done",
    "created_at": "2025-07-28T10:00:00Z"
}
```

## Development Workflow

### Before Making Changes
```bash
cd .. && ./test-be.sh  # Ensure all 66 tests pass
```

### After Making Changes
```bash
# Run affected tests
uv run pytest tests/unit/test_todo_service.py  # If you changed TodoService
uv run pytest tests/integration/test_todo_endpoints.py  # If you changed API routes

# Run full suite before committing  
cd .. && ./test-be.sh
```

### Adding New Features
1. Write unit tests first for business logic
2. Write integration tests for new API endpoints with database
3. Update test fixtures if data formats change
4. Verify async compatibility for database operations
5. Run full test suite to ensure no regressions

### Async Test Guidelines
```python
# Correct
async def test_create_todo_with_database(test_client: AsyncClient):
    response = await test_client.post("/todos", json={"text": "Test"})
    assert response.status_code == 201

# Avoid - causes event loop conflicts
def test_create_todo_sync(test_client: TestClient):
    response = test_client.post("/todos", json={"text": "Test"})
```

## CI/CD Integration

### Automated Testing
Tests run automatically on:
- Pull requests to main branch
- Changes to `course_project/todo-backend/**`
- Container image builds

### Local CI Testing with ACT

```bash
# Test backend CI pipeline locally
act --job test-backend

# Test other jobs
act --job code-quality
act --job test-frontend
```

#### ACT Setup

1. Install ACT (macOS with Homebrew):
   ```bash
   brew install act
   ```

2. Create secrets file for database credentials:
   ```bash
   # Copy example file (recommended)
   cp .secrets.example .secrets
   
   # Or create manually (automatically gitignored)
   cat > .secrets << EOF
   TEST_POSTGRES_USER=test_user
   TEST_POSTGRES_PASSWORD=test_password123
   EOF
   ```

3. Run tests:
   ```bash
   act --job test-backend  # Runs full backend test suite with PostgreSQL
   ```

#### ACT Integration
GitHub Actions workflow automatically detects ACT execution and:
- Sets database environment variables from GitHub secrets
- Uses local PostgreSQL container for testing
- Maintains identical behavior between local and CI environments

### Test Results Integration
- Coverage reports generated and stored as CI artifacts
- Test isolation: Each CI run gets fresh database containers  
- Async compatibility: CI environment handles async tests properly
- Container dependencies: PostgreSQL containers managed automatically
- Secret management: GitHub secrets for CI, .secrets file for local ACT testing

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# If you see "ModuleNotFoundError: No module named 'src'"
cd course_project/todo-backend  # Always run from correct directory
uv sync --group dev  # Ensure dev dependencies installed
```

#### Database Connection Issues
```bash
# If tests fail with database connection errors
docker ps  # Check if postgres container is running
cd .. && ./test-be.sh  # Script handles container lifecycle
```

#### Event Loop Conflicts
```python
# Use proper async patterns:
async def test_new_feature(test_client: AsyncClient):  # Correct
    response = await test_client.get("/endpoint")

def test_new_feature(test_client: TestClient):  # Avoid - causes issues
    response = test_client.get("/endpoint")
```

### Test Performance
- Unit tests: ~0.1 seconds (no database)
- Integration tests: ~1.0 seconds (with PostgreSQL)  
- Total suite: ~1.1 seconds (66 tests)
- Database startup: ~2-3 seconds (only if container not running)

### Debugging Tests
```bash
# Verbose output with print statements
uv run pytest tests/ -v -s

# Run single test
uv run pytest tests/integration/test_todo_endpoints.py::TestTodoEndpointsLimited::test_create_todo_returns_created_todo -v -s

# Drop into debugger on failure
uv run pytest tests/ --pdb
```

## Future Testing Roadmap

### Completed
- Unit tests: Business logic testing with TodoService
- Integration tests: API endpoints with real database
- Async database support: Event loop conflict resolution
- Container integration: PostgreSQL test database automation
- Test isolation: Per-test database state management
- CI/CD integration: Automated testing pipeline

### Planned Enhancements
- Contract testing
- Performance testing  
- Security testing
- Chaos testing
- End-to-end testing

### Kubernetes-Specific Testing (Future)
- Health check validation
- Resource constraint testing
- Service discovery testing
- ConfigMap/Secret integration
- Graceful shutdown testing

---

**Status**: Strong foundation for development and basic deployment. Requires security and performance testing for production readiness.

