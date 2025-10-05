# Cluster-Level Manifests

This directory contains cluster-wide infrastructure configurations that operate independently of application deployments. These manifests manage shared services, security policies, and GitOps infrastructure.

## Directory Structure

```
cluster-manifests/
├── README.md                           # This documentation
├── main-app.yaml                       # ArgoCD Application for production GitOps
├── argocd-application-staging.yaml     # ArgoCD Application for staging GitOps
├── argocd-server-loadbalancer.yaml     # ArgoCD UI LoadBalancer service
├── cluster-protection-rbac.yaml        # Cluster-wide RBAC security policies
├── agc-gateway.yaml                    # Azure Application Gateway for Containers
├── agc-httproute.yaml                  # Main HTTPRoute for production traffic
├── agc-httproute-template.yaml         # Template for feature branch HTTPRoutes
├── agc-httproute-nip-io-test.yaml      # Test HTTPRoute with nip.io DNS
├── agc-test-app.yaml                   # Test application for gateway validation
├── k8s-nsa2-gateway.yaml              # Alternative Gateway API configuration
└── nsa2-alb.yaml                       # Alternative ALB configuration
```

## GitOps Infrastructure

### Multi-Environment GitOps Strategy

The cluster uses ArgoCD to manage deployments across multiple environments with identical GitOps patterns but environment-specific configurations.

### Production Application (`main-app.yaml`)

**Purpose**: Manages production todo-application stack via GitOps principles.

**Configuration**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: main-app
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/rjpalt/KubernetesMOOC.git
    targetRevision: main
    path: course_project/manifests/overlays/production
  destination:
    namespace: project
```

**Key Features**:
- **Automated Sync**: `syncPolicy.automated` enables continuous deployment
- **Self-Healing**: Automatically corrects configuration drift
- **Prune Policy**: Removes resources deleted from Git
- **Ignore Rules**: Excludes HPA replica counts from sync operations

**Managed Resources**: 29+ Kubernetes resources including:
- Deployments (todo-backend, todo-frontend, broadcaster)
- Services and networking (HTTPRoutes, Services)
- Configuration (ConfigMaps, Secrets via Azure Key Vault)
- NATS message broker infrastructure

**Infrastructure**:
- **Database**: Azure Database for PostgreSQL (dedicated production server)
- **Gateway**: Azure Application Gateway for Containers
- **URL**: http://d9hqaucbbyazhfem.fz53.alb.azure.com/project/
- **Resources**: Full production capacity (3000m CPU, 3072Mi memory)

**Deployment Status**: ✅ Production Ready
- **Sync Status**: Synced
- **Health Status**: Healthy
- **Last Sync**: Automated on Git commits to main branch

### Staging Application (`argocd-application-staging.yaml`)

**Purpose**: Manages staging environment for pre-production validation.

**Configuration**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: staging-app
  namespace: argocd
  labels:
    environment: staging
spec:
  source:
    repoURL: https://github.com/rjpalt/KubernetesMOOC.git
    targetRevision: main
    path: course_project/manifests/overlays/staging
  destination:
    namespace: staging
```

**Key Features**:
- **Identical GitOps Pattern**: Same sync policies as production
- **Cost-Optimized**: Reduced resource limits (2000m CPU, 2048Mi memory)
- **Isolated Database**: Separate database on shared feature server
- **Independent Routing**: Hostname-based routing (staging.23.98.101.23.nip.io)

**Managed Resources**: Same 29+ resource types as production with staging-specific configuration:
- **HPA Limits**: maxReplicas: 2 (vs 3 in production)
- **NATS Replicas**: 1 (vs 3 in production for cost optimization)
- **Database**: todoapp_staging on kubemooc-postgres-feature
- **Secrets**: postgres-secret-staging via Azure Key Vault

**Infrastructure**:
- **Database**: Azure Database for PostgreSQL (shared feature server, dedicated database)
- **Gateway**: Azure Application Gateway for Containers (AGC)
- **URL**: http://staging.23.98.101.23.nip.io/
- **Resources**: 67% of production capacity

**Deployment Status**: Ready for DevOps deployment
- **Template**: Available in cluster-manifests/
- **Validation**: Manifests validated via kustomize build
- **Action Required**: Apply ArgoCD Application to enable GitOps

### Environment Comparison

| Aspect | Production | Staging | Feature Branches |
|--------|-----------|---------|------------------|
| **ArgoCD Managed** | Yes (main-app) | Yes (staging-app) | No (Azure Function) |
| **Namespace** | project | staging | feature-{branch} |
| **Database** | Production DBaaS | Feature DBaaS (dedicated DB) | Feature DBaaS (dynamic DB) |
| **Max Replicas** | 3 | 2 | 1 |
| **NATS Replicas** | 3 | 1 | 1 |
| **Gateway** | AGC | AGC | AGC |
| **Routing** | Path-based (/project/) | Hostname (staging.nip.io) | Hostname (feature-x.nip.io) |
| **Resources** | 3000m CPU | 2000m CPU | 1000m CPU |

### ArgoCD Access (`argocd-server-loadbalancer.yaml`)

**Purpose**: Provides external access to ArgoCD UI for GitOps management.

**Configuration**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: argocd-server-loadbalancer
  namespace: argocd
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
```

**Access**: https://20.54.1.117 (Azure LoadBalancer IP)
**Security**: Default ArgoCD authentication required

## Security Infrastructure

### Cluster Protection RBAC (`cluster-protection-rbac.yaml`)

**Purpose**: Implements cluster-wide security policies and access controls.

**Key Components**:
- **ServiceAccounts**: Dedicated service accounts for different functions
- **ClusterRoles**: Cluster-wide permission definitions
- **ClusterRoleBindings**: Association of roles with service accounts
- **RBAC Policies**: Principle of least privilege enforcement

**Security Features**:
- Namespace isolation enforcement
- Resource access restrictions
- API server protection policies
- Cross-namespace communication controls

## Gateway Infrastructure

### Azure Application Gateway for Containers

The cluster uses Azure Application Gateway for Containers (AGC) as the primary ingress solution, providing enterprise-grade load balancing and traffic management.

#### Main Gateway (`agc-gateway.yaml`)

**Purpose**: Primary production gateway for todo-application traffic.

**Configuration**:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: gateway
  namespace: project
spec:
  gatewayClassName: azure-alb-external
```

**Features**:
- **Azure Integration**: Native Azure Application Gateway backend
- **TLS Termination**: HTTPS support with Azure-managed certificates
- **High Availability**: Multi-zone load balancing
- **Health Probes**: Automatic health checking of backend services

#### Production HTTPRoute (`agc-httproute.yaml`)

**Purpose**: Routes production traffic to todo-application services.

**Configuration**:
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: todo-app-route
  namespace: project
spec:
  parentRefs:
  - name: gateway
  hostnames:
  - "d9hqaucbbyazhfem.fz53.alb.azure.com"
```

**Routing Rules**:
- **Frontend**: `/project/*` → `todo-frontend-svc:8080`
- **Backend Health**: `/be-health` → `todo-backend-svc:8002`
- **Backend API**: `/project/api/*` → `todo-backend-svc:8002`

**Production URL**: http://d9hqaucbbyazhfem.fz53.alb.azure.com/project/

#### Feature Branch Support

**Template HTTPRoute** (`agc-httproute-template.yaml`):
- **Purpose**: Template for dynamic feature branch routing
- **Pattern**: Uses `BRANCH_NAME` placeholder for Azure Function replacement
- **DNS**: Utilizes nip.io for dynamic subdomain routing
- **Usage**: Enables isolated testing environments per feature branch

**Test HTTPRoute** (`agc-httproute-nip-io-test.yaml`):
- **Purpose**: Validation of nip.io DNS routing patterns
- **Configuration**: Static test configuration for gateway validation

### Alternative Gateway Configurations

#### Kubernetes Gateway API (`k8s-nsa2-gateway.yaml`)

**Purpose**: Standard Kubernetes Gateway API implementation for comparison.

**Use Case**: Provides vendor-neutral gateway configuration as fallback option.

#### Network Security Appliance (`nsa2-alb.yaml`)

**Purpose**: Alternative ALB configuration with enhanced security features.

**Features**:
- **WAF Integration**: Web Application Firewall policies
- **DDoS Protection**: Enhanced traffic filtering
- **Security Rules**: Custom security policy enforcement

## Deployment Strategy

### Infrastructure-as-Code

All cluster manifests follow Infrastructure-as-Code principles:

1. **Version Controlled**: All configurations stored in Git
2. **Declarative**: Resources defined in YAML manifests
3. **Immutable**: Changes deployed via Git commits
4. **Auditable**: Complete change history preserved

### Deployment Process

**Manual Infrastructure Deployment** (One-time):
```bash
# Deploy ArgoCD Application (enables GitOps for applications)
kubectl apply -f cluster-manifests/main-app.yaml

# Deploy cluster security policies
kubectl apply -f cluster-manifests/cluster-protection-rbac.yaml

# Deploy gateway infrastructure
kubectl apply -f cluster-manifests/agc-gateway.yaml
kubectl apply -f cluster-manifests/agc-httproute.yaml
```

**Automated Application Deployment** (Continuous):
- ArgoCD monitors `course_project/manifests/overlays/production`
- Git commits trigger automatic synchronization
- Applications deploy without manual intervention

### Operational Status

**Current State**: ✅ Production Ready

**Active Resources**:
- ✅ ArgoCD Application managing 29+ application resources
- ✅ Azure Application Gateway providing external access
- ✅ RBAC policies enforcing security boundaries
- ✅ Production HTTPRoute handling traffic routing

**Monitoring**:
- ArgoCD UI: https://20.54.1.117
- Application health: Automatic via ArgoCD health checks
- Gateway status: Azure portal monitoring

## Maintenance & Updates

### Regular Maintenance Tasks

1. **ArgoCD Updates**: Monitor ArgoCD releases and update when necessary
2. **Gateway Configuration**: Review and update routing rules as needed
3. **Security Policies**: Regular review of RBAC configurations
4. **SSL Certificates**: Monitor certificate expiration (Azure-managed)

### Troubleshooting

**Common Issues**:

1. **ArgoCD Sync Failures**:
   ```bash
   kubectl get applications -n argocd
   kubectl describe application main-app -n argocd
   ```

2. **Gateway Connectivity**:
   ```bash
   kubectl get gateway -n project
   kubectl describe httproute todo-app-route -n project
   ```

3. **RBAC Permission Issues**:
   ```bash
   kubectl auth can-i <verb> <resource> --as=<user>
   ```

**Log Access**:
- ArgoCD logs: `kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server`
- Gateway logs: Azure portal → Application Gateway logs

## Security Considerations

### Access Controls

- **ArgoCD**: Admin access required for GitOps management
- **Cluster Resources**: RBAC policies enforce least privilege
- **Gateway**: Azure-managed security policies and WAF rules

### Network Security

- **Ingress**: All external traffic filtered through Azure Application Gateway
- **Egress**: Controlled via network policies and firewall rules
- **Internal**: Namespace isolation enforced via RBAC

### Compliance

- **Audit Trail**: All changes tracked in Git history
- **Access Logging**: ArgoCD and Azure gateway provide comprehensive logs
- **Policy Enforcement**: Automated policy validation via ArgoCD

---

**Maintained by**: Platform Team  
**Last Updated**: September 28, 2025  
**Status**: Production Ready ✅