#!/bin/bash

# Run all tests (backend + frontend)
# Usage: ./test-all.sh

set -e  # Exit on any error

echo "🧪 Running All Tests..."
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
uv sync --group dev --group test

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
