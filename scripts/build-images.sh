#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"

# Build script for todo application Docker images
# Usage: ./build-images.sh <tag>
# Example: ./build-images.sh v1.0.0

TAG="${1:-}"
if [ -z "$TAG" ]; then
    echo "Warning: No tag provided"
    echo "If you continue, the tag 'latest' will be used."
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo    # Move to new line
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Build cancelled."
        echo "Usage: $0 <tag>"
        echo "Example: $0 v1.0.0"
        exit 1
    fi
    TAG="latest"
    echo "Using tag: latest"
fi

echo "Building Docker images with tag: $TAG"
echo "Architectures: ARM64 (local development) + AMD64 (AKS deployment)"
echo "=================================================================="

cd "$ROOT/course_project"

# Build ARM64 images (for local development)
echo "Building ARM64 images for local development..."
echo "----------------------------------------------"

# Build frontend ARM64 image
echo "Building frontend ARM64 image (todo-app-fe:$TAG-arm64)..."
cd todo-app
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in todo-app directory"
    exit 1
fi

docker build --platform linux/arm64 -t todo-app-fe:$TAG-arm64 .
if [ $? -eq 0 ]; then
    echo "Frontend ARM64 image built successfully: todo-app-fe:$TAG-arm64"
else
    echo "Frontend ARM64 image build failed"
    exit 1
fi

# Build backend ARM64 image
echo ""
echo "Building backend ARM64 image (todo-app-be:$TAG-arm64)..."
cd ../todo-backend
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in todo-backend directory"
    exit 1
fi

docker build --platform linux/arm64 -t todo-app-be:$TAG-arm64 .
if [ $? -eq 0 ]; then
    echo "Backend ARM64 image built successfully: todo-app-be:$TAG-arm64"
else
    echo "Backend ARM64 image build failed"
    exit 1
fi

# Build cron job ARM64 image
echo ""
echo "Building cron job ARM64 image (todo-app-cron:$TAG-arm64)..."
cd ../todo-cron
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in todo-cron directory"
    exit 1
fi

docker build --platform linux/arm64 -t todo-app-cron:$TAG-arm64 .
if [ $? -eq 0 ]; then
    echo "Cron job ARM64 image built successfully: todo-app-cron:$TAG-arm64"
else
    echo "Cron job ARM64 image build failed"
    exit 1
fi

# Build AMD64 images (for AKS deployment)
echo ""
echo "Building AMD64 images for AKS deployment..."
echo "-------------------------------------------"

# Build frontend AMD64 image
echo "Building frontend AMD64 image (todo-app-fe:$TAG-amd64)..."
cd ../todo-app

docker build --platform linux/amd64 -t todo-app-fe:$TAG-amd64 .
if [ $? -eq 0 ]; then
    echo "Frontend AMD64 image built successfully: todo-app-fe:$TAG-amd64"
else
    echo "Frontend AMD64 image build failed"
    exit 1
fi

# Build backend AMD64 image
echo ""
echo "Building backend AMD64 image (todo-app-be:$TAG-amd64)..."
cd ../todo-backend

docker build --platform linux/amd64 -t todo-app-be:$TAG-amd64 .
if [ $? -eq 0 ]; then
    echo "Backend AMD64 image built successfully: todo-app-be:$TAG-amd64"
else
    echo "Backend AMD64 image build failed"
    exit 1
fi

# Build cron job AMD64 image
echo ""
echo "Building cron job AMD64 image (todo-app-cron:$TAG-amd64)..."
cd ../todo-cron

docker build --platform linux/amd64 -t todo-app-cron:$TAG-amd64 .
if [ $? -eq 0 ]; then
    echo "Cron job AMD64 image built successfully: todo-app-cron:$TAG-amd64"
else
    echo "Cron job AMD64 image build failed"
    exit 1
fi

# Build E2E ARM64 image
echo ""
echo "Building E2E ARM64 image (todo-app-e2e:$TAG-arm64)..."
cd ../tests/e2e
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in tests/e2e directory"
    exit 1
fi

docker build --platform linux/arm64 -t todo-app-e2e:$TAG-arm64 .
if [ $? -eq 0 ]; then
    echo "E2E ARM64 image built successfully: todo-app-e2e:$TAG-arm64"
else
    echo "E2E ARM64 image build failed"
    exit 1
fi
cd ../../course_project

# Build E2E AMD64 image
echo ""
echo "Building E2E AMD64 image (todo-app-e2e:$TAG-amd64)..."
cd ../tests/e2e

docker build --platform linux/amd64 -t todo-app-e2e:$TAG-amd64 .
if [ $? -eq 0 ]; then
    echo "E2E AMD64 image built successfully: todo-app-e2e:$TAG-amd64"
else
    echo "E2E AMD64 image build failed"
    exit 1
fi
cd ../../course_project

# Update docker-compose.yaml with new tag
echo ""
echo "Updating docker-compose.yaml with ARM64 images for local development"
echo "=================================================================="

# Go back to project root
cd ..

# Create backup
if [ -f "docker-compose.yaml" ]; then
    cp docker-compose.yaml docker-compose.yaml.backup
    echo "Backup created: docker-compose.yaml.backup"
    
    # Update image tags using sed (use ARM64 variants for local development)
    sed -i.tmp "s/image: todo-app-be:[^[:space:]]*/image: todo-app-be:$TAG-arm64/" docker-compose.yaml
    sed -i.tmp "s/image: todo-app-fe:[^[:space:]]*/image: todo-app-fe:$TAG-arm64/" docker-compose.yaml
    sed -i.tmp "s/image: todo-app-cron:[^[:space:]]*/image: todo-app-cron:$TAG-arm64/" docker-compose.yaml
    sed -i.tmp "s/image: todo-app-e2e:[^[:space:]]*/image: todo-app-e2e:$TAG-arm64/" docker-compose.yaml
    rm docker-compose.yaml.tmp  # Remove sed backup file
    
    # Validate YAML syntax using docker compose (no Python dependency)
    if docker compose -f docker-compose.yaml config -q >/dev/null 2>&1; then
        echo "docker-compose.yaml updated successfully with ARM64 images"
        echo "YAML validation passed (docker compose config)"
    else
        echo "YAML validation failed! Restoring backup..."
        cp docker-compose.yaml.backup docker-compose.yaml
        echo "Backup restored"
        exit 1
    fi
else
    echo "docker-compose.yaml not found - skipping update"
fi

echo ""
echo "=================================================================="
echo "All images built successfully!"
echo "ARM64 images (for local development):"
echo "  - todo-app-fe:$TAG-arm64"
echo "  - todo-app-be:$TAG-arm64"
echo "  - todo-app-cron:$TAG-arm64"
echo "  - todo-app-e2e:$TAG-arm64"
echo ""
echo "AMD64 images (for AKS deployment):"
echo "  - todo-app-fe:$TAG-amd64"
echo "  - todo-app-be:$TAG-amd64"
echo "  - todo-app-cron:$TAG-amd64"
echo "  - todo-app-e2e:$TAG-amd64"
echo ""
echo "docker-compose.yaml updated to use ARM64 images for local development"
echo "Use the AMD64 images in your Kubernetes manifests for AKS deployment."
