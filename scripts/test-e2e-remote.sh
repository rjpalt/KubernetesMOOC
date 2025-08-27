#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

# E2E Test Script - Remote URL
# Runs E2E tests against any deployed environment (e.g., feature branch in Kubernetes)

TARGET_URL=$1

if [ -z "$TARGET_URL" ]; then
    echo "Error: TARGET_URL is required"
    echo "Usage: $0 <target_url>"
    echo "Example: $0 http://branch-name.23.98.101.23.nip.io/"
    exit 1
fi

echo "Running E2E tests against remote URL: $TARGET_URL"

cd "$ROOT/course_project/tests/e2e"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Playwright dependencies..."
    npm ci
    npx playwright install --with-deps
fi

# Run tests against remote URL
echo "Executing Playwright tests..."
E2E_BASE_URL="$TARGET_URL" npx playwright test

echo "E2E tests completed successfully!"
