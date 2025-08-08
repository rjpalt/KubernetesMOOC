# Todo Application - Microservices Project

Two-service todo application: **todo-backend** (REST API) and **todo-app** (Frontend with image caching). The **todo-cron** service for automated Wikipedia todo generation is available but not part of current deployments.

## Architecture

- **todo-backend** (Port 8001): FastAPI REST API for todo CRUD operations
- **todo-app** (Port 8000): FastAPI frontend with HTMX UI, communicates with backend via HTTP
- **todo-cron**: CronJob service for automated Wikipedia todos (available but not currently deployed)

### Data Flow

```mermaid
graph TD
    UserBrowser -->|HTMX POST /project/todos| Gateway
    Gateway -->|/todos to Frontend| Frontend
    Frontend -->|JSON API Call| Backend
    Backend -->|JSON Response| Frontend
    Frontend -->|HTML Fragment| UserBrowser

    UserBrowser -->|GET /project/docs| Gateway
    Gateway -->|/docs to Backend| Backend
    Backend -->|Swagger UI| UserBrowser
    
    UserBrowser -->|GET /project/be-health| Gateway
    Gateway -->|/be-health to Backend| Backend
    Backend -->|JSON Health Status| UserBrowser
```

## Quick Start

```bash
# Start both services with one command
./start-services.sh

# Or manually:
cd todo-backend && uv sync && uv run python -m src.main &
cd ../todo-app && uv sync && uv run python -m src.main &
```

Access:
- Frontend: http://localhost:8000
- Backend API docs: http://localhost:8001/docs

## Security Features

### XSS Protection ✅
- **Content Security Policy (CSP)**: Strict CSP headers prevent script injection
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **Template Escaping**: Jinja2 auto-escaping prevents XSS in user content
- **Input Validation**: Malicious payloads stored safely as literal text

### SQL Injection Protection ✅  
- **SQLAlchemy ORM**: Parameterized queries prevent SQL injection
- **Input Validation**: Parameter type validation and sanitization
- **Database Integrity**: Comprehensive testing against injection attacks

### API Security
- **Request Logging**: Structured logging with correlation IDs
- **Error Handling**: Secure error responses without information disclosure
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Content Type Validation**: Proper content type enforcement

## Docker Images

### Multi-Architecture Build System

The project supports both local development (ARM64) and cloud deployment (AMD64) with clear architecture-specific image naming:

**ARM64 Images (Local Development):**
- `todo-app-fe:TAG-arm64` - Frontend service for local Docker Compose
- `todo-app-be:TAG-arm64` - Backend service for local Docker Compose  
- `todo-app-cron:TAG-arm64` - Cron service for local Docker Compose

**AMD64 Images (AKS Deployment):**
- `todo-app-fe:TAG-amd64` - Frontend service for Azure Kubernetes Service
- `todo-app-be:TAG-amd64` - Backend service for Azure Kubernetes Service
- `todo-app-cron:TAG-amd64` - Cron service (available but not deployed)

### Environment Configuration
Before running with Docker Compose, set up your environment:

```bash
# Copy the example environment file
cp docker-compose.env.example docker-compose.env

# Edit docker-compose.env with your actual values
# At minimum, set a secure POSTGRES_PASSWORD
```

### Build Both Architectures
```bash
# Build both ARM64 and AMD64 images with specific tag (recommended)
./build-images.sh v1.0.0

# Build with 'latest' tag (prompts for confirmation)
./build-images.sh
```

This creates 6 total images:
- 2 ARM64 images for local development (backend and frontend - automatically used by docker-compose.yaml)
- 2 AMD64 images for AKS deployment (backend and frontend - use in Kubernetes manifests)
- 2 cron images (available but not currently deployed)

### Manual Docker Build
```bash
# ARM64 for local development
cd todo-app && docker build --platform linux/arm64 -t todo-app-fe:v1.0.0-arm64 .
cd todo-backend && docker build --platform linux/arm64 -t todo-app-be:v1.0.0-arm64 .

# AMD64 for AKS deployment  
cd todo-app && docker build --platform linux/amd64 -t todo-app-fe:v1.0.0-amd64 .
cd todo-backend && docker build --platform linux/amd64 -t todo-app-be:v1.0.0-amd64 .
```

## Docker Compose

### Setup & Run
```bash
# 1. Set up environment (first time only)
cp docker-compose.env.example docker-compose.env
# Edit docker-compose.env with your values

# 2. Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Configuration
The application uses `docker-compose.env` for environment variables:
- **Security**: File is gitignored to prevent credential leaks
- **Flexibility**: Easy environment switching (dev/staging/prod)
- **Centralized**: All services share common configuration
- **Architecture**: Uses ARM64 images automatically for local development

### Services
- **todo-app-fe**: Frontend on http://localhost:8000 (ARM64 image)
- **todo-app-be**: Backend API on http://localhost:8001 (ARM64 image)
- **postgres_prod**: PostgreSQL database on localhost:5432
- **Persistent data**: Database data persists in Docker volumes
- **Note**: Cron service available but not included in current docker-compose setup

## Kubernetes Deployment

### Manifest Structure
The project uses a hierarchical Kustomization structure for flexible Kubernetes deployments with production-ready Azure Key Vault integration:

```
manifests/
├── base/                          # Base configurations for all environments
│   ├── postgres/                  # PostgreSQL StatefulSet with Azure Key Vault secrets
│   ├── shared/                    # Namespace and Gateway API resources
│   ├── todo-be/                   # Backend Deployment and Service
│   ├── todo-cron/                 # CronJob for automated tasks
│   └── todo-fe/                   # Frontend Deployment, Service, and PVC
└── overlays/                      # Environment-specific configurations
    ├── development/               # Development environment overrides
    ├── staging/                   # Staging environment overrides
    └── production/                # Production environment overrides
```

### Azure Key Vault Integration
The deployment uses Azure Key Vault for secure credential management:

- **Azure Managed Identity**: `keyvault-identity-kube-mooc` with Key Vault Secrets User role
- **Workload Identity**: Federated credential linking Kubernetes ServiceAccount to Azure identity
- **CSI Secrets Store Driver**: Transparent bridge between Azure Key Vault and Kubernetes Secrets
- **PostgreSQL Secrets**: Database credentials stored securely in Azure Key Vault, automatically mounted as Kubernetes secrets

**Key Vault Setup:**
```bash
# Key Vault: kube-mooc-secrets-[timestamp]
# Secrets: postgres-user, postgres-password
# Access: Passwordless authentication via Azure Workload Identity
```

### Deployment Options

**Branch-based environment deployment:**
```bash
# Main branch deploys to 'project' namespace using production overlay
kubectl apply -k manifests/overlays/production/

# Feature branches deploy to 'feature-branch-name' namespace using feature overlay
kubectl apply -k manifests/overlays/feature/
```

**Individual service deployment:**
```bash
# Deploy only the backend (when kustomization.yaml files are created)
kubectl apply -k manifests/base/todo-be/

# Deploy only the database
kubectl apply -k manifests/base/postgres/
```

**Full application deployment:**
```bash
# Deploy all services (when root kustomization.yaml is created)
kubectl apply -k manifests/

# Or manually apply each service in dependency order
kubectl apply -k manifests/base/shared/      # Namespace first
kubectl apply -k manifests/base/postgres/    # Database second
kubectl apply -k manifests/base/todo-be/     # Backend third
kubectl apply -k manifests/base/todo-fe/     # Frontend fourth
kubectl apply -k manifests/base/todo-cron/   # Cron service last
```

**Environment-specific deployments:**
```bash
# Development environment (when overlay kustomization.yaml files are created)
kubectl apply -k manifests/overlays/development/

# Production environment with different resource limits and replicas
kubectl apply -k manifests/overlays/production/
```

### Kustomization Benefits
- **Service Independence**: Deploy and update individual microservices
- **Environment Management**: Different configurations for dev/staging/prod
- **Branch Environments**: Feature branches deploy to isolated namespaces with same configuration
- **Resource Customization**: Environment-specific resource limits, replicas, and secrets
- **GitOps Ready**: Structure supports GitOps deployment patterns

### Branch Environment Strategy
The deployment pipeline creates separate environments for each branch:

- **Main Branch**: Deploys to `project` namespace using `overlays/production/`
- **Feature Branches**: Deploy to `feature-{branch-name}` namespace using `overlays/feature/`
- **Gateway Access**: Feature namespaces labeled with `gateway-access=allowed` for routing
- **Isolation**: Each feature environment is completely isolated with its own resources
- **Same Configuration**: Feature environments use identical resource limits as production
- **Automatic Cleanup**: Feature environments can be cleaned up when branches are deleted

### Service Access
- **Frontend**: Through Gateway API at `/project/` (main UI and form submissions)
- **Backend API**: Through Gateway API at `/project/docs` for Swagger UI and `/project/be-health` for monitoring
- **Todo Operations**: Form submissions via `/project/todos` route to frontend, which proxies to backend as JSON
- **Health Checks**: `/project/be-health` endpoint routes directly to backend for monitoring
- **Security**: All database credentials managed through Azure Key Vault

### Gateway API Routing
The HTTPRoute configuration provides intelligent routing:
- `/project/todos` → Frontend service (handles form data conversion to JSON)
- `/project/be-health` → Backend service (direct health check access)
- `/project/docs` → Backend service (API documentation)
- `/project/image*` → Frontend service (image caching functionality)
- `/project/` → Frontend service (main UI and catch-all)

## Azure Deployment

### Azure Resources
- **Resource Group**: `kubernetes-learning` (North Europe region)
- **AKS Cluster**: `kube-mooc` (1 node, monitoring enabled)
- **Azure Key Vault**: `kube-mooc-secrets-[timestamp]` for secure credential storage
- **Managed Identity**: `keyvault-identity-kube-mooc` with Key Vault access
- **Gateway API**: Azure Application Load Balancer integration
- **Location**: North Europe

### Security Architecture
- **Passwordless Authentication**: Azure Workload Identity eliminates hard-coded credentials
- **Secret Rotation**: Azure Key Vault supports automated credential rotation
- **RBAC**: Fine-grained access control with Azure managed identities
- **Audit Trail**: All secret access logged in Azure Activity Log

### Prerequisites
- Azure CLI installed and authenticated
- kubectl configured for the AKS cluster
- **Docker images**: Use AMD64 variants (TAG-amd64) pushed to a container registry (Azure Container Registry)
- Azure Key Vault configured with database credentials
- CSI Secrets Store Driver enabled on AKS cluster
- Azure Workload Identity configured for passwordless authentication

## Testing

### Run All Tests
```bash
# All tests with one command
./test-all.sh

# Individual services
./test-be.sh     # Backend tests (95 tests)
./test-fe.sh     # Frontend tests

# Or manually (from course_project/todo-backend):
cd todo-backend && uv run pytest tests/ -v
cd ../todo-app && uv run pytest tests/ -v
```

### Test Coverage
- **Backend**: 95 tests covering unit tests, integration tests, API validation, security
- **Frontend**: 49 tests covering contract tests, service integration, UI components, security
- **Security**: 20 tests specifically for XSS and SQL injection prevention
- **Philosophy**: Each service tested independently for microservice isolation

See `todo-backend/tests/TEST_PLAN.md` for comprehensive testing documentation.

## CI/CD Pipeline

Modern GitOps-style pipeline with **separate Azure identities** for CI and CD stages, following security best practices:

### Azure Identity Architecture

The pipeline uses **two dedicated Azure Managed Identities** for secure, passwordless authentication:

#### CI Identity (`github-actions-ci`)
- **Purpose**: Build and push tested images during pull request validation
- **Permissions**: `AcrPush` role on Azure Container Registry only
- **Scope**: Triggered by `pull_request` events on any branch
- **Client ID**: `a7c70b35-0eb3-4363-b0e1-1c48bae476cc`
- **Security**: Minimal permissions following principle of least privilege

#### CD Identity (`github-actions-todo-cd`)  
- **Purpose**: Deploy applications to AKS after main branch merge
- **Permissions**: AKS deployment permissions + ACR access
- **Scope**: Triggered only by pushes to `main` branch
- **Client ID**: `d2e20c1d-c71a-43d8-ba21-463212e9596f`  
- **Security**: Broader permissions but restricted to production deployments

**Why Separate Identities?**
- **Blast Radius Control**: Compromised CI identity cannot deploy to production
- **Future-Proof**: Ready for separate test databases and staging clusters
- **Audit Clarity**: Clear separation between build and deployment activities
- **Permission Scoping**: Each stage has only the minimum required access

### Pipeline Architecture
```mermaid
graph TD
    A[Push/PR to any branch] --> B[CI Pipeline - Microservices]
    B --> C{All tests pass?}
    C -->|Yes| D[Build & Push Images to ACR]
    D --> E{Branch type?}
    E -->|main branch| F[Production Deployment]
    E -->|feature branch| G[Feature Branch Deployment]
    F --> H[Deploy to project namespace]
    G --> I[Deploy to feature-{branch} namespace]
    C -->|No| J[Pipeline fails - no deployment]
```

### CI Pipeline (`ci.yml`)
Sequential testing strategy with secure image building:
1. **Code Quality**: Ruff linting and formatting for both services
2. **Backend Tests**: Unit and integration tests with PostgreSQL
3. **Frontend Tests**: Service integration with mocked backend
4. **Service Integration**: Docker containers with real service communication
5. **Image Building**: Build and push tested images to ACR using **CI identity**

**Authentication Architecture:**
- Uses `AZURE_CI_CLIENT_ID` secret with `pull_request` federated credential
- Federated credential subject: `repo:rjpalt/KubernetesMOOC:pull_request`
- Permissions: `AcrPush` role only (cannot deploy to AKS)
- Scope: Triggered on ANY pull request to main branch

**Services Covered:**
- **Backend**: `kubemooc.azurecr.io/todo-app-be:{branch}-{sha}`
- **Frontend**: `kubemooc.azurecr.io/todo-app-fe:{branch}-{sha}`

**Key Features:**
- **Only tested code is built** - Images only created after all tests pass
- **Consistent tagging** - `kubemooc.azurecr.io/todo-app-be:feature-my-branch-abc123def`
- **Multi-platform** - AMD64 images for AKS deployment
- **Build cache** - GitHub Actions cache for faster subsequent builds
- **Secure by default** - Minimal Azure permissions for CI operations

### Branch Environment Deployment
Two separate deployment pipelines ensure proper isolation:

#### Production Deployment (`deploy-production.yml`)
- **Trigger**: Push to main branch (merge from PR)
- **Authentication**: Uses `AZURE_CLIENT_ID` secret with **CD identity**
- **Federated Credential**: `repo:rjpalt/KubernetesMOOC:ref:refs/heads/main`
- **Permissions**: Full AKS deployment + ACR access
- **Target**: `project` namespace using `overlays/production/`
- **Images**: Builds fresh images for production (independent validation)
- **Tests**: Runs own test suite before deployment
- **Strategy**: Independent pipeline for production reliability

#### Feature Branch Deployment (`deploy-feature-branches.yml`)  
- **Trigger**: After CI pipeline completes successfully (non-main branches)
- **Authentication**: Uses `AZURE_CLIENT_ID` secret with **CD identity**
- **Images**: Uses tested images from CI pipeline (no rebuilding)
- **Target**: `feature-{branch-name}` namespace using `overlays/feature/`
- **Services**: Deploys backend and frontend services only
- **Namespace**: Auto-creates with `gateway-access=allowed` label
- **Health Checks**: Verifies both services respond correctly

**Benefits:**
- **Integration Testing**: Test features in production-like environment
- **Stakeholder Review**: Product managers can test features before merge
- **Parallel Development**: Multiple developers work on features simultaneously
- **E2E Testing Foundation**: Perfect environment for automated end-to-end tests
- **No Duplicate Work**: Uses images that were already tested in CI

### Identity Architecture Benefits

**Current Shared Infrastructure:**
- Both CI and CD use same ACR (`kubemooc.azurecr.io`) and AKS cluster (`kube-mooc`)
- Feature and production environments share underlying Azure resources
- Separate identities provide security isolation despite shared infrastructure

**Future Infrastructure Evolution:**
```mermaid
graph TD
    A[Current: Shared Infrastructure] --> B[Future: Isolated Infrastructure]
    
    A --> A1[CI: ACR Push Only]
    A --> A2[CD: AKS Deploy + ACR]
    
    B --> B1[CI: Feature ACR + Test DB]
    B --> B2[CD: Prod ACR + Prod Cluster]
    
    A1 --> B1
    A2 --> B2
```

**Migration Path:**
- **Today**: Both identities access same resources with different permission scopes
- **Tomorrow**: Each identity can be granted access to environment-specific resources
- **No Refactoring**: Pipeline code remains unchanged during infrastructure evolution
- **Clean Separation**: CI concerns (build/test) separate from CD concerns (deploy/monitor)

### Local CI Testing with ACT

Test GitHub Actions pipeline locally using [act](https://github.com/nektos/act):

```bash
# Test specific jobs
act --job test-backend
act --job test-frontend
act --job code-quality
```

#### ACT Setup Requirements

ACT requires a `.secrets` file for local testing with GitHub secrets:

```bash
# Copy the example secrets file
cp .secrets.example .secrets

# Or create manually (this file is gitignored)
cat > .secrets << EOF
TEST_POSTGRES_USER=test_user
TEST_POSTGRES_PASSWORD=test_password123
EOF
```

The workflow automatically detects ACT execution (`github.actor == 'nektos/act'`) and sets appropriate environment variables for database testing.

## Features

- Todo CRUD operations with 140-character validation
- Automatic image fetching from picsum.photos
- Health check endpoints for monitoring
- OpenAPI documentation for both services
- **Security**: XSS prevention, SQL injection protection, security headers
- **Testing**: Comprehensive test coverage including security testing
- **Observability**: Request logging with correlation IDs
- Codecov on project pages for front and backend coverage
