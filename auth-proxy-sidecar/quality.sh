#!/bin/bash

# Quality checks for auth-proxy-sidecar
set -e

echo "🔍 Running code quality checks..."

echo "📝 Checking code formatting with ruff..."
uv run ruff check .

echo "🎨 Checking code formatting..."
uv run ruff format --check .

echo "🧪 Running tests..."
uv run pytest tests/ -v

echo "✅ All quality checks passed!"
