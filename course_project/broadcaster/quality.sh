#!/bin/bash

# Quality checks for broadcaster service (following auth-proxy-sidecar pattern)
set -e

echo "🔍 Running code quality checks for broadcaster..."

echo "📝 Checking code formatting with ruff..."
uv run ruff check src/ tests/

echo "🎨 Checking code formatting..."
uv run ruff format --check src/ tests/

echo "🧪 Running tests with coverage..."
WEBHOOK_URL="https://httpbin.org/post" uv run pytest tests/ -v --cov=src --cov-report=term-missing

echo "🔍 Type checking imports..."
WEBHOOK_URL="https://httpbin.org/post" uv run python -c "
import sys
try:
    from src.main import app
    from src.services.broadcaster_service import BroadcasterService
    from src.config.settings import settings
    print('✅ All imports successful')
    print(f'✅ Environment detection: {settings.deployment_environment}')
    print(f'✅ NATS URL: {settings.effective_nats_url}')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

echo "✅ All quality checks passed!"
