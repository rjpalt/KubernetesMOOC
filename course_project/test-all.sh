#!/bin/bash

# Run all tests (backend + frontend)
# Usage: ./test-all.sh

set -e  # Exit on any error

# Function to check if database containers are running
check_database_containers() {
    echo "🔍 Checking database containers..."
    
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
        echo "✅ Database containers are running"
        return 0
    else
        echo ""
        echo "⚠️  Database containers are not running!"
        echo ""
        echo "   Missing containers:"
        [ "$postgres_running" = false ] && echo "   - todo_postgres_dev (development database)"
        [ "$postgres_test_running" = false ] && echo "   - todo_postgres_test (test database)"
        echo ""
        echo "   To start the database containers:"
        echo "   cd todo-backend && docker compose -f docker-compose.dev.yml up -d"
        echo ""
        echo "   To check container status:"
        echo "   docker ps --filter 'name=todo_postgres'"
        echo ""
        echo "   To check container health:"
        echo "   docker compose -f todo-backend/docker-compose.dev.yml ps"
        echo ""
        return 1
    fi
}

echo "🧪 Running All Tests..."
echo ""

# Check database containers first
check_database_containers || exit 1
echo ""

# Backend tests
echo "🔧 Testing Backend Service..."
echo ""
cd todo-backend

echo "📦 Installing backend dependencies..."
uv sync --group dev

echo "🔍 Running backend tests..."
uv run pytest tests/ -v

echo ""
echo "✅ Backend tests completed!"
echo ""

# Frontend tests  
cd ../todo-app
echo "🌐 Testing Frontend Service..."
echo ""

echo "📦 Installing frontend dependencies..."
uv sync --group dev

echo "🔍 Running frontend tests..."
uv run pytest tests/ -v

echo ""
echo "✅ Frontend tests completed!"

# Summary
cd ..
echo ""
echo "🎉 All tests completed successfully!"
echo "   Backend: 27 tests"
echo "   Frontend: Contract and integration tests"
echo "   Both services tested independently"
