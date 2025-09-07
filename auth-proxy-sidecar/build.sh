#!/bin/bash

# Build script for auth-proxy-sidecar
# Automatically exports uv dependencies to requirements.txt before Docker build

set -e

echo "🔄 Exporting dependencies to requirements.txt..."
uv export --format requirements.txt --no-dev --output-file requirements.txt

echo "🏗️  Building Docker images for multiple architectures..."

# Build for local development (ARM64 for Apple Silicon)
echo "Building ARM64 image for local development..."
docker build --platform linux/arm64 -t auth-proxy-sidecar:latest-arm64 .

# Build for AKS deployment (AMD64 for cloud)
echo "Building AMD64 image for AKS deployment..."
docker build --platform linux/amd64 -t auth-proxy-sidecar:latest-amd64 .

# Tag the AMD64 version as latest for deployment
docker tag auth-proxy-sidecar:latest-amd64 auth-proxy-sidecar:latest

echo "✅ Build completed successfully!"
echo "📦 Images built:"
echo "  - auth-proxy-sidecar:latest-arm64 (for local development)"
echo "  - auth-proxy-sidecar:latest-amd64 (for AKS deployment)"
echo "  - auth-proxy-sidecar:latest (AMD64, ready for deployment)"

# Optional: Test the built image
if [ "$1" = "--test" ]; then
    echo "🧪 Testing the ARM64 image locally..."
    echo "Note: This will fail without proper Azure credentials configured"
    docker run --rm -d --platform linux/arm64 -p 8080:8080 --name auth-proxy-test auth-proxy-sidecar:latest-arm64
    sleep 5
    
    echo "Testing health endpoint..."
    if curl -f http://localhost:8080/health 2>/dev/null; then
        echo "✅ Health endpoint is responding"
    else
        echo "⚠️  Health endpoint test failed (expected without Azure credentials)"
    fi
    
    echo "Cleaning up test container..."
    docker stop auth-proxy-test 2>/dev/null || true
fi

echo ""
echo "🚀 Usage:"
echo "  Local development:  docker run -p 8080:8080 auth-proxy-sidecar:latest-arm64"
echo "  AKS deployment:     docker push auth-proxy-sidecar:latest"
