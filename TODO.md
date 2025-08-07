# TODO: Priority Tasks for Tomorrow

## Goal: Deploy Complete Todo Application Stack to AKS with Kustomization
**End State**: Individual service deployments + full stack deployment capability using hierarchical Kustomization structure with Azure Key Vault integration.

### Phase 1: Container Images & Registry
- [x] Build application images with consistent versioning (v3.5)
  ```bash
  ./build-images.sh v3.5
  ```
- [x] Tag images for Azure Container Registry
  ```bash
  docker tag todo-app-be:3.5 kubemooc.azurecr.io/todo-app-be:3.5
  docker tag todo-app-fe:3.5 kubemooc.azurecr.io/todo-app-fe:3.5
  docker tag todo-app-cron:3.5 kubemooc.azurecr.io/todo-app-cron:3.5
  ```
- [x] Push all images to ACR
  ```bash
  az acr login --name kubemooc
  docker push kubemooc.azurecr.io/todo-app-be:3.5
  docker push kubemooc.azurecr.io/todo-app-fe:3.5
  docker push kubemooc.azurecr.io/todo-app-cron:3.5
  ```

### Phase 2: Update Kubernetes Manifests
- [x] **Backend Service** (`manifests/base/todo-be/`)
  - [x] Update deployment.yaml with ACR image reference
  - [x] Configure database connection to use Azure Key Vault secrets
  - [x] Update service.yaml for proper port exposure
  - [x] Create/verify kustomization.yaml for independent deployment

- [x] **Frontend Service** (`manifests/base/todo-fe/`)
  - [x] Update deployment.yaml with ACR image reference
  - [x] Configure backend API endpoint for AKS internal communication
  - [x] Update service.yaml for Gateway API routing
  - [x] Create/verify kustomization.yaml for independent deployment

- [x] **Cron Job Service** (`manifests/base/todo-cron/`)
  - [x] Update cronjob.yaml with ACR image reference
  - [x] Configure backend API endpoint for internal cluster communication
  - [x] Create/verify kustomization.yaml for independent deployment

### Phase 3: Kustomization Structure Validation
- [x] **Service-Level Kustomizations**
  - [x] Test individual service deployment: `kubectl apply -k manifests/base/todo-be/`
  - [x] Test individual service deployment: `kubectl apply -k manifests/base/todo-fe/`
  - [x] Test individual service deployment: `kubectl apply -k manifests/base/todo-cron/`

- [ ] **Full Stack Kustomization**
  - [ ] Create root `manifests/kustomization.yaml` that includes all base services
  - [ ] Define proper deployment order (postgres → backend → frontend → cron)
  - [ ] Test full stack deployment: `kubectl apply -k manifests/`

### Phase 4: Gateway API Integration  
- [ ] **HTTPRoute Configuration**
  - [ ] Create/update HTTPRoute for frontend service routing (`/` → todo-frontend-svc)
  - [ ] Create/update HTTPRoute for backend API routing (`/todos`, `/be-health` → todo-backend-svc)
  - [ ] Apply Gateway API routes and verify functionality

### Phase 5: End-to-End Testing
- [ ] **Individual Service Testing**
  - [ ] Deploy and test backend independently
  - [ ] Deploy and test frontend independently  
  - [ ] Deploy and test cron job independently

- [ ] **Full Stack Testing**
  - [ ] Deploy complete application stack with single command
  - [ ] Verify frontend loads and can create todos
  - [ ] Verify backend API endpoints work through Gateway
  - [ ] Verify cron job creates Wikipedia todos automatically
  - [ ] Test data persistence through PostgreSQL with Azure Key Vault credentials

### Success Criteria
✅ **Service Independence**: Each service can be deployed/updated individually
✅ **Full Stack Deployment**: Single command deploys entire application  
✅ **Azure Integration**: All services use ACR images and Azure Key Vault secrets
✅ **Gateway API**: External access works through Azure Application Load Balancer
✅ **Data Persistence**: Todos persist across deployments using Azure Key Vault secured database

---

# TODO: OpenAPI Documentation Automation (FUTURE)

## Goal
Automatically extract OpenAPI specs from todo-app and todo-backend services, centralize them in course_project root, and publish via GitHub Pages with automatic updates on main branch merges.

## Prerequisites to Setup First
- [ ] Enable GitHub Pages for this repository
- [ ] Enable GitHub Actions for this repository
- [ ] Verify docker-compose.yaml works for both services

## Implementation Plan

### Phase 1: Directory Structure Setup
```
course_project/
├── docs/
│   ├── api/
│   │   ├── todo-app-openapi.json
│   │   └── todo-backend-openapi.json
│   └── index.html (Swagger UI)
├── scripts/
│   └── extract-openapi.sh
└── .github/
    └── workflows/
        └── update-openapi.yml
```

### Phase 2: Manual Process (Learning)
- [ ] Create docs/api/ directory structure
- [ ] Write script to start services via docker-compose
- [ ] Write script to fetch OpenAPI specs from running services
  - todo-app: http://localhost:8000/openapi.json
  - todo-backend: http://localhost:8001/openapi.json
- [ ] Create basic Swagger UI HTML page
- [ ] Test manual process locally

### Phase 3: GitHub Actions Automation
- [ ] Create workflow file (.github/workflows/update-openapi.yml)
- [ ] Use existing GitHub Actions:
  - `docker/compose-action` - Start services with docker-compose
  - `stefanzweifel/git-auto-commit-action` - Auto-commit if specs changed
  - `peaceiris/actions-gh-pages` - Deploy to GitHub Pages

### Phase 4: Workflow Logic
1. **Trigger**: On push to main branch
2. **Health Check**: Wait for services to be ready (ports 8000/8001)
3. **Extract**: Fetch /openapi.json from both services
4. **Compare**: Check if specs have actually changed (not just timestamps)
5. **Commit**: Auto-commit updated specs if changed
6. **Deploy**: Update GitHub Pages with new Swagger UI

### Key GitHub Actions to Use
- `docker/compose-action` - Service orchestration
- `stefanzweifel/git-auto-commit-action` - Git automation
- `peaceiris/actions-gh-pages` - Pages deployment
- Custom scripts for OpenAPI extraction and comparison

### Questions to Address During Implementation
1. Service startup time and health check strategy
2. Change detection logic (ignore timestamps, focus on actual API changes)
3. Swagger UI layout (single page vs separate pages for each service)
4. Error handling if services fail to start in CI

### Expected Outcome
- Automated API documentation that stays current with code
- Public Swagger UI accessible via GitHub Pages
- Zero-maintenance documentation pipeline
- Learning experience with GitHub Actions and OpenAPI workflows

---
**Next Steps**: Enable GitHub Pages and Actions, then start with Phase 1 directory setup.

---

# TODO: Azure Key Vault Integration for AKS Deployment

## Current Status: COMPLETED ✅
- [x] Azure Key Vault creation and configuration
- [x] Workload Identity for pod-to-Azure authentication  
- [x] CSI Secrets Store Driver for mounting secrets in Kubernetes
- [x] SecretProviderClass resource definition
- [x] Database connection string management
- [x] PostgreSQL StatefulSet deployed and running with Azure Key Vault integration

## Implementation Results
✅ **Azure Key Vault**: `kube-mooc-secrets-[timestamp]` created and configured
✅ **Managed Identity**: `keyvault-identity-kube-mooc` with proper RBAC
✅ **Database Secrets**: `postgres-user` and `postgres-password` stored securely
✅ **Workload Identity**: Federated credential configured for passwordless authentication
✅ **PostgreSQL Deployment**: Running successfully with Azure Key Vault credentials

**Status**: Production-ready secret management implemented. Ready for application service deployment.

---

# TODO: GitOps Repository Implementation (FUTURE)

## Problem Statement
**Current Issue**: Manifests use placeholder tags that drift from actual deployed state. Local deployments intentionally broken to enforce CI/CD-only workflow.

## GitOps Solution Overview
**Concept**: Separate application code repository from configuration repository, with CI/CD pipeline automatically updating config repo with real image tags.

### Architecture
```
App Repo (this one)           Config Repo (separate)
├── src/                     ├── manifests/
├── Dockerfile              │   ├── todo-backend/
└── .github/workflows/      │   ├── todo-frontend/
    └── build.yml           │   └── todo-cron/
                            └── .github/workflows/
                                └── deploy.yml
```

### Implementation Plan
- [ ] **Create separate config repository** (`KubernetesMOOC-config`)
- [ ] **Move manifests** from app repo to config repo
- [ ] **Update CI/CD pipeline** to commit real image tags to config repo
- [ ] **Deploy ArgoCD/Flux** to watch config repo and auto-deploy changes
- [ ] **Remove placeholder tags** - config repo always has real, deployable manifests

### Benefits
✅ **Git reflects reality**: Config repo always shows actual deployed state  
✅ **Local deployment works**: Real tags mean `kubectl apply` works again  
✅ **Audit trail**: All changes tracked in Git history  
✅ **Rollback capability**: Git revert = instant rollback  
✅ **Multi-environment**: Same pattern for dev/staging/prod with different branches

### Learning Progression
```
Current: App Repo + Placeholder Tags → GitOps: App Repo + Config Repo + ArgoCD
```

**Status**: Planned for later exercises after mastering basic Kubernetes concepts.

---

# TODO: OpenAPI Documentation Automation (FUTURE)