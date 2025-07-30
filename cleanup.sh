#!/bin/bash

# Cleanup script for Docker and Kubernetes resources
# This script will properly shut down Kubernetes resources before cleaning up Docker

set -e  # Exit on any error

echo "Starting cleanup process..."

# First, check if kubectl is available and we have a cluster context
if command -v kubectl &> /dev/null; then
    echo "Checking for running Kubernetes resources..."
    
    # Clean up Helm releases first (Exercise 2.10 monitoring stack)
    if command -v helm &> /dev/null; then
        echo "Cleaning up Helm releases..."
        
        # Uninstall Prometheus/Grafana stack
        if helm list -n prometheus 2>/dev/null | grep -q "kube-prometheus-stack"; then
            echo "Uninstalling Prometheus/Grafana stack..."
            helm uninstall -n prometheus $(helm list -n prometheus -q) 2>/dev/null || echo "Prometheus stack cleanup completed"
        fi
        
        # Uninstall Loki stack
        if helm list -n loki-stack 2>/dev/null | grep -q "loki"; then
            echo "Uninstalling Loki stack..."
            helm uninstall -n loki-stack loki 2>/dev/null || echo "Loki stack cleanup completed"
        fi
        
        # Clean up any remaining Helm releases in other namespaces
        ALL_RELEASES=$(helm list --all-namespaces -q 2>/dev/null || echo "")
        if [ -n "$ALL_RELEASES" ]; then
            echo "Cleaning up remaining Helm releases..."
            echo "$ALL_RELEASES" | xargs -I {} helm uninstall {} --namespace $(helm list --all-namespaces | grep {} | awk '{print $2}') 2>/dev/null || echo "Helm cleanup completed"
        fi
    else
        echo "Helm not found, skipping Helm cleanup"
    fi
    
    # Delete monitoring namespaces (this will cascade delete everything in them)
    echo "Deleting monitoring namespaces..."
    kubectl delete namespace prometheus loki-stack --ignore-not-found=true --timeout=60s 2>/dev/null || echo "Monitoring namespaces already clean"
    
    # Get all pods across all namespaces
    if kubectl get pods --all-namespaces 2>/dev/null | grep -q -v "^NAMESPACE"; then
        echo "Found remaining pods, shutting them down gracefully..."
        
        # Delete all deployments first (this will scale down pods gracefully)
        echo "Deleting all deployments..."
        kubectl delete deployments --all --all-namespaces --grace-period=30 --timeout=60s 2>/dev/null || echo "No deployments to delete or timeout reached"
        
        # Delete all services
        echo "Deleting all services..."
        kubectl delete services --all --all-namespaces --grace-period=30 --timeout=60s 2>/dev/null || echo "No services to delete or timeout reached"
        
        # Delete all remaining pods (if any stragglers)
        echo "Deleting any remaining pods..."
        kubectl delete pods --all --all-namespaces --grace-period=30 --timeout=60s 2>/dev/null || echo "No pods to delete or timeout reached"
        
        # Wait a bit for graceful shutdown
        echo "Waiting for graceful shutdown..."
        sleep 5
        
        # Force delete any stuck pods
        echo "Force deleting any stuck pods..."
        kubectl delete pods --all --all-namespaces --force --grace-period=0 2>/dev/null || echo "No stuck pods to force delete"
        
        echo "Kubernetes resources cleaned up"
    else
        echo "No running pods found"
    fi
else
    echo "kubectl not found, skipping Kubernetes cleanup"
fi

# Now check for running clusters and delete them
echo "Checking for running Kubernetes clusters..."
if k3d cluster list 2>/dev/null | grep -q "k3s-default"; then
    k3d cluster delete k3s-default
    echo "k3d cluster deleted"
elif k3d cluster list 2>/dev/null | grep -q -E "^\s*\*"; then
    # Delete the currently active cluster if no default found
    CLUSTER_NAME=$(k3d cluster list | grep -E "^\s*\*" | awk '{print $2}')
    echo "Deleting active cluster: $CLUSTER_NAME"
    k3d cluster delete "$CLUSTER_NAME"
    echo "k3d cluster deleted"
else
    echo "No k3d cluster found to delete"
fi

# Stop and remove all Docker containers
echo "Stopping all Docker containers..."
if [ "$(docker ps -q)" ]; then
    docker stop $(docker ps -q)
    echo "All containers stopped"
else
    echo "No running containers found"
fi

echo "Removing all Docker containers..."
if [ "$(docker ps -aq)" ]; then
    docker rm $(docker ps -aq)
    echo "All containers removed"
else
    echo "No containers to remove"
fi

# Remove Docker networks (except default ones)
echo "Removing custom Docker networks..."
CUSTOM_NETWORKS=$(docker network ls --filter type=custom --format "{{.Name}}" | grep -v "bridge\|host\|none" || true)
if [ -n "$CUSTOM_NETWORKS" ]; then
    echo "$CUSTOM_NETWORKS" | xargs -r docker network rm
    echo "Custom networks removed"
else
    echo "No custom networks to remove"
fi

# Skip Docker volumes cleanup (not needed for this project)
echo "Skipping Docker volumes cleanup..."

# Optional: Clean up Docker system (removes unused images, build cache, etc.)
echo "Cleaning up Docker system..."
docker system prune -f
echo "Docker system cleaned up"

echo "Cleanup complete! Your system is now clean."
echo "Note: Docker images are preserved. Use 'docker image prune -a' to remove unused images."
