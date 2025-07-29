#!/bin/bash
# Script to start PostgreSQL containers for local development

echo "Starting PostgreSQL containers for development..."

# Start both development and test databases
docker-compose -f docker-compose.dev.yml up -d

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 5

# Check development database
echo "Checking development database..."
docker exec todo_postgres_dev pg_isready -U todouser -d todoapp
if [ $? -eq 0 ]; then
    echo "✅ Development database is ready"
else
    echo "❌ Development database failed to start"
    exit 1
fi

# Check test database
echo "Checking test database..."
docker exec todo_postgres_test pg_isready -U todouser -d todoapp_test
if [ $? -eq 0 ]; then
    echo "✅ Test database is ready"
else
    echo "❌ Test database failed to start"
    exit 1
fi

echo ""
echo "🎉 PostgreSQL setup complete!"
echo ""
echo "Development database: postgresql://todouser:todopass@localhost:5432/todoapp"
echo "Test database: postgresql://todouser:todopass@localhost:5433/todoapp_test"
echo ""
echo "To stop databases: docker-compose -f docker-compose.dev.yml down"
echo "To connect to dev DB: docker exec -it todo_postgres_dev psql -U todouser -d todoapp"
echo "To connect to test DB: docker exec -it todo_postgres_test psql -U todouser -d todoapp_test"
