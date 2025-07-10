#!/bin/bash

# Set TAG environment variable (defaults to 'latest' if not provided)
export TAG=${TAG:-latest}

echo "🧪 Testing Docker Compose setup with TAG=${TAG}..."

# Build and start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 5

# Test the generator endpoint
echo "🔍 Testing log generator..."
curl -s http://localhost:8000/health | grep -q "ok" && echo "✅ Generator health check passed" || echo "❌ Generator health check failed"
curl -s http://localhost:8000/ | grep -q "timestamp" && echo "✅ Generator API working" || echo "❌ Generator API failed"

# Test the log server endpoint
echo "🔍 Testing log server..."
curl -s http://localhost:8001/health | grep -q "ok" && echo "✅ Log server health check passed" || echo "❌ Log server health check failed"

# Wait a bit for logs to be generated
echo "⏳ Waiting for logs to be generated..."
sleep 10

# Test log reading
echo "🔍 Testing log file sharing..."
LOG_CONTENT=$(curl -s http://localhost:8001/logs)
if echo "$LOG_CONTENT" | grep -q "Application started"; then
    echo "✅ Log server can read shared logs"
    echo "📝 Sample log content:"
    echo "$LOG_CONTENT" | tail -3
else
    echo "❌ Log server cannot read shared logs"
    echo "Debug: Log content received:"
    echo "$LOG_CONTENT"
fi

echo ""
echo "🔍 Container status:"
docker-compose ps

echo ""
echo "💡 Commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop: docker-compose down -v"
echo "  Rebuild: docker-compose up --build -d"
