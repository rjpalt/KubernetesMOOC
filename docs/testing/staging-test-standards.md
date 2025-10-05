# Staging Test Standards

Central testing conventions and guidelines for implementing L2 and L3 tests in the staging environment. All AI test implementers must follow these standards to ensure consistency, quality, and maintainability.

## Purpose

This document defines:
- Test naming and organization conventions
- Test data patterns and cleanup procedures
- Assertion guidelines and timeout standards
- Error handling and retry strategies
- Documentation requirements

## Test Level Definitions

### L2 Tests (Service Integration)
**Purpose**: Validate backend API endpoints, infrastructure services (NATS, broadcaster), and service-to-service communication at the API level.

**Technology**: pytest (Python), AsyncClient for FastAPI

**Scope**:
- Backend API health endpoints
- Database connectivity and data persistence
- NATS message publishing from backend
- Broadcaster message consumption from NATS
- Broadcaster webhook delivery to external endpoints
- Service discovery and inter-service communication

**Out of Scope**:
- Frontend rendering (browser-based testing)
- User workflows (covered by L3)
- Backend unit tests (already tested in PR phase)

### L3 Tests (End-to-End)
**Purpose**: Validate complete user workflows from browser through full stack (frontend → backend → database).

**Technology**: Playwright (TypeScript/JavaScript), browser automation

**Scope**:
- User-facing CRUD operations
- Frontend rendering and HTMX interactions
- Frontend-to-backend communication
- Database persistence visible to users
- Error handling visible to users

**Out of Scope**:
- NATS message broker visibility (internal infrastructure)
- Broadcaster service visibility (internal infrastructure)
- Backend API endpoints not exposed through frontend

## Test Organization

### Directory Structure
```
course_project/tests/
├── e2e/                           # L3 End-to-End tests
│   ├── tests/
│   │   ├── smoke.spec.ts         # Existing: Basic smoke tests
│   │   ├── todo-crud.spec.ts     # Existing: CRUD workflows
│   │   └── todo-done-feature.spec.ts  # Existing: Feature tests
│   ├── playwright.config.ts      # Playwright configuration
│   └── global-setup.ts           # Global test setup
├── staging/                       # L2 Staging integration tests (NEW)
│   ├── conftest.py               # Pytest fixtures
│   ├── test_backend_health.py    # Health check tests
│   ├── test_database_integration.py  # Database tests
│   ├── test_nats_publishing.py   # NATS publishing tests
│   ├── test_broadcaster_consumption.py  # NATS consumption tests
│   └── test_webhook_delivery.py  # Webhook delivery tests
└── README.md                      # Test suite overview
```

### File Naming Conventions

**L2 Tests (pytest)**:
- Pattern: `test_<component>_<feature>.py`
- Examples:
  - `test_backend_health.py`
  - `test_database_integration.py`
  - `test_nats_publishing.py`
  - `test_broadcaster_consumption.py`
  - `test_webhook_delivery.py`

**L3 Tests (Playwright)**:
- Pattern: `<feature>-<description>.spec.ts`
- Examples:
  - `smoke.spec.ts`
  - `todo-crud.spec.ts`
  - `todo-done-feature.spec.ts`

**Individual Test Functions**:
- L2 Pattern: `test_<action>_<expected_result>`
- L3 Pattern: `test('<user action> should <expected result>')`
- Examples:
  - L2: `test_health_endpoint_returns_200_with_service_name()`
  - L3: `test('creating todo should persist in database')`

## Test Data Management

### Unique ID Generation

**Timestamp-Based IDs (REQUIRED)**:
All test data must use timestamp-based unique IDs to prevent collisions in parallel test execution.

```python
# L2 Python tests
import time

def generate_unique_id(prefix: str) -> str:
    """Generate unique ID with timestamp for test data."""
    timestamp = int(time.time() * 1000)  # Milliseconds
    return f"{prefix}_{timestamp}"

# Usage
todo_text = generate_unique_id("test_todo")
# Result: "test_todo_1704123456789"
```

```typescript
// L3 TypeScript tests
function generateUniqueId(prefix: string): string {
  const timestamp = Date.now();
  return `${prefix}_${timestamp}`;
}

// Usage
const todoText = generateUniqueId('test_todo');
// Result: "test_todo_1704123456789"
```

### Test Data Prefixes

Use consistent prefixes to identify test origin:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `test_todo_` | L2 backend CRUD tests | `test_todo_1704123456789` |
| `test_nats_` | L2 NATS message tests | `test_nats_1704123456789` |
| `test_webhook_` | L2 webhook delivery tests | `test_webhook_1704123456789` |
| `e2e_` | L3 end-to-end tests | `e2e_1704123456789` |
| `staging_` | Generic staging test data | `staging_1704123456789` |

### Cleanup Procedures

**L2 Tests**: Clean up test data in the same test function after assertions complete.

```python
async def test_create_todo_persists_in_database(staging_client: AsyncClient):
    # Arrange
    todo_text = generate_unique_id("test_todo")
    
    # Act
    response = await staging_client.post("/todos", json={"text": todo_text})
    
    # Assert
    assert response.status_code == 201
    created_todo = response.json()
    assert created_todo["text"] == todo_text
    
    # Cleanup
    todo_id = created_todo["id"]
    delete_response = await staging_client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 204  # Verify cleanup succeeded
```

**L3 Tests**: Use centralized cleanup helpers from `cleanup-helpers.ts`.

```typescript
import { cleanupTodo } from './cleanup-helpers';

test('creating todo should persist', async ({ page }) => {
  const todoText = generateUniqueId('e2e');
  
  // Create todo
  await page.fill('input[name="todo"]', todoText);
  await page.click('button[type="submit"]');
  
  // Assert
  await expect(page.locator(`text=${todoText}`)).toBeVisible();
  
  // Cleanup
  await cleanupTodo(page, todoText);
});
```

## Assertion Guidelines

### What to Assert

**L2 Tests**:
- HTTP status codes (200, 201, 204, 404, 500)
- Response body structure and required fields
- Data persistence (verify data exists after creation)
- Service health status
- Message delivery (NATS → Broadcaster → Webhook)
- Error messages for validation failures

**L3 Tests**:
- Visual elements visible to users
- User workflows complete successfully
- Data persists across page reloads
- Error messages displayed to users
- Frontend-backend data consistency

### What NOT to Assert

**L2 Tests**:
- Frontend rendering details
- Browser behavior
- CSS styling
- JavaScript execution

**L3 Tests**:
- Internal NATS messages
- Broadcaster service logs
- Database schema details
- Backend API response formats (unless visible to users)

### Assertion Examples

**L2 Health Check**:
```python
async def test_backend_health_returns_200(staging_client: AsyncClient):
    response = await staging_client.get("/be-health")
    
    # Status code
    assert response.status_code == 200
    
    # Response structure
    health_data = response.json()
    assert "service" in health_data
    assert "todo_count" in health_data
    
    # Value types
    assert isinstance(health_data["service"], str)
    assert isinstance(health_data["todo_count"], int)
    
    # Expected values
    assert health_data["service"] == "todo-backend"
    assert health_data["todo_count"] >= 0
```

**L3 CRUD Workflow**:
```typescript
test('complete todo CRUD workflow', async ({ page }) => {
  const todoText = generateUniqueId('e2e_crud');
  
  // CREATE
  await page.fill('input[name="todo"]', todoText);
  await page.click('button[type="submit"]');
  await expect(page.locator(`text=${todoText}`)).toBeVisible();
  
  // UPDATE (mark as done)
  await page.click(`button[data-todo-text="${todoText}"]`);
  await expect(page.locator(`text=${todoText}`).locator('..')).toHaveClass(/done/);
  
  // DELETE
  await page.click(`button[data-delete-todo="${todoText}"]`);
  await expect(page.locator(`text=${todoText}`)).not.toBeVisible();
});
```

## Timeout Standards

### Default Timeouts

| Operation | Timeout | Retry Strategy | Reason |
|-----------|---------|----------------|--------|
| ArgoCD sync wait | 5 minutes | Check every 10s | Deployment includes image pull |
| Health check endpoint | 2 minutes | Retry 3 times | Pods may be restarting |
| API calls (L2) | 30 seconds | No retry | Fast failure for debugging |
| Page loads (L3) | 30 seconds | Playwright default | Browser rendering time |
| Element visibility (L3) | 10 seconds | Playwright default | HTMX updates |
| Database queries | 10 seconds | No retry | Should be fast in staging |
| NATS message delivery | 15 seconds | Retry 2 times | Async message broker |
| Webhook delivery | 20 seconds | Retry 2 times | External network call |

### Timeout Configuration

**L2 Tests (pytest)**:
```python
import asyncio

async def wait_for_health(client: AsyncClient, timeout: int = 120) -> bool:
    """Wait for backend health with retry logic."""
    start_time = time.time()
    retry_count = 0
    max_retries = 3
    
    while time.time() - start_time < timeout:
        try:
            response = await client.get("/be-health", timeout=30.0)
            if response.status_code == 200:
                return True
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
        
        await asyncio.sleep(10)  # Check every 10 seconds
    
    raise TimeoutError(f"Health check failed after {timeout}s")
```

**L3 Tests (Playwright)**:
```typescript
// playwright.config.ts
export default defineConfig({
  timeout: 30000,        // 30s per test
  expect: {
    timeout: 10000,      // 10s for assertions
  },
  use: {
    actionTimeout: 10000, // 10s for user actions
  },
});

// In tests
await page.waitForSelector('text=Todo created', { timeout: 15000 });
```

## Error Handling

### Fail Fast vs Retry

**Fail Fast (No Retry)**:
- Configuration errors (missing environment variables)
- Invalid test data (malformed JSON)
- Test logic errors (assertion failures)
- Database schema mismatches

**Retry Allowed**:
- Network timeouts (transient failures)
- Service temporarily unavailable (503 errors)
- ArgoCD sync in progress
- Pod restarts during deployment

### Error Message Standards

**Good Error Messages**:
```python
# Include context
assert response.status_code == 200, \
    f"Health check failed: {response.status_code}, body: {response.text}"

# Include test data
assert todo_text in response.json()["items"], \
    f"Todo '{todo_text}' not found in: {response.json()['items']}"

# Include timing
assert elapsed_time < 5.0, \
    f"NATS message delivery took {elapsed_time:.2f}s (expected <5s)"
```

**Bad Error Messages**:
```python
# Vague
assert response.status_code == 200  # Fails with: "assert 500 == 200"

# No context
assert "todo" in data  # What todo? What data?

# No actionable info
assert success  # Why did it fail?
```

### Logging Standards

**L2 Tests**:
```python
import logging

logger = logging.getLogger(__name__)

async def test_nats_publishing(staging_client: AsyncClient):
    logger.info("Starting NATS publishing test")
    
    todo_text = generate_unique_id("test_nats")
    logger.info(f"Creating todo: {todo_text}")
    
    response = await staging_client.post("/todos", json={"text": todo_text})
    logger.info(f"Response status: {response.status_code}")
    
    if response.status_code != 201:
        logger.error(f"Failed to create todo: {response.text}")
    
    assert response.status_code == 201
```

**L3 Tests**:
```typescript
test('todo creation workflow', async ({ page }) => {
  console.log('Starting todo creation test');
  
  const todoText = generateUniqueId('e2e');
  console.log(`Creating todo: ${todoText}`);
  
  await page.fill('input[name="todo"]', todoText);
  await page.click('button[type="submit"]');
  
  const visible = await page.locator(`text=${todoText}`).isVisible();
  console.log(`Todo visible: ${visible}`);
  
  expect(visible).toBe(true);
});
```

## Test Fixtures and Setup

### L2 Fixtures (pytest)

**Required Fixtures** (define in `conftest.py`):

```python
import pytest
from httpx import AsyncClient

@pytest.fixture
def staging_backend_url() -> str:
    """Staging backend URL from environment."""
    import os
    url = os.getenv("STAGING_BACKEND_URL")
    assert url, "STAGING_BACKEND_URL environment variable required"
    return url

@pytest.fixture
async def staging_client(staging_backend_url: str) -> AsyncClient:
    """AsyncClient for staging backend API."""
    async with AsyncClient(base_url=staging_backend_url, timeout=30.0) as client:
        yield client

@pytest.fixture
def unique_id_generator():
    """Helper for generating unique test IDs."""
    def _generate(prefix: str) -> str:
        import time
        return f"{prefix}_{int(time.time() * 1000)}"
    return _generate
```

### L3 Fixtures (Playwright)

**Global Setup** (`global-setup.ts`):
```typescript
async function globalSetup() {
  // Wait for ArgoCD deployment
  await waitForDeployment();
  
  // Verify services healthy
  await verifyServicesHealthy();
}
```

**Test Fixtures** (built-in Playwright fixtures):
- `page`: Browser page context
- `context`: Browser context
- `request`: API request context (for cleanup)

## Parallel Execution

### Strategy

L2 and L3 tests run **in parallel** to minimize total execution time:

```yaml
# GitHub Actions workflow
jobs:
  test-l2:
    name: L2 Service Integration Tests
    runs-on: ubuntu-latest
    steps:
      - name: Run pytest L2 tests
        run: pytest course_project/tests/staging/ -v
  
  test-l3:
    name: L3 End-to-End Tests
    runs-on: ubuntu-latest
    steps:
      - name: Run Playwright E2E tests
        run: npm test -- course_project/tests/e2e/
```

**Execution Time**:
- L2 tests: ~4-5 minutes (12-15 tests)
- L3 tests: ~3-4 minutes (7 tests)
- Total: ~5 minutes (parallel) vs ~8 minutes (sequential)

### Test Isolation

**Data Isolation**:
- Use timestamp-based unique IDs (prevents collisions)
- Clean up test data after each test
- Avoid shared state between tests

**Resource Isolation**:
- L2 tests use AsyncClient (no browser)
- L3 tests use Playwright browser (no direct API calls)
- No shared fixtures between L2 and L3

## Documentation Requirements

### Test File Documentation

Each test file must include:

```python
"""
Test Module: Backend Health Checks

Purpose:
    Validate backend health endpoints return correct status and data.

Scope:
    - GET /be-health returns 200 with service name and todo count
    - Health endpoint responds within 2 seconds
    - Health data structure matches OpenAPI schema

Dependencies:
    - Backend service deployed to staging
    - Database accessible from backend
    
Environment Variables:
    - STAGING_BACKEND_URL: Backend API base URL
    
Test Count: 3 tests
Execution Time: ~30 seconds
"""
```

### Individual Test Documentation

Each test function must include:

```python
async def test_health_endpoint_returns_200_with_service_name(staging_client: AsyncClient):
    """
    Verify health endpoint returns 200 status with correct service name.
    
    Steps:
        1. Send GET request to /be-health
        2. Assert status code is 200
        3. Assert response contains "service" field
        4. Assert service name is "todo-backend"
    
    Expected Result:
        Health endpoint returns 200 with service name "todo-backend"
    """
    response = await staging_client.get("/be-health")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data["service"] == "todo-backend"
```

## CI/CD Integration

### Environment Variables

**Required for L2 Tests**:
```bash
STAGING_BACKEND_URL=https://your-staging-backend.example.com
STAGING_FRONTEND_URL=https://your-staging-frontend.example.com
```

**Required for L3 Tests**:
```bash
TARGET_URL=https://your-staging-frontend.example.com
```

### Artifact Collection

Tests must generate artifacts for debugging:

```yaml
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results-l2
    path: |
      test-reports/
      logs/
    retention-days: 7
```

### GitHub Actions Summary

Tests must update GitHub Actions summary:

```python
def update_github_summary(results: dict):
    """Update GitHub Actions summary with test results."""
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return
    
    with open(summary_file, "a") as f:
        f.write("## L2 Test Results\n\n")
        f.write(f"- Total: {results['total']}\n")
        f.write(f"- Passed: {results['passed']}\n")
        f.write(f"- Failed: {results['failed']}\n")
        f.write(f"- Duration: {results['duration']:.2f}s\n")
```

## Test Maintenance

### When to Update Tests

**Update Required**:
- API endpoint changes (new routes, parameters)
- Response format changes (new fields, removed fields)
- Feature additions (new user workflows)
- Timeout adjustments (performance improvements)

**Update NOT Required**:
- Backend implementation changes (internal refactoring)
- Database schema changes (if API unchanged)
- Deployment configuration changes
- Infrastructure updates (unless affecting test execution)

### Test Review Checklist

Before merging test code:

- [ ] Test names follow naming conventions
- [ ] Test data uses timestamp-based unique IDs
- [ ] Cleanup procedures implemented
- [ ] Assertions include error messages with context
- [ ] Timeouts configured appropriately
- [ ] Documentation complete (module + function)
- [ ] Tests pass in CI/CD pipeline
- [ ] No hardcoded URLs or credentials
- [ ] Test isolation verified (no shared state)
- [ ] Parallel execution compatible

## Reference Documentation

- Backend Test Plan: `course_project/todo-backend/tests/TEST_PLAN.md`
- Frontend Test Plan: `course_project/todo-app/TEST_PLAN.md`
- E2E Test Examples: `course_project/tests/e2e/tests/`
- Playwright Config: `course_project/tests/e2e/playwright.config.ts`
- Pytest Fixtures: `course_project/tests/staging/conftest.py`

## Questions and Support

For questions about testing standards:
1. Check this document first
2. Review existing test examples in the codebase
3. Consult the relevant TEST_PLAN.md for service-specific patterns
4. Ask the QA Lead for clarification

---

**Version**: 1.0
**Last Updated**: 2025-10-05
**Owner**: QA Lead