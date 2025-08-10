#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

echo "[scripts/quality.sh] Wrapper -> $ROOT/course_project/quality.sh $*"
cd "$ROOT/course_project"
exec ./quality.sh "$@"
