#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

echo "[scripts/azure-stop.sh] Wrapper -> $ROOT/azure-stop.sh"
exec "$ROOT/azure-stop.sh" "$@"
