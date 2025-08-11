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
