#!/bin/bash

# Local development script for auth-proxy-sidecar
set -e

echo "🚀 Setting up auth-proxy-sidecar for local development..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "📦 Installing dependencies..."
uv sync --group dev

echo "🔍 Running quality checks..."
./quality.sh

echo "📋 Development environment ready!"
echo ""
echo "Available commands:"
echo "  uv run python app.py          # Run the application"
echo "  uv run pytest                 # Run tests"
echo "  uv run ruff check .           # Check code quality"
echo "  uv run ruff format .          # Format code"
echo "  ./quality.sh                  # Run all quality checks"
echo "  ./build.sh                    # Build multi-arch Docker images"
echo "  ./build.sh --test             # Build and test ARM64 image locally"
echo "  ./build-and-push.sh           # Build and push to kubemooc.azurecr.io"
echo ""
echo "🔄 Dependency Management:"
echo "  - Edit dependencies in pyproject.toml"
echo "  - Run build scripts to auto-export simple requirements.txt"
echo "  - No manual sync required between dependency files"
echo ""
echo "🏥 Health check: http://localhost:8080/health"
echo "🔗 Query proxy: http://localhost:8080/api/v1/query"
echo ""
echo "⚠️  Note: Azure credentials must be configured for the app to start successfully."
