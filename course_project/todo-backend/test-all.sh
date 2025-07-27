#!/bin/bash
# Comprehensive test runner for todo-backend
# Demonstrates container-based testing approach for Kubernetes readiness

set -e  # Exit on any error

echo "🧪 Todo Backend Test Suite"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "tests" ]; then
    print_error "Must be run from todo-backend directory"
    exit 1
fi

print_status "Running from todo-backend directory"

# 2. Check Docker availability
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

print_status "Docker is available"

# 3. Ensure test database is running
echo ""
echo "🐳 Ensuring test database is running..."
echo "======================================"

# The tests will handle starting the database automatically via conftest.py
# But let's verify Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

print_status "Docker daemon is running"

# 4. Install/update dependencies
echo ""
echo "📦 Installing dependencies..."
echo "============================="

if command -v uv &> /dev/null; then
    print_status "Using uv for dependency management"
    uv sync --group dev
else
    print_warning "uv not found, falling back to pip"
    pip install -e ".[dev]"
fi

print_status "Dependencies installed"

# 5. Run linting first
echo ""
echo "🔍 Running code quality checks..."
echo "================================="

if command -v ruff &> /dev/null; then
    echo "Running ruff check..."
    if ruff check .; then
        print_status "Ruff check passed"
    else
        print_warning "Ruff found issues (continuing with tests)"
    fi
    
    echo "Running ruff format check..."
    if ruff format --check .; then
        print_status "Code formatting is correct"
    else
        print_warning "Code formatting issues found (continuing with tests)"
    fi
else
    print_warning "Ruff not available, skipping linting"
fi

# 6. Run unit tests
echo ""
echo "🧪 Running unit tests..."
echo "========================"

if uv run python -m pytest tests/unit/ -v --tb=short; then
    print_status "Unit tests passed"
else
    print_error "Unit tests failed"
    exit 1
fi

# 7. Run integration tests
echo ""
echo "🔗 Running integration tests..."
echo "==============================="

if uv run python -m pytest tests/integration/ -v --tb=short; then
    print_status "Integration tests passed"
else
    print_error "Integration tests failed"
    exit 1
fi

# 8. Run all tests with coverage
echo ""
echo "📊 Running full test suite with coverage..."
echo "==========================================="

if uv run python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v; then
    print_status "Full test suite passed with coverage"
else
    print_error "Full test suite failed"
    exit 1
fi

# 9. Summary
echo ""
echo "🎉 All tests passed!"
echo "===================="
echo ""
echo "Key learnings demonstrated:"
echo "- ✅ Container-based database testing"
echo "- ✅ Async test patterns"
echo "- ✅ Database isolation between tests"
echo "- ✅ Automatic test database lifecycle management"
echo "- ✅ Integration testing with real database"
echo "- ✅ Kubernetes-ready testing approach"
echo ""
echo "Next steps for Kubernetes deployment:"
echo "- Database connection configuration via secrets"
echo "- Health check endpoint testing"
echo "- Container image testing"
echo "- Kubernetes manifest testing"
echo ""
print_status "Test suite complete!"
