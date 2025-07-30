# Common Kubernetes Commands

This file contains frequently used command patterns across exercises.

## Standard Setup Pattern

Most exercises follow this basic pattern:

### 1. Start k3d Cluster
```bash
k3d cluster create -p 8080:80@loadbalancer -a 2
```

### 2. Import Images
```bash
# Single image
k3d image import <image-name>:<tag>

# Multiple images
k3d image import image1:tag1
k3d image import image2:tag2
```

### 3. Create Persistent Volume Folder (when needed)
```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
```

### 4. Apply Manifests
```bash
# Apply all manifests in a directory
kubectl apply -f manifests/

# Apply specific manifest files
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/service.yaml
kubectl apply -f manifests/ingress.yaml
```

### 5. Namespace Operations (Chapter 3+)
```bash
# Apply namespace
kubectl apply -f manifests/shared/namespace.yaml

# Switch to namespace
kubens <namespace-name>
```

### 6. Secrets (with SOPS)
```bash
sops --decrypt manifests/path/secret.enc.yaml | kubectl apply -f -
```

### 7. Verification Commands
```bash
# Check resources
kubectl get pods,svc,ingress
kubectl get pv,pvc,pods,svc,ingress

# Check logs
kubectl logs -f <pod-name>

# Test endpoints
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/pingpong
```

## Exercise-Specific Patterns

### Port Forwarding (Early exercises)
```bash
kubectl port-forward <pod-name> <local-port>:<container-port>
```

### Persistent Volume Commands
```bash
kubectl exec -it <pod-name> -c <container-name> -- ls /path
kubectl exec -it <pod-name> -c <container-name> -- cat /path/file.txt
```

### Database Setup Pattern
```bash
# Secrets first
sops --decrypt manifests/postgres/secret.enc.yaml | kubectl apply -f -

# Then service and statefulset
kubectl apply -f manifests/postgres/service.yaml
kubectl apply -f manifests/postgres/statefulset.yaml
```
