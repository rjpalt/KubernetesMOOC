#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

TAG="${1-}"
if [ -z "$TAG" ]; then
  echo "Error: TAG is required"
  echo "Usage: make build-images TAG=vX.Y.Z"
  exit 1
fi

echo "[scripts/build-images.sh] Wrapper -> $ROOT/course_project/build-images.sh $TAG"
cd "$ROOT/course_project"
exec ./build-images.sh "$TAG"
