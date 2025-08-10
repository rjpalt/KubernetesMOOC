#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

echo "[scripts/db-up.sh] Wrapper -> $ROOT/course_project/todo-backend/start-db.sh"
cd "$ROOT/course_project/todo-backend"
exec ./start-db.sh "$@"
