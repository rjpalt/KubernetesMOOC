#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

echo "[scripts/clean.sh] Wrapper -> $ROOT/cleanup.sh"
exec "$ROOT/cleanup.sh" "$@"
