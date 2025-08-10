# Onboarding

This page points you to the canonical docs and commands. Keep it short.

- Read the repository map: docs/overview/repo-map.md
- Local development (DB, services, compose usage): docs/development/local-dev.md
- Scripts and what they do: docs/development/script-catalog.md
- Testing overview: docs/testing/index.md
- Backend testing details: course_project/todo-backend/tests/TEST_PLAN.md
- Frontend testing details: course_project/todo-app/TEST_PLAN.md (when added)
- Kubernetes manifests locations and scope: docs/platform/manifests-index.md

Quickstart
- Backend dev DB: use backend compose (documented in local-dev.md). A future make db-up wrapper will call it.
- Run backend tests: course_project/test-be.sh
- Run frontend tests: course_project/test-fe.sh
- Run all tests: course_project/test-all.sh
