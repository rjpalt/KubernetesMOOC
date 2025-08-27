#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

# E2E Test Script - Local Docker Compose
# Builds and runs the entire application stack in Docker Compose, 
# executes E2E tests against it, and automatically cleans up.

echo "Running E2E tests against local Docker Compose stack..."

cd "$ROOT"

# Ensure we're starting clean
echo "Cleaning up any existing containers..."
make compose-down 2>/dev/null || true

# Start the application stack
echo "Starting application stack..."
make compose-up &
COMPOSE_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Cleaning up..."
    kill $COMPOSE_PID 2>/dev/null || true
    make compose-down 2>/dev/null || true
}
trap cleanup EXIT

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Run E2E tests
echo "Running E2E tests..."
cd course_project/tests/e2e

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Playwright dependencies..."
    npm ci
    npx playwright install --with-deps
fi

# Run tests against local stack
E2E_BASE_URL="http://localhost:8000" npx playwright test

echo "E2E tests completed successfully!"
