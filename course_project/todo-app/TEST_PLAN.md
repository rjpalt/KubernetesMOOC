# Todo Frontend - Testing Plan

Single source of truth for the frontend testing strategy.

References
- Project overview: `course_project/TESTING_OVERVIEW.md`
- Backend test plan: `course_project/todo-backend/tests/TEST_PLAN.md`

## Scope & goals
- Verify UI routes/templates and client-side behavior owned by the frontend.
- Validate security headers and XSS prevention on frontend responses.
- Verify contracts with backend via mocks; no live backend required for FE tests.
- Keep tests fast, deterministic, and environment-aware (dev vs prod).

## Test structure (current)
```
course_project/todo-app/tests/
├── fixtures/
│   ├── __init__.py
│   └── todo_fixtures.py
├── container/
│   └── test_container_basic.py          # Docker build/run smoke tests
├── integration/
│   ├── test_base_path.py                # API_BASE_PATH behavior and templated URLs
│   ├── test_health_checks.py            # /health JSON and performance
│   ├── test_html_responses.py           # Template rendering, graceful degradation
│   ├── test_image_endpoints.py          # /image, /image/info, /fetch-image
│   └── test_xss_security.py             # XSS and security headers (CSP, etc.)
├── unit/
│   ├── test_contracts.py                # Minimal contract checks with backend
│   ├── test_models.py                   # Placeholder for FE-owned models
│   └── test_todo_backend_client.py      # HTTP client behavior (httpx mocked)
└── conftest.py                          # TestClient + dependency overrides
```

## Running tests
Prerequisites
```bash
cd course_project/todo-app
uv sync --group dev
```

Quick commands
```bash
# Frontend tests (recommended wrapper)
cd .. && ./test-fe.sh

# Or run manually
uv run pytest tests/ -v
```

Coverage
```bash
uv run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Fixtures and test client
- `conftest.py` provides a FastAPI `TestClient` with dependency overrides:
  - `get_image_service` → Mock(ImageService)
  - `get_todo_backend_client` → AsyncMock(TodoBackendClient)
  - `get_templates` → real template instance
- Use `Mock`/`AsyncMock` to avoid network and file I/O; tests are in-process.

## Categories and current coverage

### Unit
- `test_todo_backend_client.py`: parses backend JSON, handles HTTP errors, timeouts, and connection failures; enforces URL formatting.
- `test_contracts.py`: minimal existence/shape checks for backend client methods and data format (hyphenated status like `not-done`).
- `test_models.py`: placeholder for FE-owned models (add image/template models as they evolve).

### Integration (in-process HTTP)
- `test_html_responses.py`: root page renders with graceful degradation when backend is unavailable; verifies image service usage and HTML structure.
- `test_base_path.py`: validates `API_BASE_PATH` env var behaviors; URL prefixes rendered into templates.
- `test_health_checks.py`: `/health` JSON shape and performance.
- `test_image_endpoints.py`: `/image`, `/image/info`, `/fetch-image` behavior and cache headers.

### Security
- `test_xss_security.py`: XSS defenses and security headers on HTML/JSON responses and CSP basics.

### Container (smoke)
- `container/test_container_basic.py`:
  - Docker image builds successfully.
  - Container starts and `/health` returns healthy.
  - Verifies Python version and core dependencies present.
  - Requires Docker; runs slower than unit/integration tests.

## Environment-aware behavior
- Local: developer machine; backend calls mocked; DB not required.
- CI: GitHub Actions; mirrors local behavior where possible; container tests may be slower.
- Base path: `API_BASE_PATH` influences rendered URLs; tests cover default and prefixed scenarios (via subprocess).
- Debug vs production: keep responses sanitized; no stack traces in standard responses.

## E2E scope (out of scope here)
- End-to-End tests are project-level and live under `course_project/e2e/` (planned). They run independently of FE/BE suites. See `course_project/TESTING_OVERVIEW.md`.

## CI integration
- FE tests run in PRs that touch `course_project/todo-app/**`.
- Coverage is generated as CI artifact (align with backend process).
- Container tests may be guarded/flagged if CI runtime is limited; document any skip markers when introduced.

## Troubleshooting
- Import errors: run from `course_project/todo-app` and ensure `uv sync --group dev`.
- Network flakiness: prefer in-process `TestClient`; avoid real HTTP servers in tests.
- Docker tests: ensure Docker is available and not rate-limited; increase timeouts if running on slow machines.

## Roadmap / planned additions
- Add FE-owned model tests (image/template view models) in `unit/`.
- Expand security header assertions (Referrer-Policy, Permissions-Policy) if enforced by the app.
- Add basic a11y smoke checks (optional) and snapshot tests for stable HTML fragments.
- Strengthen contract tests against backend OpenAPI (fixture-based) without live network.
