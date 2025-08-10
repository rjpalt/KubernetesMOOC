#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

BE_COMPOSE_FILE="docker-compose.dev.yml"

echo "[scripts/db-down.sh] Wrapper -> docker compose -f course_project/todo-backend/${BE_COMPOSE_FILE} down"
cd "$ROOT/course_project/todo-backend"
exec docker compose -f "$BE_COMPOSE_FILE" down
