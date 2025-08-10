#!/usr/bin/env bash
set -euo pipefail

# --- Configuration ---
RESOURCE_GROUP="kubernetes-learning"
AKS_CLUSTER_NAME="kube-mooc"

echo "--- Stopping Azure Kubernetes Service ---"
az aks stop --name "$AKS_CLUSTER_NAME" --resource-group "$RESOURCE_GROUP"

echo "--- Verifying Cluster Status ---"
# Get the current power state code from Azure
STATUS=$(az aks show --name "$AKS_CLUSTER_NAME" --resource-group "$RESOURCE_GROUP" --query "powerState.code" -o tsv)

# Check if the status is "Stopped"
if [ "$STATUS" == "Stopped" ]; then
    echo "Verification successful: Cluster is stopped."
else
    echo "Verification failed: Cluster status is '$STATUS'."
    exit 1
fi
