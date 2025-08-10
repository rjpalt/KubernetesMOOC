# Local development

Goals: one obvious way to start services locally, and a clear DB policy. No file moves.

Database and compose policy
- The canonical local Postgres for development is defined in course_project/todo-backend/docker-compose.dev.yml.
- Tests manage their own isolation; the dev DB is persistent and shared.
- For discoverability, we will provide a root-level task (e.g., make db-up) that calls the backend DB scripts without moving files.

How to start backend dev DB now
- Option A: from course_project/todo-backend using docker-compose.dev.yml (see start-db.sh if provided)
- Option B: use course_project/test-be.sh which handles DB for tests

Services
- Backend: see course_project/todo-backend/README.md and start-dev.sh
- Frontend: see course_project/todo-app/README.md
- Other utilities: see their respective READMEs

Environment
- Keep per-service .env/.env.example for now. Shared env folder is deferred.

Future wrappers (planned)
- make db-up / make db-down → delegate to backend DB compose
- make be-dev / make fe-dev → delegate to service scripts
