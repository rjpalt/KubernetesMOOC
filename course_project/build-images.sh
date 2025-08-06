#!/bin/bash

# Build script for todo application Docker images
# Usage: ./build-images.sh <tag>
# Example: ./build-images.sh v1.0.0

set -e  # Exit on any error

# Check if tag parameter is provided
if [ $# -eq 0 ]; then
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
else
    TAG=$1
fi

echo "Building Docker images with tag: $TAG"
echo "Platform: linux/amd64 (AKS compatible)"
echo "=========================================="

# Build frontend image
echo "Building frontend image (todo-app-fe:$TAG)..."
cd todo-app
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in todo-app directory"
    exit 1
fi

docker build --platform linux/amd64 -t todo-app-fe:$TAG .
if [ $? -eq 0 ]; then
    echo "✓ Frontend image built successfully: todo-app-fe:$TAG"
else
    echo "✗ Frontend image build failed"
    exit 1
fi

# Build backend image
echo ""
echo "Building backend image (todo-app-be:$TAG)..."
cd ../todo-backend
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in todo-backend directory"
    exit 1
fi

docker build --platform linux/amd64 -t todo-app-be:$TAG .
if [ $? -eq 0 ]; then
    echo "✓ Backend image built successfully: todo-app-be:$TAG"
else
    echo "✗ Backend image build failed"
    exit 1
fi

# Build cron job image
echo ""
echo "Building cron job image (todo-app-cron:$TAG)..."
cd ../todo-cron
if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in todo-cron directory"
    exit 1
fi

docker build --platform linux/amd64 -t todo-app-cron:$TAG .
if [ $? -eq 0 ]; then
    echo "✓ Cron job image built successfully: todo-app-cron:$TAG"
else
    echo "✗ Cron job image build failed"
    exit 1
fi

# Update docker-compose.yaml with new tag
echo ""
echo "Updating docker-compose.yaml with tag: $TAG"
echo "============================================"

# Go back to project root
cd ..

# Create backup
if [ -f "docker-compose.yaml" ]; then
    cp docker-compose.yaml docker-compose.yaml.backup
    echo "✓ Backup created: docker-compose.yaml.backup"
    
    # Update image tags using sed
    sed -i.tmp "s/image: todo-app-be:[^[:space:]]*/image: todo-app-be:$TAG/" docker-compose.yaml
    sed -i.tmp "s/image: todo-app-fe:[^[:space:]]*/image: todo-app-fe:$TAG/" docker-compose.yaml
    sed -i.tmp "s/image: todo-app-cron:[^[:space:]]*/image: todo-app-cron:$TAG/" docker-compose.yaml
    rm docker-compose.yaml.tmp  # Remove sed backup file
    
    # Validate YAML syntax
    python3 -c "import yaml; yaml.safe_load(open('docker-compose.yaml'))" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ docker-compose.yaml updated successfully"
        echo "✓ YAML validation passed"
    else
        echo "✗ YAML validation failed! Restoring backup..."
        cp docker-compose.yaml.backup docker-compose.yaml
        echo "✓ Backup restored"
        exit 1
    fi
else
    echo "⚠ docker-compose.yaml not found - skipping update"
fi

echo ""
echo "=========================================="
echo "✓ All images built successfully!"
echo "Images created:"
echo "  - todo-app-fe:$TAG"
echo "  - todo-app-be:$TAG"
echo "  - todo-app-cron:$TAG"
echo ""
echo "✓ docker-compose.yaml updated to use tag: $TAG"
echo "You can now use these images in your Kubernetes manifests or run with docker-compose."
