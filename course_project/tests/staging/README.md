# L2 Staging Integration Tests

Service-level integration tests for validating the staging environment infrastructure and backend API functionality.

## Overview

**Purpose**: Validate backend services, database connectivity, and Kubernetes networking in the staging environment before production promotion.

**Test Level**: L2 (Service Integration)
- Tests backend API endpoints directly (no browser)
- Validates infrastructure (Gateway, DBaaS, service discovery)
- Runs against live staging environment in AKS

**Test Count**: 6 tests across 3 modules
**Execution Time**: ~40 seconds total
**Technology**: pytest + httpx AsyncClient

## Test Inventory

### Backend Health Tests (2 tests)
**File**: `test_backend_health.py`
- `test_health_endpoint_returns_200_with_service_name` - Validates `/be-health` endpoint returns correct service name
- `test_health_endpoint_includes_todo_count` - Validates health endpoint includes todo count field

**Can run locally**: ✅ Yes (health endpoint accessible via Gateway)

### Database Integration Tests (2 tests)
**File**: `test_database_integration.py`
- `test_create_todo_persists_in_database` - Validates todo creation persists in DBaaS
- `test_read_todo_retrieves_persisted_data` - Validates todo retrieval from DBaaS

**Can run locally**: ❌ No (Azure DBaaS not publicly accessible)

### Service Discovery Tests (2 tests)
**File**: `test_service_discovery.py`
- `test_backend_service_reachable_via_gateway` - Validates Gateway HTTPRoute to backend
- `test_backend_can_query_database` - Validates backend-to-database connectivity

**Can run locally**: ❌ No (Kubernetes networking only available in AKS)

## Prerequisites

### Environment Variables

**Required**:
```bash
export STAGING_BACKEND_URL="https://d9hqaucbbyazhfem.fz53.alb.azure.com/project"
```

**Note**: Update the URL to match your actual staging environment Gateway address.

### Dependencies

Install test dependencies:
```bash
cd course_project/tests/staging
pip install -r requirements.txt
```

Or using uv (recommended):
```bash
uv pip install -r requirements.txt
```

## Running Tests

### Full Test Suite (CI Environment Required)

```bash
# Set staging URL
export STAGING_BACKEND_URL="https://your-staging-backend.example.com"

# Run all tests
pytest -v

# Run with HTML report
pytest -v --html=report.html --self-contained-html
```

### Health Tests Only (Can Run Locally)

Health tests can run from your local machine if staging Gateway is accessible:

```bash
# Set staging URL
export STAGING_BACKEND_URL="https://d9hqaucbbyazhfem.fz53.alb.azure.com/project"

# Run only health tests
pytest test_backend_health.py -v

# Expected output:
# test_backend_health.py::test_health_endpoint_returns_200_with_service_name PASSED
# test_backend_health.py::test_health_endpoint_includes_todo_count PASSED
```

### Syntax Validation (Local Development)

During development, you can validate Python syntax locally without executing tests:

```bash
# Check syntax for all test files
python -m py_compile conftest.py
python -m py_compile test_backend_health.py
python -m py_compile test_database_integration.py
python -m py_compile test_service_discovery.py
```

## Database Connectivity Limitation

**CRITICAL**: Azure Database for PostgreSQL (DBaaS) is **not publicly accessible**.

**What this means**:
- Database integration tests **cannot run from local machine**
- Service discovery tests **cannot run from local machine**
- Tests **must execute in GitHub Actions workflow** (inside AKS network)

**Why**:
- DBaaS is configured with private endpoint (no public IP)
- Backend connects to DBaaS via Azure Private Link
- Only pods inside AKS cluster can reach DBaaS

**Development workflow**:
1. ✅ Write tests locally (use IDE, syntax checking)
2. ✅ Run health tests locally (validate Gateway connectivity)
3. ❌ Cannot run database tests locally (DBaaS not accessible)
4. ✅ Push to CI for full test execution (GitHub Actions has AKS access)

## Test Data Management

### Unique ID Generation

All tests use timestamp-based unique IDs with random suffix to prevent collisions:

```python
# Pattern: prefix_timestamp_randomSuffix
# Example: test_todo_1704123456789_5432

todo_text = unique_id_generator("test_todo")
```

**Why**: Multiple tests running in parallel won't create duplicate data.

### Cleanup Procedures

**Every test cleans up its data**:

```python
# Create test data
create_response = await staging_client.post("/todos", json={"text": todo_text})
todo_id = create_response.json()["id"]

# ... test assertions ...

# Cleanup (REQUIRED)
delete_response = await staging_client.delete(f"/todos/{todo_id}")
assert delete_response.status_code == 204
```

**Why**: Prevents test data accumulation in staging environment.

## Test Patterns

### Async Testing

All tests use async/await pattern with httpx AsyncClient:

```python
@pytest.mark.asyncio
async def test_example(staging_client: AsyncClient):
    response = await staging_client.get("/endpoint")
    assert response.status_code == 200
```

### Assertion Context

All assertions include error context for debugging:

```python
# Good - includes context
assert response.status_code == 201, \
    f"Failed to create todo: {response.status_code}, {response.text}"

# Bad - no context
assert response.status_code == 201
```

### Fixtures

**`staging_backend_url`**: Reads `STAGING_BACKEND_URL` from environment
**`staging_client`**: AsyncClient configured with 30-second timeout
**`unique_id_generator`**: Function to generate unique test data IDs

## CI/CD Integration

### GitHub Actions Workflow

Tests run automatically in CI pipeline:

```yaml
- name: Run L2 Staging Tests
  env:
    STAGING_BACKEND_URL: ${{ steps.get-staging-url.outputs.url }}
  run: |
    cd course_project/tests/staging
    pytest -v --html=report.html
    
- name: Upload Test Report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: l2-test-report
    path: course_project/tests/staging/report.html
```

### When Tests Run

- After staging deployment completes
- After ArgoCD sync finishes
- Before production promotion eligibility

## Troubleshooting

### "STAGING_BACKEND_URL environment variable required"

**Problem**: Environment variable not set.

**Solution**:
```bash
export STAGING_BACKEND_URL="https://your-staging-backend.example.com"
echo $STAGING_BACKEND_URL  # Verify it's set
```

### "Connection refused" or timeout errors

**Problem**: Backend not accessible.

**Solutions**:
1. Verify staging URL is correct (check Gateway address)
2. Check if staging is deployed: `kubectl get pods -n staging`
3. Verify Gateway HTTPRoute is configured
4. For database tests: Must run in CI (not locally)

### Tests pass locally but fail in CI

**Problem**: Environment differences.

**Common causes**:
1. Environment variable not set in CI workflow
2. Staging URL differs between local and CI
3. Timing issues (wait for ArgoCD sync)
4. Cleanup not working properly

**Debug**:
1. Check CI logs for exact error message
2. Verify `STAGING_BACKEND_URL` in workflow YAML
3. Check if ArgoCD sync completed before tests run
4. Verify cleanup assertions pass

### Database tests fail with "connection error"

**Expected**: Database tests **cannot run locally**.

**Why**: Azure DBaaS is not publicly accessible (private endpoint only).

**Solution**: Tests must run in CI environment (GitHub Actions inside AKS network).

**Validation**: Use syntax checking locally, execution in CI:
```bash
# Local: Syntax only
python -m py_compile test_database_integration.py

# CI: Full execution (has DBaaS access)
# Tests run automatically in GitHub Actions
```

## Test Standards

All tests follow conventions defined in `docs/testing/staging-test-standards.md`:

- ✅ Test naming: `test_<action>_<expected_result>`
- ✅ Unique IDs: Timestamp + random suffix
- ✅ Cleanup: Delete test data after assertions
- ✅ Error context: Assertions include debugging info
- ✅ Timeouts: 30 seconds for API calls
- ✅ Documentation: Module and function docstrings
- ✅ Async: All tests use `@pytest.mark.asyncio`

## Related Documentation

- **Testing Standards**: `docs/testing/staging-test-standards.md`
- **QA Decision Log**: `tmp/qa_decision_log.md` (Decisions 1, 5)
- **Backend Test Patterns**: `course_project/todo-backend/tests/TEST_PLAN.md`
- **Task Instructions**: `tmp/epic_2_implementation_instructions_04_l2_core_tests.md`

## Success Criteria

- [ ] All 6 tests pass in CI environment
- [ ] Health tests pass locally (Gateway accessible)
- [ ] Database tests execute only in CI (expected limitation)
- [ ] Test data cleanup verified (no leftover todos)
- [ ] Test execution time < 60 seconds
- [ ] HTML report generated successfully

---

**Status**: Implementation complete
**Version**: 1.0
**Last Updated**: November 2, 2025
