# Script catalog (draft)

Purpose: explain what each script does, where it lives, and the recommended wrapper name. Do not remove or move scripts now.

Top-level scripts
- azure-start.sh / azure-stop.sh — Start/stop Azure resources (ops). Wrapper: make azure-start / make azure-stop
- build-apps.sh — Build project apps. Wrapper: make build
- build-pp-and-lo.sh — Build ping-pong and log_output images. Wrapper: make build-pp-lo
- cleanup.sh — Clean local artifacts/containers. Wrapper: make clean

course_project/
- start-services.sh — Start common services for local dev. Wrapper: make dev
- test-all.sh — Run all course_project tests. Wrapper: make test
- test-be.sh — Run backend tests. Wrapper: make test-be
- test-fe.sh — Run frontend tests. Wrapper: make test-fe

course_project/todo-backend/
- docker-compose.dev.yml — Local Postgres (dev) and test DB. Source of truth for dev DB.
- start-dev.sh — Start backend in development mode. Wrapper: make be-dev
- start-db.sh — Start only DB via compose. Wrapper: make db-up
- test-all.sh — Run all backend tests. Wrapper: make test-be

ping-pong/
- quality.sh — Lint/test/quality for ping-pong. Wrapper: make pp-quality

log_output/
- docker-compose.yml — Local log server compose. Wrappers: make logserver-up / make logserver-down

Notes
- Deprecated or overlapping scripts will be marked here with “Use X instead.”
- Wrappers are optional; scripts remain callable directly.
