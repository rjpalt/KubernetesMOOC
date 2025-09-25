#!/bin/bash

# Local build script for broadcaster service
set -e

echo "🏗️ Building broadcaster container locally..."

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found in current directory"
    exit 1
fi

echo "🏗️  Building Docker images for multiple architectures..."

# Build for local development (ARM64 for Apple Silicon)
echo "Building ARM64 image for local development..."
docker build --platform linux/arm64 -t broadcaster:latest-arm64 .

# Build for AKS deployment (AMD64 for cloud)
echo "Building AMD64 image for AKS deployment..."
docker build --platform linux/amd64 -t broadcaster:latest-amd64 .

# Tag the AMD64 version as latest for deployment
docker tag broadcaster:latest-amd64 broadcaster:latest

echo "✅ Build completed successfully!"
echo "� Images built:"
echo "  - broadcaster:latest-arm64 (for local development)"
echo "  - broadcaster:latest-amd64 (for AKS deployment)"
echo "  - broadcaster:latest (AMD64, ready for deployment)"

# Optional: Test the built image
if [ "$1" = "--test" ]; then
    echo "🧪 Testing the ARM64 image locally..."
    echo "Note: This will test local ARM64 image"
    docker run --rm -d --platform linux/arm64 -p 8002:8002 -p 7777:7777 --name broadcaster-test -e WEBHOOK_URL=https://httpbin.org/post broadcaster:latest-arm64
    sleep 5
    
    echo "Testing health endpoint..."
    if curl -f http://localhost:8002/health 2>/dev/null; then
        echo "✅ Health endpoint is responding"
    else
        echo "⚠️  Health endpoint test failed"
    fi
    
    echo "Cleaning up test container..."
    docker stop broadcaster-test 2>/dev/null || true
fi

echo ""
echo "🚀 Usage:"
echo "  Local development:  WEBHOOK_URL=https://httpbin.org/post docker run -p 8002:8002 -p 7777:7777 broadcaster:latest-arm64"
echo "  AKS deployment:     docker push broadcaster:latest"
echo ""
echo "📋 Next steps:"
echo "  • Test locally: ./build.sh --test"
echo "  • Push to registry: ./build-and-push.sh"
echo "  • Check health: curl http://localhost:8002/health"
echo "  • Check metrics: curl http://localhost:7777/metrics"
