# Kubernetes Manifests - Kustomization Structure

This directory contains Kubernetes manifests organized for use with Kustomize, enabling flexible deployment across different environments.

## Directory Structure

```
manifests/
├── base/                          # Base configurations (environment-agnostic)
│   ├── shared/                    # Shared resources (namespace, ingress)
│   │   ├── namespace.yaml
│   │   └── ingress.yaml
│   ├── postgres/                  # PostgreSQL database
│   │   ├── statefulset.yaml
│   │   ├── service.yaml
│   │   ├── secrets.yaml
│   │   └── secrets.enc.yaml
│   ├── todo-be/                   # Backend API service
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── todo-fe/                   # Frontend web service
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── persistentvolume.yaml
│   │   └── persistentvolumeclaim.yaml
│   └── todo-cron/                 # Scheduled Wikipedia todo generation
│       └── cronjob.yaml
└── overlays/                      # Environment-specific overrides
    ├── development/               # Development environment settings
    ├── staging/                   # Staging environment settings
    └── production/                # Production environment settings
```

## Deployment Dependencies

Services must be deployed in the following order due to dependencies:

1. **shared/** - Creates namespace and ingress configuration
2. **postgres/** - Database must be ready before backend
3. **todo-be/** - Backend API must be ready before frontend and cron
4. **todo-fe/** - Frontend service (depends on backend)
5. **todo-cron/** - Scheduled tasks (depends on backend API)

## Kustomization Files

Each service directory contains `kustomization.yaml` files that define their resources:

### Individual Service Deployment

Deploy individual services:
```bash
# Deploy shared resources first
kubectl apply -k manifests/base/shared/

# Deploy database
kubectl apply -k manifests/base/postgres/

# Deploy backend
kubectl apply -k manifests/base/todo-be/

# Deploy frontend  
kubectl apply -k manifests/base/todo-fe/

# Deploy cron job
kubectl apply -k manifests/base/todo-cron/
```

### Full Stack Deployment

Deploy the entire application with a single command:
```bash
# Deploy all services at once (recommended)
kubectl apply -k manifests/base/

# Or using explicit path
kubectl apply -k course_project/manifests/base/
```

The full-stack kustomization automatically handles deployment order and applies common labels to all resources.

## Service Communication

- **Frontend → Backend**: HTTP API calls via service DNS (`todo-app-be-svc:2506`)
- **Cron → Backend**: HTTP API calls via service DNS (`todo-app-be-svc:2506`)
- **Backend → Database**: PostgreSQL connection via service DNS (`postgres-svc:5432`)
- **External Access**: Through Ingress routing to frontend and backend services

## Cluster-Level Security Configuration

### Namespace Deletion Protection

Kubernetes RBAC has been configured to restrict namespace deletion to authorized Azure Functions only:

**Location**: `/cluster-manifests/cluster-protection-rbac.yaml`

**Applied**: August 19, 2025 ✅

```bash
kubectl apply -f cluster-manifests/cluster-protection-rbac.yaml
```

**Purpose**: 
- Prevents accidental deletion of critical namespaces
- Restricts namespace deletion to the deprovisioning function only
- Allows safe cleanup of feature branch environments

**Details**:
- **ClusterRole**: `namespace-manager` - defines namespace deletion permissions
- **ClusterRoleBinding**: Only `mi-deprovisioning-function` (Principal ID: `41ed2068-1c66-4911-9345-1b413cb9a21c`) can delete namespaces
- **Protection**: System namespaces (`default`, `kube-system`, etc.) are protected via application logic

This ensures that feature branch cleanup is secure and controlled while protecting production and system namespaces.

## Environment Patterns

- **Development**: Single replicas, resource limits for local testing
- **Staging**: Production-like settings with reduced resources
- **Production**: Multiple replicas, strict resource limits, security policies
