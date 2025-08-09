# TODO: Exercise 3.7 Completion

## URGENT: Debug Current Issues - DIAGNOSED ✅
- [x] **Backend pods failing**: CreateContainerConfigError → Missing postgres-secret in feature namespace
- [x] **Postgres not starting**: ContainerCreating stuck → Azure Key Vault auth failure (wrong namespace)
- [x] **Cron job spam**: ImagePullBackOff every minute → Disabled cronjob ✅
- [x] **Check which namespace**: feature-ex-3-7 ✅
- [x] **Debug secrets/config issues**: Root cause identified ✅

## Root Cause Analysis ✅
**Problem**: Azure Key Vault Workload Identity only configured for `project` namespace, but feature environments use `feature-*` namespaces.

**Error**: `No matching federated identity record found for presented assertion subject 'system:serviceaccount:feature-ex-3-7:postgres-service-account'`

**Solution**: Copy `postgres-secret` from `project` namespace to feature namespace in deployment workflow.

## Fixed in Workflow ✅
Added step in `deploy-feature-branches.yml` to copy database secret:
```yaml
- name: Copy database secret to feature namespace
  run: |
    kubectl get secret postgres-secret -n project -o yaml | \
      sed 's/namespace: project/namespace: ${{ env.NAMESPACE }}/' | \
      sed '/resourceVersion:/d' | sed '/uid:/d' | sed '/creationTimestamp:/d' | \
      sed '/ownerReferences:/,+4d' | kubectl apply -f -
```

## ⚠️ Current Implementation Issues

### 1. Kustomization Overlay Route Management - MEDIUM PRIORITY
**Problem**: HTTPRoute patches are hardcoded in `course_project/manifests/overlays/feature/kustomization.yaml`
```yaml
patches:
  - target:
      kind: HTTPRoute
      name: todo-app
    patch: |-
      - op: replace
        path: /spec/rules/0/matches/0/path/value
        value: /feature-BRANCH_NAME/be-health
      - op: replace
        path: /spec/rules/1/matches/0/path/value
        value: /feature-BRANCH_NAME/docs/
      # ... 3 more hardcoded endpoints
```

**Issues**:
- **Maintenance Overhead**: New API endpoints require manual addition to overlay patches
- **Documentation Gap**: Requirement not documented for developers
- **Error Prone**: Easy to forget updating overlay when adding new routes
- **Scaling Issue**: Multiple overlays (dev/staging/prod) would need sync

**Solutions**:
- [ ] Document overlay maintenance requirement in development guidelines
- [ ] Create pre-commit hook to validate overlay completeness
- [ ] Consider dynamic HTTPRoute generation from base route definitions
- [ ] Add CI check to ensure overlay patches match base HTTPRoute rules

### 2. Azure Federated Credential Lifecycle Management - HIGH PRIORITY  
**Problem**: Federated credentials created per feature branch but never cleaned up

**Current Behavior**:
```bash
# Creates: postgres-workload-identity-{branch-name}
az identity federated-credential create \
  --name "postgres-workload-identity-${{ env.BRANCH_NAME }}"

# Only deletes on deployment FAILURE, not on branch deletion/merge
```

**Issues**:
- **Resource Leak**: Accumulating federated credentials in Azure AD
- **Security Risk**: Orphaned credentials for deleted branches
- **Azure Limits**: May hit federated credential limits per managed identity
- **Cost**: Unnecessary Azure AD resources consuming quota

**Solutions**:
- [ ] **Immediate**: Create cleanup workflow triggered on branch deletion
- [ ] **Medium-term**: Create cleanup workflow triggered on PR merge to main
- [ ] **Long-term**: Consider shared credential approach with namespace-based subject patterns
- [ ] **Monitoring**: Add Azure CLI script to list and identify orphaned credentials

### 3. Missing Cleanup Workflows - HIGH PRIORITY
**Problem**: No automation for cleaning up feature environment resources

**Missing Cleanup Events**:
- Branch deletion (most important)
- PR merge to main
- Manual cleanup capability
- Periodic cleanup of old resources

**Resources Needing Cleanup**:
- Azure federated credentials (`postgres-workload-identity-{branch}`)
- Kubernetes namespaces (`feature-{branch}`)
- Container images (optional - registry cleanup)

**Implementation Plan**:
```yaml
# .github/workflows/cleanup-feature-branch.yml
name: Cleanup Feature Branch Resources
on:
  delete:
    branches:
      - '*'
  pull_request:
    types: [closed]
    branches: [main]
```

## ⚠️ Current Limitation: Shared Database
**Current Setup**: All feature environments share the same PostgreSQL database as production.

**Problem**: Data isolation issues - feature tests can affect each other and production data.

**Future Enhancement**: Each feature environment should have its own database instance:
- **Option 1**: Azure Database for PostgreSQL per feature branch
- **Option 2**: PostgreSQL pods with persistent volumes per namespace  
- **Option 3**: In-memory databases for testing (fastest, ephemeral)

**Implementation Priority**: MEDIUM - Current shared setup works for learning/demo purposes, but proper isolation needed for real development workflows.

## Debug Commands
```bash
kubectl describe pod <backend-pod-name>
kubectl describe pod postgres-statefulset-0
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get namespaces
```

## Next Steps (After Debugging)
- [ ] Wait for CI completion on PR #15
- [ ] Verify feature deployment works (namespace: feature-ex-3-7)
- [ ] Merge PR #15 to main
- [ ] Verify main branch deployment still works
- [ ] Submit exercise 3.7

## What We Fixed
- Image tagging (head SHA consistency)
- Branch naming (ex-3.7 → ex-3-7 for Kubernetes)
- Deployment names in workflow
- Workflow file location (pushed to main)


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

# TODO: Feature Environment Database Isolation (FUTURE)

## Current Limitation
All feature environments share the same PostgreSQL database as production, creating potential data conflicts and test isolation issues.

## Proposed Solutions

### Option 1: Azure Database for PostgreSQL per Feature Branch
```yaml
# In deployment workflow
- name: Create feature database
  run: |
    # Create Azure Database for PostgreSQL Flexible Server
    az postgres flexible-server create \
      --name "todo-db-feature-${BRANCH_NAME}" \
      --resource-group kubernetes-learning \
      --sku-name Standard_B1ms \
      --storage-size 32 \
      --tier Burstable \
      --database-name todoapp
```

### Option 2: PostgreSQL StatefulSet per Namespace
```yaml
# Deploy dedicated postgres instance in each feature namespace
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-statefulset
  namespace: feature-branch-name
```

### Option 3: Ephemeral In-Memory Database
```yaml
# Use SQLite or in-memory postgres for fast, isolated testing
env:
  - name: DATABASE_URL
    value: "sqlite:///tmp/feature_test.db"
```

## Implementation Considerations
- **Cost**: Option 1 most expensive, Option 3 cheapest
- **Speed**: Option 3 fastest startup, Option 1 slowest
- **Isolation**: All options provide full isolation
- **Persistence**: Options 1&2 persist data, Option 3 ephemeral
- **Production Similarity**: Option 1 most similar to production

## Recommended Approach
Start with **Option 2** (StatefulSet per namespace) for good balance of isolation, cost, and production similarity.

---

# TODO: Playwright E2E Testing with Feature Branch Environments

## High-Level Implementation
- **CI/CD Extension**: Add E2E job after feature environment deployment
- **Test Target**: Live feature environments via Gateway API (not mocks)
- **Pipeline Flow**: CI → Deploy → E2E Tests → Block/Allow PR merge
- **Kubernetes Integration**: Test against real services in isolated namespaces

## Key Benefits
- Validates complete user workflows before production
- Leverages existing feature environment infrastructure
- Fast feedback loop (~10-15 minutes from push to results)
- Production-like testing with real Gateway API routing

## Implementation Steps
1. Add Playwright tests in `course_project/e2e-tests/`
2. Extend `ci.yml` with E2E job after deployment
3. Configure tests to target feature environment URLs
4. Set up test result reporting and PR blocking

**Priority**: HIGH - Natural next step for production readiness
**Effort**: MEDIUM - Builds on existing infrastructure

---

# TODO: OpenAPI Documentation Automation (FUTURE)