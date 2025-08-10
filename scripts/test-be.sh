#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

echo "[scripts/test-be.sh] Wrapper -> $ROOT/course_project/test-be.sh"
cd "$ROOT/course_project"
exec ./test-be.sh "$@"
