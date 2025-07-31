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

**Status**: 75/75 tests passing

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

### Test Inventory (75 Tests Total)

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

#### Integration Tests (40 tests)
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

**test_request_logging.py** - Request Logging Middleware (12 tests)
- Structured JSON logging for all requests/responses
- Response time monitoring and performance metrics
- Error classification (validation, not found, server errors)
- Client IP extraction and user agent tracking
- Log format validation for Grafana integration
- Request correlation ID generation and preservation
- Request-response correlation tracking
- Error log correlation ID inclusion

**test_sql_injection_prevention.py** - SQL Injection Security (5 tests)
- SQL injection payload testing in todo text creation
- Parameter injection testing in todo ID operations
- Update operation injection testing
- Database stability under sustained injection attacks
- Parameter type validation preventing SQL injection

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

### Critical Security Vulnerabilities (OWASP Top 10)

#### 1. Broken Authentication & Authorization (OWASP #1)
- **CRITICAL**: No authentication mechanism implemented
- **CRITICAL**: No authorization controls on any endpoints  
- **CRITICAL**: Any user can access/modify any todo
- **CRITICAL**: No session management
- **CRITICAL**: No user identity verification

#### 2. Cryptographic Failures (OWASP #2)
- **HIGH**: Database passwords stored in plain text configuration
- **HIGH**: No encryption for sensitive data in transit/rest
- **HIGH**: No password hashing mechanisms
- **HIGH**: No secure random token generation
- **MEDIUM**: Default PostgreSQL credentials in development

#### 3. Injection Vulnerabilities (OWASP #3)
- **IMPLEMENTED**: Comprehensive SQL injection prevention testing
- **PROTECTION**: SQLAlchemy ORM provides parameterized queries
- **VALIDATED**: Malicious input stored safely as literal text
- **TESTED**: Parameter validation and database integrity verification
- **MEDIUM**: No NoSQL injection testing (not applicable currently)

#### 4. Insecure Design (OWASP #4)
- **HIGH**: No threat modeling performed
- **HIGH**: Missing security-by-design principles
- **HIGH**: No defense in depth architecture
- **MEDIUM**: No secure development lifecycle

#### 5. Security Misconfiguration (OWASP #5)
- **CRITICAL**: CORS configured to allow all origins ("*")
- **HIGH**: Debug mode potentially enabled in production
- **HIGH**: Default database credentials ("todopass")
- **HIGH**: No security headers implementation
- **HIGH**: Detailed error messages expose system information
- **MEDIUM**: No network security controls

#### 6. Vulnerable and Outdated Components (OWASP #6)
- **MEDIUM**: No automated vulnerability scanning
- **MEDIUM**: No dependency version management
- **MEDIUM**: External CDN dependencies (HTMX) without integrity checks
- **LOW**: Regular security updates not automated

#### 7. Identification and Authentication Failures (OWASP #7)  
- **CRITICAL**: No user identification system
- **CRITICAL**: No authentication failure handling
- **CRITICAL**: No account lockout mechanisms
- **CRITICAL**: No password policy enforcement

#### 8. Software and Data Integrity Failures (OWASP #8)
- **HIGH**: No integrity verification for external dependencies
- **HIGH**: No secure CI/CD pipeline verification
- **MEDIUM**: No code signing implementation
- **MEDIUM**: No tamper detection mechanisms

#### 9. Security Logging and Monitoring Failures (OWASP #9)
- **HIGH**: No security event logging (authentication failures, access violations)
- **HIGH**: No audit trails for sensitive operations
- **HIGH**: No alerting on suspicious activities
- **MEDIUM**: Request logging exists but lacks security context
- **MEDIUM**: No intrusion detection capabilities

#### 10. Server-Side Request Forgery (SSRF) (OWASP #10)
- **HIGH**: External image fetching without URL validation
- **HIGH**: No allowlist for external domains (picsum.photos)
- **HIGH**: Potential internal network access via image URLs
- **MEDIUM**: No timeout/rate limiting on external requests

### Additional Security Concerns

#### Cross-Site Scripting (XSS)
- **HIGH**: Inline JavaScript in HTML templates
- **HIGH**: Direct user input rendering without proper escaping
- **HIGH**: No Content Security Policy (CSP) headers
- **MEDIUM**: HTMX usage without XSS protection verification

#### Business Logic Vulnerabilities
- **HIGH**: No rate limiting on todo creation/modification
- **HIGH**: No size limits on todo content beyond 140 chars
- **HIGH**: No ownership verification between users and todos
- **MEDIUM**: No abuse prevention mechanisms

#### Information Disclosure
- **HIGH**: Detailed error messages reveal system architecture
- **HIGH**: Debug information potentially exposed in logs
- **HIGH**: Database schema information accessible
- **MEDIUM**: System fingerprinting via error responses

#### Denial of Service (DoS)
- **HIGH**: No rate limiting on API endpoints
- **HIGH**: No resource consumption limits
- **HIGH**: No request size limitations
- **MEDIUM**: Database connection pool exhaustion possible

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

| Risk Area | Current Coverage | Impact | Cloud Risk | Priority |
|-----------|------------------|---------|------------|----------|
| **IMMEDIATE FOR CLOUD DEPLOYMENT** |
| CORS Misconfiguration | None | Medium | High | **HIGH** |
| No Security Headers | None | Medium | High | **HIGH** |
| Rate Limiting Missing | None | High | High | **HIGH** |
| **HIGH PRIORITY FIXES** |
| SQL Injection | **IMPLEMENTED** | High | Medium | **COMPLETE** |
| XSS Vulnerabilities | None | High | Medium | **HIGH** |
| SSRF via Image Fetching | None | High | Medium | **HIGH** |
| Information Disclosure | None | Medium | High | **MEDIUM** |
| **COURSE PROJECT ACCEPTABLE** |
| No Authentication | None | Critical | Low* | **FUTURE** |
| No Authorization | None | Critical | Low* | **FUTURE** |
| Default Local Credentials | None | Low | Low | **LOW** |
| **OPERATIONAL CONCERNS** |
| Database Downtime | None | High | Medium | **MEDIUM** |
| Load/Concurrency | None | High | High | **MEDIUM** |
| Security Logging | Partial | Medium | Medium | **MEDIUM** |
| Container Limits | None | Medium | High | **MEDIUM** |

*Low risk for course project - single-user environment assumed

### Practical Security Risk Matrix

| Security Area | Local Dev Risk | Cloud Risk | Effort | Course Priority |
|---------------|----------------|------------|---------|-----------------|
| CORS Configuration | Low | **HIGH** | **LOW** | **IMMEDIATE** |
| Security Headers | Low | **HIGH** | **LOW** | **IMMEDIATE** |
| Rate Limiting | Low | **HIGH** | **MEDIUM** | **HIGH** |
| SQL Injection | Low | **HIGH** | **LOW** | **COMPLETE** |
| XSS Prevention | Low | **HIGH** | **LOW** | **HIGH** |
| Authentication | Low | High | **HIGH** | **FUTURE** |
| SSRF Protection | Low | **MEDIUM** | **LOW** | **MEDIUM** |

## Recommended Test Additions

### IMMEDIATE PRIORITY - Cloud Deployment Readiness

#### Security Configuration Tests
```python
# Test CORS security for cloud deployment
async def test_cors_configuration_for_production():
    """Test that CORS is properly configured for production."""
    response = await test_client.options("/todos")
    cors_header = response.headers.get("access-control-allow-origin")
    
    # For course project, should allow specific domains, not wildcard
    if os.getenv("ENVIRONMENT") == "production":
        assert cors_header != "*"
        # Should be specific domains like:
        # "https://todo.your-cluster.azure.com"
        # "http://todo-app-fe:8000"

# Test security headers for cloud deployment
async def test_security_headers_present():
    """Test presence of basic security headers."""
    response = await test_client.get("/todos")
    headers = response.headers
    
    # Basic security headers for cloud deployment
    assert "x-content-type-options" in headers
    assert "x-frame-options" in headers  
    # Note: HSTS only needed if HTTPS is terminated at app level
```

#### Rate Limiting Tests
```python
# Test basic rate limiting
async def test_rate_limiting_prevents_abuse():
    """Test that rapid requests are throttled."""
    # This is important for cloud deployment
    tasks = []
    for i in range(50):  # Reduced from 100 for course project
        task = test_client.post("/todos", json={"text": f"Test {i}"})
        tasks.append(task)
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Should have some rate limiting mechanism
    successful = [r for r in responses if hasattr(r, 'status_code') and r.status_code == 201]
    # For course project: allow more requests but should have some limit
    assert len(successful) < 50, "Should have some rate limiting in place"
```

### HIGH PRIORITY - Input Security

#### SQL Injection Prevention Tests (IMPLEMENTED)
```python
# Test SQL injection prevention in todo text creation
async def test_sql_injection_in_todo_text_creation(test_client: AsyncClient):
    """Test that SQL injection attempts in todo text are safely handled."""
    malicious_inputs = [
        "'; DROP TABLE todos; --",
        "1' OR '1'='1",
        "'; DELETE FROM todos--",
        "' UNION SELECT * FROM todos--",
        "'; INSERT INTO todos (text) VALUES ('hacked'); --",
    ]
    
    for malicious_input in malicious_inputs:
        response = await test_client.post("/todos", json={"text": malicious_input})
        
        # SQLAlchemy ORM protects us - verify safe handling
        assert response.status_code in [201, 400, 422]
        
        if response.status_code == 201:
            todo_id = response.json()["id"]
            get_response = await test_client.get(f"/todos/{todo_id}")
            assert get_response.status_code == 200
            # Text stored as-is, not executed
            assert get_response.json()["text"] == malicious_input

# Test SQL injection prevention in ID parameters
async def test_sql_injection_in_todo_id_parameters(test_client: AsyncClient):
    """Test SQL injection protection in URL parameters."""
    malicious_ids = [
        "1'; DROP TABLE todos; --",
        "1 OR 1=1",
        "1; DELETE FROM todos",
    ]
    
    for malicious_id in malicious_ids:
        get_response = await test_client.get(f"/todos/{malicious_id}")
        assert get_response.status_code in [404, 422]  # Safe rejection

# Test database stability under injection attacks  
async def test_database_stability_under_injection_attacks(test_client: AsyncClient):
    """Test database remains stable under sustained attacks."""
    # Multiple dangerous payloads processed safely
    # Database integrity maintained throughout
```

#### Practical SQL Injection Tests  
```python
# Test SQL injection prevention (realistic for course project)
async def test_sql_injection_prevention():
    """Test that SQL injection attempts are safely handled."""
    malicious_inputs = [
        "'; DROP TABLE todos; --",
        "1' OR '1'='1",
        "'; DELETE FROM todos--",
    ]
    
    for malicious_input in malicious_inputs:
        response = await test_client.post("/todos", json={"text": malicious_input})
        
        # SQLAlchemy ORM should protect us, but verify:
        # 1. Request doesn't crash the server
        assert response.status_code in [201, 400, 422]
        
        # 2. If accepted, data is stored safely
        if response.status_code == 201:
            todo_id = response.json()["id"]
            get_response = await test_client.get(f"/todos/{todo_id}")
            assert get_response.status_code == 200
            # Text should be stored as-is, not executed
            assert get_response.json()["text"] == malicious_input
```

#### XSS Prevention Tests
```python
# Test XSS prevention for course project
async def test_basic_xss_prevention():
    """Test that XSS payloads are safely stored."""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "javascript:alert('xss')",
    ]
    
    for payload in xss_payloads:
        response = await test_client.post("/todos", json={"text": payload})
        assert response.status_code == 201
        
        # Backend should store data safely (frontend handles rendering)
        todo_id = response.json()["id"]
        get_response = await test_client.get(f"/todos/{todo_id}")
        stored_text = get_response.json()["text"]
        # Data stored as-is - frontend responsible for safe rendering
        assert stored_text == payload
```

### MEDIUM PRIORITY - Operational Security

#### Input Validation Tests
```python
# Test input size limits
async def test_input_size_limits():
    """Test that oversized inputs are rejected."""
    # Test beyond 140 char limit
    large_text = "A" * 1000
    response = await test_client.post("/todos", json={"text": large_text})
    assert response.status_code == 422  # Validation error
    
    # Test empty inputs
    response = await test_client.post("/todos", json={"text": ""})
    assert response.status_code == 422

# Test malformed requests
async def test_malformed_request_handling():
    """Test that malformed requests are handled gracefully."""
    # Missing required fields
    response = await test_client.post("/todos", json={})
    assert response.status_code == 422
    
    # Invalid JSON structure
    response = await test_client.post("/todos", json={"invalid": "structure"})
    assert response.status_code == 422
```

#### Error Handling Tests
```python
# Test error information disclosure
async def test_error_responses_dont_leak_info():
    """Test that error responses don't expose system details."""
    # Test with non-existent todo
    response = await test_client.get("/todos/999999")
    assert response.status_code == 404
    
    error_detail = response.json().get("detail", "")
    # Should not expose database info, file paths, etc.
    assert "database" not in error_detail.lower()
    assert "postgres" not in error_detail.lower()
    assert "/" not in error_detail  # No file paths
```

### FUTURE CONSIDERATIONS (Post-Course)

#### Authentication Framework Tests
```python
# Placeholder for future authentication implementation
async def test_authentication_framework():
    """Future: Test authentication when implemented."""
    # This would be implemented if the course project evolved to multi-user
    pass

# Placeholder for authorization tests
async def test_user_data_isolation():
    """Future: Test that users can only access their own data."""
    # Would require user accounts and session management
    pass
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
- Integration tests: ~1.5 seconds (with PostgreSQL)  
- Total suite: ~1.6 seconds (75 tests)
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
- **SQL injection prevention: Comprehensive security testing**

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

**Status**: Strong foundation for development and basic deployment. **SQL injection protection implemented and validated**. Priority security fixes needed for cloud deployment: CORS configuration, basic security headers, rate limiting, and input validation. Authentication can be addressed in future iterations as the project scales beyond single-user course demonstration.

