# Project-wide Testing Overview

Purpose: single source for testing strategy across services, including E2E.

Canonical service plans
- Backend: course_project/todo-backend/tests/TEST_PLAN.md
- Frontend: course_project/todo-app/TEST_PLAN.md (to be added)

Test categories
- Unit: fast, isolated, no external services
- Integration: service APIs with real dependencies (e.g., Postgres for backend)
- Security: targeted checks (e.g., injection, headers) where applicable
- End-to-End (E2E): user-centric flows across FE+BE (tools TBD)

Environments
- Local: developer machine, DB via backend compose
- CI: GitHub Actions; DB and dependencies provisioned per workflow; mirrors local behavior where possible

End-to-End tests (TBD)
- Location: course_project/e2e/ (planned)
- Tools: Playwright/Cypress/pytest+httpx (decision pending)
- Independence: E2E runs independently of FE/BE unit/integration tests

Command references
- Backend tests: course_project/test-be.sh
- Frontend tests: course_project/test-fe.sh
- All tests: course_project/test-all.sh

Principles
- Single canonical doc per service; top-level index links, no duplication
- Keep tests environment-aware and deterministic
- Prefer async-friendly patterns in Python backend (see backend TEST_PLAN)
