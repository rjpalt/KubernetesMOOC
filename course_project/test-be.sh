#!/bin/bash

# Run backend tests
# Usage: ./test-be.sh

set -e  # Exit on any error

echo "🧪 Running Backend Tests..."
echo ""

cd todo-backend

# Install dependencies if needed
echo "📦 Installing dependencies..."
uv sync --group dev

# Run tests
echo "🔍 Running backend tests..."
uv run pytest tests/ -v

echo ""
echo "✅ Backend tests completed!"
