# Project-wide Testing Overview

Purpose: single source for testing strategy across services, including E2E.

Canonical service plans
- Backend: course_project/todo-backend/tests/TEST_PLAN.md
- Frontend: course_project/todo-app/TEST_PLAN.md (to be added)

Test categories
- Unit: fast, isolated, no external services
- Integration: service APIs with real dependencies (e.g., Postgres for backend)
- Security: targeted checks (e.g., injection, headers) where applicable
- End-to-End (E2E): user-centric flows across FE+BE using Playwright

Environments
- Local: developer machine, DB via backend compose
- CI: GitHub Actions; DB and dependencies provisioned per workflow; mirrors local behavior where possible
- Feature Branch: Live Kubernetes environments for remote E2E testing

End-to-End tests (Implemented)
- Location: course_project/tests/e2e/
- Tools: Playwright
- Independence: E2E runs independently of FE/BE unit/integration tests and can target any environment.

Command references
- Backend tests: make test-be
- Frontend tests: make test-fe
- All unit/integration tests: make test
- E2E tests (local): make test-e2E-local
- E2E tests (remote): TARGET_URL=<your-url> make test-e2e-remote

Principles
- Single canonical doc per service; top-level index links, no duplication
- Keep tests environment-aware and deterministic
- Prefer async-friendly patterns in Python backend (see backend TEST_PLAN)
