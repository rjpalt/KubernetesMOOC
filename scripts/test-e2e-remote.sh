#!/bin/bash

set -e

TARGET_URL=$1

if [ -z "$TARGET_URL" ]; then
    echo "Error: TARGET_URL is required"
    echo "Usage: $0 <target_url>"
    exit 1
fi

echo "Building Playwright test image..."
docker build -t todo-app-e2e:latest-$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/') ./course_project/tests/e2e

echo "Running E2E tests against $TARGET_URL..."
docker run --rm -e E2E_BASE_URL="$TARGET_URL" todo-app-e2e:latest-$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
