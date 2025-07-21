#!/bin/bash

# Start both todo services locally
# Usage: ./start-services.sh

set -e  # Exit on any error

echo "🚀 Starting Todo Microservices..."
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend service
echo "📦 Starting todo-backend (port 8001)..."
cd todo-backend
uv sync --quiet
uv run python -m src.main &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend service  
echo "🌐 Starting todo-app (port 8000)..."
cd todo-app
uv sync --quiet
uv run python -m src.main &
FRONTEND_PID=$!
cd ..

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 3

# Check if services are running
echo ""
echo "🔍 Checking service health..."

if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Backend running: http://localhost:8001/docs"
else
    echo "❌ Backend health check failed"
fi

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Frontend running: http://localhost:8000"
else
    echo "❌ Frontend health check failed"
fi

echo ""
echo "🎉 Services are running!"
echo "   Frontend: http://localhost:8000"
echo "   Backend API: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running and wait for signals
wait
