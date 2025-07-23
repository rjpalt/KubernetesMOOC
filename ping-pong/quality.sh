#!/bin/bash

# Code quality script for ping-pong project
# Runs import sorting, formatting, and linting

set -e  # Exit on any error

echo "🔧 Running code quality checks..."

echo "📦 Sorting imports with isort..."
uv run --active isort .

echo "🎨 Formatting code with black..."
uv run --active black .

echo "🔍 Linting with flake8..."
uv run --active flake8 .

echo "✅ Code quality checks completed successfully!"
