#!/bin/bash

echo "🚀 Setting up broadcaster development environment..."

# Install dependencies
uv sync --group dev

echo "✅ Development dependencies installed"
echo ""
echo "📋 Available commands:"
echo "  • Code quality: ./quality.sh"
echo "  • Local build: ./build.sh"
echo "  • Push to registry: ./build-and-push.sh"
echo "  • Run tests: uv run pytest tests/ -v"
echo "  • Dev server: WEBHOOK_URL=https://httpbin.org/post uv run uvicorn src.main:app --reload --port 8002"
echo ""
echo "🔧 Environment variables needed:"
echo "  • WEBHOOK_URL=https://httpbin.org/post (for testing)"
echo "  • LOG_LEVEL=DEBUG (optional)"
