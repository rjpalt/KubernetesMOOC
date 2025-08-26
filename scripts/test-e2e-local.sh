#!/bin/bash
set -e

COMPOSE_FILE="course_project/docker-compose.yaml"
PLAYWRIGHT_EXIT_CODE=0

echo "Starting application services..."
docker-compose -f $COMPOSE_FILE up -d --build todo-app-fe todo-app-be postgres_prod

echo "Waiting for services to be healthy..."
while ! docker-compose -f $COMPOSE_FILE exec -T todo-app-fe curl -f http://localhost:8000/health >/dev/null 2>&1; do
    echo "Waiting for todo-app-fe to be healthy..."
    sleep 5
done

echo "Services are ready. Running Playwright tests..."
set +e
docker-compose -f $COMPOSE_FILE run --build --rm playwright
PLAYWRIGHT_EXIT_CODE=$?
set -e

echo "Cleaning up services..."
docker-compose -f $COMPOSE_FILE down

if [ $PLAYWRIGHT_EXIT_CODE -eq 0 ]; then
    echo "E2E tests passed successfully!"
else
    echo "E2E tests failed with exit code $PLAYWRIGHT_EXIT_CODE"
fi

exit $PLAYWRIGHT_EXIT_CODE
