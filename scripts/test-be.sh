#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

# Function to check if database containers are running
check_database_containers() {
    echo "Checking database containers..."
    
    local postgres_running=false
    local postgres_test_running=false
    
    # Check if todo_postgres_dev is running
    if docker ps --filter "name=todo_postgres_dev" --filter "status=running" | grep -q todo_postgres_dev; then
        postgres_running=true
    fi
    
    # Check if todo_postgres_test is running  
    if docker ps --filter "name=todo_postgres_test" --filter "status=running" | grep -q todo_postgres_test; then
        postgres_test_running=true
    fi
    
    if [ "$postgres_running" = true ] && [ "$postgres_test_running" = true ]; then
        echo "Database containers are running"
        return 0
    else
        echo ""
        echo "Database containers are not running!"
        echo ""
        echo "   Missing containers:"
        [ "$postgres_running" = false ] && echo "   - todo_postgres_dev (development database)"
        [ "$postgres_test_running" = false ] && echo "   - todo_postgres_test (test database)"
        echo ""
        echo "   To start the database containers:"
        echo "   make db-up"
        echo ""
        echo "   To check container status:"
        echo "   docker ps --filter 'name=todo_postgres'"
        echo ""
        return 1
    fi
}

echo "Running Backend Tests..."
echo ""

# Check database containers first
check_database_containers || exit 1
echo ""

cd "$ROOT/course_project/todo-backend"

# Install dependencies if needed
echo "Installing dependencies..."
uv sync --group dev

# Run tests
echo "Running backend tests..."
uv run pytest tests/ -v

echo ""
echo "Backend tests completed!"
