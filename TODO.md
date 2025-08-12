# TODO - Project Tasks

## Overview
This document tracks tasks and features for the KubernetesMOOC project, including cleanup workflows, feature environments, and future enhancements. It is organized by status and priority to help manage development effectively.

| Task | Status | Priority | Next Action |
|------|--------|----------|-------------|
| Review Deployment Pipelines | 🔄 Active | **CRITICAL** | Audit workflows with Copilot |
| Preview Environment DNS | ⏸️ Future | MEDIUM | Plan ExternalDNS setup |
| Database Isolation | 🔄 Active | HIGH | Azure Functions webhook automation |
| E2E Testing | ⏸️ Future | HIGH | Playwright setup |
| OpenAPI Docs | ⏸️ Future | LOW | GitHub Pages automation |
| GitOps Repository | ⏸️ Future | LOW | Separate config repo |
| CI/CD Trigger Optimization | ✅ Done | LOW | **COMPLETED** |
| Namespace Creation Efficiency | ✅ Done | LOW | **COMPLETED** |
| Dependabot Setup | ⏸️ Future | MEDIUM | Configure .github/dependabot.yml |
| CodeQL Security Scanning | ⏸️ Future | MEDIUM | Add .github/workflows/codeql.yml |
| Branch Protection Rules | ⏸️ Future | HIGH | Enforce CI+CodeQL for merge |

## Active Tasks

### Critical
- [ ] **Fix PostgreSQL Backup CronJob - Complete Rebuild**
  - **Why**: Current Azure Workload Identity setup is broken; backup functionality not working
  - **Scope**: Clean slate approach following documented infrastructure design
  - **Details**: See dedicated section below for step-by-step plan

### Critical
- [ ] Review deployment pipelines with Copilot for optimization and best practices
  - **Why**: Recent health check fixes need validation; ensure robust CI/CD patterns
  - **Scope**: Production, feature branch, and cleanup workflows

### Immediate
- [x] ~~Refactor workflows to use repository variables~~
  - **Why**: Remove hardcoded values, improve maintainability
- [ ] Implement Azure Functions webhook for database automation (Phase 1)
  - **Why**: Immediate database isolation without complex infrastructure
  - **Scope**: Branch create/delete webhooks → Azure Functions → Database provisioning
  - **Details**: See [Issue #18](https://github.com/rjpalt/KubernetesMOOC/issues/18) for Python implementation
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
- [ ] Database isolation per feature branch - Phase 2: Full infrastructure (see [Issue #17](https://github.com/rjpalt/KubernetesMOOC/issues/17))
  - **Why**: Complete preview environment setup after Phase 1 webhook automation
  - **Details**: ALB/Gateway, DNS, cert-manager integration
- [ ] Add Playwright E2E tests targeting live environments
  - **Why**: Validate complete workflows before production
- [ ] Set up GitOps with separate config repository
  - **Why**: Track actual deployed state, enable proper rollbacks

## PostgreSQL Backup CronJob - Rebuild Plan

### Current State Analysis
**Problems:**
- Service account in wrong namespace (`project` vs `default`)
- Service account name mismatch (`postgres-backup-prod-service-account` vs `backup-serviceaccount`)
- Azure Workload Identity environment variables not being injected
- Backup uploads failing due to authentication issues

**What Works:**
- PostgreSQL database connectivity ✅
- CronJob scheduling ✅
- Local backup creation ✅
- Script logic and error handling ✅

### Step 1: Clean Up Current Implementation
- [ ] Remove current broken service account
  ```bash
  kubectl delete serviceaccount postgres-backup-prod-service-account -n project
  ```
- [ ] Remove backup-service-account.yaml from manifests
- [ ] Update kustomization.yaml to remove backup-service-account.yaml
- [ ] Revert pg_cronjob.yaml to not use any service account (use default)

### Step 2: Follow Documented Infrastructure Design
Based on `.project/context.yaml`, the production backup should use:
- **Namespace**: `default` (not `project`)
- **Service Account**: `backup-serviceaccount`
- **Managed Identity**: `backup-production-identity` (50f96678-064c-463a-a3e3-2297a3b557f1)
- **Storage Container**: `database-backups`
- **Federated Credential**: Already configured for `system:serviceaccount:default:backup-serviceaccount`

### Step 3: Create Proper Service Account
- [ ] Create new service account in `default` namespace:
  ```yaml
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: backup-serviceaccount
    namespace: default
    annotations:
      azure.workload.identity/client-id: "50f96678-064c-463a-a3e3-2297a3b557f1"
    labels:
      azure.workload.identity/use: "true"
  ```

### Step 4: Update CronJob Configuration
- [ ] Move pg_cronjob to `default` namespace
- [ ] Update serviceAccountName to `backup-serviceaccount`
- [ ] Verify environment variables match storage account configuration
- [ ] Keep enhanced logging (LOG_LEVEL: DEBUG) for verification

### Step 5: Test and Validate
- [ ] Deploy updated manifests
- [ ] Verify Azure Workload Identity environment variables are injected
- [ ] Test backup creation and Azure upload
- [ ] Verify backups appear in `kubemoocbackups/database-backups` container
- [ ] Reduce logging to INFO once working

### Step 6: Consider Future Improvements
- [ ] Document why backup runs in `default` vs `project` namespace
- [ ] Consider moving to `project` namespace if workload identity can be reconfigured
- [ ] Add backup retention policy
- [ ] Add monitoring/alerting for backup failures
- [ ] **Reduce sensitive logging in backup script for production**
  - **Why**: Current debug logging exposes Client ID, Tenant ID, and token content (security risk)
  - **Action**: Mask sensitive values, remove token content logging, add PRODUCTION_MODE flag
  - **Priority**: After authentication is confirmed working
- [ ] **Document Azure Workload Identity federated token usage in Azure-memos.md**
  - **Why**: Need reference for manually using az CLI inside AKS containers with federated tokens
  - **Content**: How to authenticate with `az login --federated-token` using environment variables
  - **Reference**: Current backup script implementation as working example

### Key Insights
- The infrastructure was designed with specific naming patterns
- Azure federated credentials are already configured correctly
- The issue is namespace/service account name mismatch, not Azure configuration
- Following the documented design should resolve authentication issues

### Workflow Optimizations
- [x] ~~Optimize CI/CD trigger paths for smarter rebuilds~~
  - **Current**: ~~Triggers on any `course_project/**` change (docs, manifests, etc.)~~
  - **Goal**: ~~Only trigger on source code changes (src/, Dockerfile, pyproject.toml)~~
  - **Why**: ~~Avoid unnecessary rebuilds/deployments for documentation changes~~
  - **Status**: **COMPLETED** - CI now only triggers on meaningful code changes
- [x] ~~Improve namespace creation efficiency in feature deployments~~
  - **Current**: ~~Always attempts `kubectl create namespace || true`~~
  - **Goal**: ~~Check if namespace exists first, then create only if needed~~
  - **Why**: ~~Cleaner logs, faster deployment, better error handling~~
  - **Status**: **COMPLETED** - Deployment now checks namespace existence before creation

### Security & Quality Automation
- [ ] Set up Dependabot for automated dependency updates
  - **Goal**: Monitor Python dependencies in pyproject.toml files for security vulnerabilities
  - **Config**: `.github/dependabot.yml` with schedule and PR grouping
  - **Why**: Proactive security patching, reduced maintenance overhead
- [ ] Configure CodeQL security scanning
  - **Goal**: Automated static analysis for Python code security issues
  - **Config**: `.github/workflows/codeql.yml` triggered on push/PR
  - **Why**: Early detection of security vulnerabilities in source code
- [ ] Enforce CI and security checks as PR merge requirements
  - **Goal**: Require CI pipeline + CodeQL to pass before merge to main
  - **Config**: Branch protection rules in GitHub repository settings
  - **Why**: Prevent broken or insecure code from reaching production

### Platform Features (Future)
- [ ] Document overlay maintenance requirement (README + Azure memos)
- [ ] Consider External Secrets Operator (ESO) with Azure Key Vault; optionally HashiCorp Vault for dynamic secrets
- [ ] Decide preview env trigger: PR-opened (recommended for cost) vs. branch-created; implement chosen workflow
- [ ] Prep platform installs (cluster-wide): ExternalDNS (Azure DNS) and cert-manager (Let's Encrypt), scoped to preview domain
- [ ] Per-feature hostnames with ExternalDNS + cert-manager (Preview Environments)
  - **Why**: Avoid path-prefix crowding and rewrite complexity in Gateway API
  - **Goal**: feature-<branch>.preview.example.com URLs with automatic TLS
- [ ] OpenAPI documentation automation with GitHub Pages
- [ ] GitOps repository implementation for better state tracking
- [ ] Playwright E2E testing with feature branch environments
