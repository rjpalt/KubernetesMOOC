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
│   ├── nats/                      # NATS message bus infrastructure
│   │   ├── statefulset.yaml      # 2-container pod (nats + metrics-exporter)
│   │   ├── service.yaml          # Main NATS service (port 4222)
│   │   ├── metrics-service.yaml  # Prometheus metrics service (port 7777)
│   │   ├── configmap.yaml        # NATS server configuration
│   │   └── kustomization.yaml    # Base resource list
│   ├── todo-be/                   # Backend API service
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── todo-fe/                   # Frontend web service
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── persistentvolume.yaml
│   │   └── persistentvolumeclaim.yaml
│   ├── todo-cron/                 # Scheduled Wikipedia todo generation
│   │   └── cronjob.yaml
│   └── broadcaster/               # NATS to HTTP webhook broadcaster service
│       ├── deployment.yaml       # FastAPI service with NATS consumer
│       ├── service.yaml          # Main HTTP service (port 8002)
│       ├── metrics-service.yaml  # Prometheus metrics service (port 7777)
│       ├── secret-template.yaml  # Webhook URL configuration
│       └── kustomization.yaml    # Base resource list
└── overlays/                      # Environment-specific overrides
    ├── development/               # Development environment settings
    │   └── nats/                  # NATS development overlay
    │       ├── nats-dev-patch.yaml
    │       └── kustomization.yaml
    ├── staging/                   # Staging environment settings
    └── production/                # Production environment settings
        ├── nats/                  # NATS production overlay
        │   ├── nats-prod-patch.yaml
        │   └── kustomization.yaml
        ├── hpa-backend.yaml       # Backend autoscaling (1-5 replicas)
        ├── hpa-frontend.yaml      # Frontend autoscaling (1-3 replicas)
        ├── hpa-broadcaster.yaml   # Broadcaster autoscaling (1-5 replicas)
        ├── resourcequota.yaml     # Resource limits
        └── kustomization.yaml     # Production-specific configuration
```

## NATS Message Bus Infrastructure

### Architecture Overview

The NATS message bus provides the core messaging infrastructure for the todo application, enabling asynchronous communication between services. The implementation follows GitOps principles with static manifests generated from proven Helm charts.

### How NATS Integration Works

**Core Message Bus**: NATS serves as the central nervous system for the todo application:
- **Publisher**: Todo-backend publishes todo creation/update events
- **Subscriber**: Broadcaster service consumes events and triggers notifications
- **Protocol**: Native NATS messaging protocol for high-performance pub/sub

**Service Discovery Pattern**:
```yaml
NATS Connection String: nats://nats:4222
Namespace: feature-ex-c4-e6 (development) | project (production)
Protocol: NATS native messaging
```

### Multi-Container Pod Architecture

The NATS pod runs two containers for separation of concerns:

**Primary Container** (`nats`):
- **Image**: `docker.io/bitnami/nats:2.11.8-debian-12-r0`
- **Purpose**: Core NATS message broker
- **Ports**: 4222 (client), 6222 (cluster), 8222 (monitoring)
- **Health**: HTTP probes on monitoring port

**Metrics Sidecar** (`nats-exporter`):
- **Image**: `docker.io/bitnami/nats-exporter:0.17.3-debian-12-r8`
- **Purpose**: Prometheus metrics collection
- **Port**: 7777 (metrics endpoint)
- **Integration**: Scrapes NATS monitoring API (localhost:8222)

### Why This Architecture Works

1. **Separation of Concerns**: Messaging and monitoring are isolated
2. **Azure Integration**: Prometheus annotations enable auto-discovery
3. **Health Monitoring**: Independent health checks for each function
4. **Resource Efficiency**: Shared pod networking with minimal overhead

### GitOps Implementation Strategy

**Helm Template Generation Approach**:
```bash
# One-time manifest generation from proven chart
helm template nats bitnami/nats -f values.yaml > base/nats/manifests.yaml

# Split into individual resource files
# Commit to Git as single source of truth
# Use Kustomize overlays for environment differences
```

**Why Helm Template vs Direct Helm Install**:
- ✅ **GitOps Compliance**: Declarative manifests in version control
- ✅ **Single Source of Truth**: Base manifests are authoritative
- ✅ **Multi-Environment**: Kustomize overlays for feature vs production
- ✅ **CI/CD Integration**: kubectl apply -k deployment pattern
- ✅ **Proven Configuration**: Leverages Bitnami chart expertise

⚠️ **Trade-off: Manual Update Responsibility**: We accept responsibility for updating images and configurations manually rather than automatic Helm chart updates.

### NATS Services Architecture

**Main Service** (`nats`):
- **Purpose**: Client connections and inter-service communication
- **Port**: 4222 (NATS protocol)
- **Usage**: `nats://nats:4222` from application services

**Headless Service** (`nats-headless`):
- **Purpose**: StatefulSet pod discovery and clustering
- **Ports**: 4222, 6222, 8222
- **Usage**: Internal NATS cluster formation

**Metrics Service** (`nats-metrics`):
- **Purpose**: Prometheus metrics collection
- **Port**: 7777 (HTTP metrics endpoint)
- **Annotations**: Azure Managed Prometheus auto-discovery
- **Usage**: `http://nats-metrics:7777/metrics`

### Environment Configuration Strategy

**Development Overlay** (Feature Branches):
```yaml
Replicas: 1 (single instance)
Resources: Minimal (50m CPU, 128Mi memory)
Persistence: None (ephemeral storage)
Clustering: Disabled
```

**Production Overlay** (Project Namespace):
```yaml
Replicas: 3 (high availability cluster)
Resources: Production (500m CPU, 512Mi memory)
Persistence: 10Gi storage per node
Clustering: Enabled with inter-node routing
```

### Metrics and Monitoring Integration

**Azure Managed Prometheus Integration**:
- **Discovery**: Annotation-based service discovery
- **Metrics Port**: 7777 (standard across all services)
- **Scrape Path**: /metrics (Prometheus format)
- **Auto-Discovery**: `prometheus.io/scrape: "true"`

**Available Metrics**:
- Connection metrics (`gnatsd_connz_*`)
- Route metrics (`gnatsd_routez_*`) 
- Subscription metrics (`gnatsd_subsz_*`)
- Server metrics (`gnatsd_varz_*`)
- Go runtime metrics (`go_*`)
- Process metrics (`process_*`)

### Security and Network Policy

**Container Security**:
- Non-root user execution (UID 1001)
- Read-only root filesystem
- Minimal capabilities (drop ALL)
- Security context enforcement

**Network Policy**:
- Ingress: Ports 4222, 6222, 7777, 8222
- Egress: Unrestricted (for external integrations)
- Namespace isolation maintained

## Broadcaster Service Infrastructure

### Architecture Overview

The Broadcaster service bridges NATS messaging with external HTTP webhooks, enabling the todo application to notify external systems of todo events asynchronously.

### How Broadcaster Integration Works

**Core Message Consumer**: Broadcaster subscribes to NATS messages and forwards them as HTTP webhooks:
- **Subscriber**: Consumes messages from NATS topic `todos.events` 
- **Queue Group**: Uses `broadcaster-workers` queue group for load balancing across replicas
- **Webhook Client**: Forwards messages to external HTTP endpoints
- **Protocol**: NATS native subscription + HTTP POST for webhooks

**Service Discovery Pattern**:
```yaml
NATS Connection: nats://nats:4222
HTTP Service: broadcaster-svc:8002
Metrics Endpoint: broadcaster-metrics:7777
Webhook URL: Configured via broadcaster-secret (WEBHOOK_URL)
```

### Multi-Port Service Architecture

The Broadcaster deployment exposes two ports for separation of concerns:

**Main Service Port** (`8002`):
- **Purpose**: HTTP API for health checks and service management
- **Health Endpoints**: `/health` (readiness), `/healthz` (liveness)
- **Service**: `broadcaster-svc:8002`

**Metrics Port** (`7777`):
- **Purpose**: Prometheus metrics collection
- **Endpoint**: `/metrics` (Prometheus format)
- **Service**: `broadcaster-metrics:7777`
- **Integration**: Azure Managed Prometheus auto-discovery via annotations

### Why This Architecture Works

1. **Queue Groups**: Load balancing ensures only one replica processes each message
2. **Resilient Design**: Service continues running even if NATS or webhook endpoints are unavailable
3. **Azure Integration**: Prometheus annotations enable automatic metrics collection
4. **Security**: Non-root containers with read-only filesystem and minimal capabilities
5. **Scalability**: HPA enables automatic scaling based on CPU utilization

### Environment Configuration Strategy

**Development Overlay** (Feature Branches):
```yaml
Replicas: 1 (single instance for testing)
Resources: Minimal (50m CPU, 64Mi memory)
Webhook URL: https://httpbin.org/post (test endpoint)
Log Level: DEBUG (verbose logging)
```

**Production Overlay** (Project Namespace):
```yaml
Replicas: 2-5 (HPA-managed with queue group load balancing)
Resources: Production (100m CPU, 128Mi memory)
Webhook URL: Production webhook endpoint
Log Level: INFO (production logging)
```

### Metrics and Monitoring Integration

**Azure Managed Prometheus Integration**:
- **Discovery**: Annotation-based service discovery on `broadcaster-metrics`
- **Metrics Port**: 7777 (consistent with NATS pattern)
- **Scrape Path**: /metrics (Prometheus format)
- **Auto-Discovery**: `prometheus.io/scrape: "true"`

**Available Metrics**:
- Message processing (`broadcaster_messages_processed_total`)
- Webhook requests (`broadcaster_webhook_requests_total`)
- NATS connection status (`broadcaster_nats_connected`)
- HTTP request duration (`broadcaster_request_duration_seconds`)
- Go runtime metrics (`go_*`)
- Process metrics (`process_*`)

### Security and Configuration

**Container Security**:
- Non-root user execution (UID 1001)
- Read-only root filesystem with writable `/tmp` volumes
- Minimal capabilities (drop ALL)
- Security context enforcement

**Secret Management**:
- **webhook URL**: Stored in `broadcaster-secret` Kubernetes secret
- **Environment Variables**: Structured configuration via Pydantic settings
- **Development**: Test webhook URL (`https://httpbin.org/post`)
- **Production**: Real webhook endpoint (configured externally)

**Resource Management**:
- **Requests**: Conservative CPU/memory allocation
- **Limits**: Prevent resource exhaustion
- **HPA**: Automatic scaling based on CPU utilization (70% threshold)

## Autoscaling Configuration

### Horizontal Pod Autoscalers (Production Only)
The production overlay includes CPU-based autoscaling for all applications:

**Backend HPA** (`overlays/production/hpa-backend.yaml`):
- **Replicas**: 1-5 pods
- **Trigger**: 70% CPU utilization
- **Behavior**: 60s scale-up, 300s scale-down stabilization

**Frontend HPA** (`overlays/production/hpa-frontend.yaml`):
- **Replicas**: 1-3 pods  
- **Trigger**: 70% CPU utilization
- **Behavior**: 60s scale-up, 300s scale-down stabilization

**Broadcaster HPA** (`overlays/production/hpa-broadcaster.yaml`):
- **Replicas**: 1-5 pods
- **Trigger**: 70% CPU utilization
- **Behavior**: 60s scale-up, 300s scale-down stabilization
- **Queue Groups**: NATS queue groups ensure load balancing across replicas

### Cluster-Level Autoscaling
- **Node Autoscaler**: 1-5 nodes (configured at AKS cluster level)
- **Triggers**: Pod resource demands exceeding current node capacity
- **Scope**: Cluster-wide, supports all environments

## Deployment Dependencies

Services must be deployed in the following order due to dependencies:

1. **shared/** - Creates namespace and ingress configuration
2. **postgres/** - Database must be ready before backend
3. **nats/** - Message bus must be ready before broadcaster
4. **todo-be/** - Backend API must be ready before frontend and cron
5. **broadcaster/** - Message consumer (depends on NATS)
6. **todo-fe/** - Frontend service (depends on backend)
7. **todo-cron/** - Scheduled tasks (depends on backend API)

## Kustomization Files

Each service directory contains `kustomization.yaml` files that define their resources:

### Individual Service Deployment

Deploy individual services:
```bash
# Deploy shared resources first
kubectl apply -k manifests/base/shared/

# Deploy database
kubectl apply -k manifests/base/postgres/

# Deploy message bus
kubectl apply -k manifests/base/nats/

# Deploy backend
kubectl apply -k manifests/base/todo-be/

# Deploy frontend  
kubectl apply -k manifests/base/todo-fe/

# Deploy broadcaster service
kubectl apply -k manifests/base/broadcaster/

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
- **Backend → NATS**: Publishes todo events via NATS protocol (`nats://nats:4222`)
- **NATS → Broadcaster**: Message bus delivers events to subscriber services (`nats://nats:4222`)
- **Broadcaster → External**: HTTP webhooks to external services via configured URL
- **Cron → Backend**: HTTP API calls via service DNS (`todo-app-be-svc:2506`)
- **Backend → Database**: PostgreSQL connection via service DNS (`postgres-svc:5432`)
- **Monitoring → NATS**: Prometheus scrapes metrics via HTTP (`http://nats-metrics:7777/metrics`)
- **Monitoring → Broadcaster**: Prometheus scrapes metrics via HTTP (`http://broadcaster-metrics:7777/metrics`)
- **External Access**: Through Ingress routing to frontend and backend services

## Manifest Management Strategy

### GitOps with Helm Template Generation

This project uses a **hybrid approach** combining the expertise of Helm charts with GitOps principles:

**Generation Process**:
1. **Helm Template**: Generate static manifests from proven Bitnami charts
2. **Git Commit**: Base manifests become single source of truth in version control
3. **Kustomize Overlays**: Environment-specific patches for development/production
4. **kubectl apply**: Declarative deployment via Kustomize

**Benefits of This Approach**:
- ✅ **GitOps Compliance**: All resources declaratively defined in Git
- ✅ **Proven Configurations**: Leverage Bitnami chart best practices
- ✅ **Multi-Environment**: Kustomize overlays handle environment differences
- ✅ **CI/CD Friendly**: Standard kubectl apply -k deployment pattern
- ✅ **Version Control**: Full history of infrastructure changes

### Manual Update Responsibility

⚠️ **Important Trade-off**: By using `helm template` instead of `helm install`, we accept responsibility for manual updates:

**What We Must Monitor and Update**:
- **Container Images**: NATS and nats-exporter image versions
- **Security Patches**: CVE fixes in base images
- **Chart Updates**: New features or bug fixes from Bitnami
- **Configuration Changes**: Updated best practices or defaults

**Update Process When Required**:
```bash
# 1. Check for chart updates
helm repo update bitnami

# 2. Review changelog
helm show chart bitnami/nats
helm show readme bitnami/nats

# 3. Generate new manifests
helm template nats bitnami/nats -f updated-values.yaml > new-manifests.yaml

# 4. Review differences
diff course_project/manifests/base/nats/ new-manifests.yaml

# 5. Update base manifests
# 6. Test in development overlay
# 7. Commit to Git
# 8. Deploy and verify
```

**Monitoring Strategy**:
- **Dependabot**: GitHub alerts for base image vulnerabilities
- **Security Scanning**: Container image scanning in CI/CD
- **Chart Monitoring**: Periodic review of Bitnami NATS chart releases
- **Health Monitoring**: Azure Monitor alerts for pod health and metrics

**Alternative Approaches Considered**:
- **Pure Helm**: Would provide auto-updates but breaks GitOps principles
- **Native Manifests**: Would require rebuilding proven chart configurations
- **Flux/ArgoCD**: Would add complexity but provide automated chart updates

**Decision Rationale**: 
We prioritize GitOps compliance and declarative infrastructure over automatic updates, accepting the operational overhead of manual monitoring and updates in exchange for better observability, rollback capabilities, and environment consistency.

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
