#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

echo "[scripts/compose-down.sh] Wrapper -> docker compose -f course_project/docker-compose.yaml down"
exec docker compose -f "$ROOT/course_project/docker-compose.yaml" down
