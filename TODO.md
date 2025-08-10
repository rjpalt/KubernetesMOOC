# TODO - Project Tasks

## Overview
This document tracks tasks and features for the KubernetesMOOC project, including cleanup workflows, feature environments, and future enhancements. It is organized by status and priority to help manage development effectively.

| Task | Status | Priority | Next Action |
|------|--------|----------|-------------|
| Exercise 3.7 Cleanup | 🟡 Testing | HIGH | Test with ex-3-8 branch |
| Feature Environment Cleanup | ✅ Done | - | Complete |
| Azure Key Vault | ✅ Done | - | Complete |
| Preview Environment DNS | ⏸️ Future | MEDIUM | Plan ExternalDNS setup |
| Database Isolation | ⏸️ Future | MEDIUM | PostgreSQL per namespace |
| E2E Testing | ⏸️ Future | HIGH | Playwright setup |
| OpenAPI Docs | ⏸️ Future | LOW | GitHub Pages automation |
| GitOps Repository | ⏸️ Future | LOW | Separate config repo |

## Active Tasks

### Immediate
- [x] ~~Refactor workflows to use repository variables~~
  - **Why**: Remove hardcoded values, improve maintainability
- [ ] Test cleanup workflow with ex-3-8 branch lifecycle
  - **Why**: Verify automated cleanup works before considering done
- [ ] Document overlay maintenance in README
  - **Why**: Others need to know how to update HTTPRoute paths

### Short Term  
- [ ] Decide preview env trigger: PR-opened vs branch-created
  - **Why**: Need clear policy before implementing ExternalDNS
- [ ] Install ExternalDNS and cert-manager for preview domains
  - **Why**: Enable feature-branch.example.com URLs instead of path prefixes

### Future
- [ ] Implement database isolation per feature branch
  - **Why**: Prevent feature tests affecting each other
- [ ] Add Playwright E2E tests targeting live environments
  - **Why**: Validate complete workflows before production
- [ ] Set up GitOps with separate config repository
  - **Why**: Track actual deployed state, enable proper rollbacks

---
- [ ] Document overlay maintenance requirement (README + Azure memos)
- [ ] Consider External Secrets Operator (ESO) with Azure Key Vault; optionally HashiCorp Vault for dynamic secrets
- [ ] Decide preview env trigger: PR-opened (recommended for cost) vs. branch-created; implement chosen workflow
- [ ] Prep platform installs (cluster-wide): ExternalDNS (Azure DNS) and cert-manager (Let’s Encrypt), scoped to preview domain

---

## FUTURE: Per-feature Hostnames with ExternalDNS + cert-manager (Preview Environments)

### Why
- Avoid path-prefix crowding and rewrite complexity in Gateway API
- Consistent, human-friendly URLs per feature (feature-<branch>.preview.example.com)
- Clean TLS with per-host or wildcard certificates; simpler browser/SameSite behavior
- Better isolation boundaries and easier cleanup (DNS and certs deprovision with namespace delete)
- Clearer observability (per-host metrics/logs) and policy controls (quotas, rate limits)

### What to Implement (High Level)
- DNS
  - Choose and provision base preview domain (e.g., preview.example.com) in Azure DNS
  - Delegate if needed; ensure CI/cluster has least-privilege to manage only this zone
- ExternalDNS (cluster-wide)
  - Install with Azure DNS provider; set txt-owner-id and domain filters to preview.example.com
  - Restrict to namespaces labeled for previews; enable garbage collection
- cert-manager (cluster-wide)
  - Install and configure ClusterIssuers (Let’s Encrypt staging/prod) using DNS-01 with Azure DNS
  - Option A: Wildcard cert for *.preview.example.com
  - Option B: Per-host certificates issued on demand
- Gateway design
  - Recommended: Use a dedicated ALB/Gateway for all feature namespaces (shared preview Gateway), keep production on a separate Gateway/ALB to reduce blast radius
  - Configure AllowedRoutes/namespaceSelectors so feature namespaces can bind only their own hosts
- App routing
  - Each feature namespace defines an HTTPRoute with host: feature-<branch>.preview.example.com pointing to its services (no path rewrites)
  - Ensure frontend/backend base URLs align with host-based routing
- CI/CD automation (per feature)
  - Trigger: PR-opened (recommended) to save resources; optionally support branch-created if desired
  - Steps: create namespace → apply manifests with HOSTNAME variable → wait for ExternalDNS record + cert ready → post PR comment with URL
  - Cleanup on PR-closed: delete namespace; ExternalDNS removes DNS; cert-manager cleans up certs
- Guardrails
  - Apply resource quotas/limits per namespace; minimal replicas; autoscaling caps
  - Optional edge auth/IP allowlist for previews; baseline NetworkPolicies

### Azure-Native Provisioning Service (Recommended Enhancement)
- **Problem**: GitHub Actions directly managing Azure resources creates security and operational issues
- **Solution**: Azure Functions-based provisioning service with Azure-native identity management
- **Architecture**: GitHub Actions → OIDC → Azure Function → Provision/Cleanup Resources
- **Benefits**:
  - Reduced CI/CD permissions (only calls one Azure endpoint vs managing all resources)
  - Centralized provisioning logic with business rules, validation, resource limits
  - Better error handling, retry logic, and audit trails within Azure ecosystem
  - Consistent resource naming, tagging, and lifecycle management
  - Enhanced logging and monitoring capabilities for troubleshooting
- **Implementation**: 
  - Azure Function with Managed Identity and least-privilege Azure RBAC
  - HTTP triggers for provision/cleanup operations with structured request/response
  - Comprehensive logging with Application Insights for debugging complex scenarios
  - ARM/Bicep templates for consistent resource provisioning patterns

### Trigger Choice: PR-opened vs Branch-created
- PR-opened: More resource-savvy, aligns with review lifecycle; preferred default
- Branch-created: Faster feedback but can create unused environments; use only if contributors rely on early URLs

### Risks/Decisions
- ALB limits and cost: One shared preview ALB/Gateway vs per-env ALB; start with one shared preview ALB/Gateway and keep prod separate
- Certificate strategy: wildcard (simpler) vs per-host (granular)
- DNS permissions: scope creds to preview zone only
- Provisioning service complexity: Additional Azure component to maintain but significantly improves security posture

### Next Steps
- Decide base preview domain and add Azure DNS zone
- Approve design: shared preview ALB/Gateway, prod isolated; PR-opened trigger
- Add platform installs (ExternalDNS + cert-manager) with limited scope
- Design and implement Azure Functions provisioning service with comprehensive logging
- Add CI jobs for create/update and cleanup on PR lifecycle

---

## ⚠️ Current Limitation: Shared Database
**Current Setup**: All feature environments share the same PostgreSQL database as production.

**Problem**: Data isolation issues - feature tests can affect each other and production data.

**Future Enhancement**: Each feature environment should have its own database instance:
- **Option 1**: Azure Database for PostgreSQL per feature branch
- **Option 2**: PostgreSQL pods with persistent volumes per namespace  
- **Option 3**: In-memory databases for testing (fastest, ephemeral)

**Implementation Priority**: MEDIUM - Current shared setup works for learning/demo purposes, but proper isolation needed for real development workflows.

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