# Todo Frontend - Testing Plan

Single source of truth for the frontend testing strategy. Backend and project-wide references:
- Project overview: `course_project/TESTING_OVERVIEW.md`
- Backend test plan: `course_project/todo-backend/tests/TEST_PLAN.md`

## Scope & goals
- Verify UI views/templates, routing, and client-side behavior that the frontend service owns
- Validate security headers and XSS prevention for all frontend responses
- Ensure integration with the backend is correct via mocks/contract checks (frontend tests do not require a live backend)
- Keep tests fast, deterministic, and environment-aware (dev vs prod)

## Test structure
```
course_project/todo-app/tests/
├── unit/                      # Pure unit tests (no I/O)
│   ├── test_templates.py      # Template rendering/sanitization
│   ├── test_routes.py         # View/route handlers (logic only)
│   ├── test_utils.py          # Helpers & formatters
│   └── ...
├── integration/               # HTTP-level tests with in-process app
│   ├── test_http_endpoints.py # GET/POST of pages & assets
│   ├── test_backend_contracts.py # Contract/mocks to backend API
│   └── ...
├── security/                  # Security responses & headers
│   ├── test_xss_prevention.py # Stored/reflected XSS defenses
│   └── test_security_headers.py # CSP, X-Frame-Options, etc.
└── conftest.py                # Fixtures (app/test client, settings)
```

Status: skeleton established. Update test counts as suites land.

## Running tests

Prerequisites
```bash
cd course_project/todo-app
uv sync --group dev
```

Quick commands
```bash
# Recommended wrappers
cd .. && ./test-fe.sh

# Or run manually
uv run pytest tests/ -v
```

Coverage
```bash
uv run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Categories and coverage

### Unit tests (fastest)
- Template rendering: escapes, HTML structure, conditional blocks
- Routing/view logic: parameter handling and branching (no network)
- Utilities: formatting, parsers, mappers
- Snapshot tests allowed for HTML snippets (stable selectors only)

### Integration tests (in-process HTTP)
- App bootstraps and serves core routes (200/302/404)
- Static assets served with correct content types
- Backend interactions mocked:
  - Validate requests formed as expected
  - Validate basic success/error paths
- Contract checks to backend API (OpenAPI fixtures or mock responses)

### Security tests
- XSS prevention across pages/components (stored/reflected/encoded payloads)
- Security headers present and correct on all endpoints
  - Content-Security-Policy (CSP)
  - X-Content-Type-Options, X-Frame-Options, Referrer-Policy
  - Content-Type enforcement
- Error responses do not leak internals; debug info only in development

### Accessibility (optional, recommended)
- Basic a11y smoke checks (headings, titles, labels)
- Can be run with lightweight linters or Playwright a11y scans later

## Async and test client
If the frontend is an ASGI app, use an in-process client (e.g., httpx.AsyncClient + ASGITransport) for integration tests to avoid network flakiness. Keep fixtures similar to backend patterns for consistency.

Example fixture sketch (for reference only):
```python
@pytest_asyncio.fixture
aasync def test_client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
```

## Environments
- Development: may include helpful debug_info blocks in error pages/responses
- Production: must return sanitized errors and strict headers
- Tests should assert environment-appropriate behavior

## CI integration
- Frontend tests run in PRs that touch `course_project/todo-app/**`
- Coverage reported as CI artifact (align with backend process)

## Troubleshooting
- Import errors: run from `course_project/todo-app` and ensure `uv sync --group dev`
- Flaky tests: prefer in-process ASGI client; avoid network/http server processes
- Snapshots: update only with conscious review; document reasoning in PR

## Roadmap / planned additions
- Strengthen contract tests against backend OpenAPI spec
- Add XSS payload corpus similar to backend security tests
- Introduce lightweight a11y checks
- Align test output format with project logging/observability goals
