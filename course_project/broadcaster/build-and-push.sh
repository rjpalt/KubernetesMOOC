#!/bin/bash

# Build and push script for AKS deployment (following auth-proxy-sidecar pattern)
set -e

# Configuration
REGISTRY=${REGISTRY:-"kubemooc.azurecr.io"}
IMAGE_NAME=${IMAGE_NAME:-"broadcaster"}
TAG=${TAG:-"latest"}

echo "🔐 Logging into Azure Container Registry..."
if ! az acr login --name kubemooc; then
    echo "❌ Failed to login to Azure Container Registry"
    echo "💡 Make sure you're logged into Azure CLI with 'az login'"
    echo "💡 And have access to kubemooc.azurecr.io registry"
    exit 1
fi

echo "🏗️ Building AMD64 image for AKS deployment..."

# Build and push AMD64 image only (AKS uses AMD64 nodes)
docker build --platform linux/amd64 -t "${REGISTRY}/${IMAGE_NAME}:${TAG}" .

echo "📤 Pushing to Azure Container Registry..."
docker push "${REGISTRY}/${IMAGE_NAME}:${TAG}"

# Also tag with timestamp for versioning
TIMESTAMP_TAG="${REGISTRY}/${IMAGE_NAME}:$(date +%Y%m%d-%H%M%S)"
docker tag "${REGISTRY}/${IMAGE_NAME}:${TAG}" "${TIMESTAMP_TAG}"
docker push "${TIMESTAMP_TAG}"

echo "✅ AMD64 image built and pushed successfully!"
echo "📦 Images pushed:"
echo "  - ${REGISTRY}/${IMAGE_NAME}:${TAG} (latest)"
echo "  - ${TIMESTAMP_TAG} (timestamped)"
echo ""
echo "🚀 Deploy to AKS with:"
echo "  kubectl apply -k course_project/manifests/overlays/development/"
echo ""
echo "🔄 Or restart existing deployment:"
echo "  kubectl rollout restart deployment/broadcaster -n feature-ex-c4-e6"
echo ""
echo "💡 To configure:"
echo "  export REGISTRY=kubemooc.azurecr.io"
echo "  export IMAGE_NAME=broadcaster"
echo "  export TAG=v1.0.0"
echo ""
echo "⚠️  Prerequisites:"
echo "  - Azure CLI installed and logged in (az login)"
echo "  - Docker daemon running"
