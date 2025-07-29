# TODO: Priority Tasks for Tomorrow's Assessment

## ⚡ CRITICAL: GitHub Actions & Kubernetes Validation (Next Session Start)

### 🔥 IMMEDIATE NEXT SESSION TASKS
When resuming work, complete these tasks in order:

#### 1. GitHub Actions CI/CD Pipeline Fixes
- [ ] **Fix remaining GitHub Actions test issues** - Currently failing on database service configuration
  - Issue: PostgreSQL service added but tests may still have connection issues
  - Check: Environment variables alignment between workflow and Settings class
  - Verify: Service health checks are working properly
- [ ] **Test GitHub Actions workflow thoroughly** - Ensure all test stages pass (unit, integration, coverage)
- [ ] **Validate CI environment vs local environment** - Confirm test behavior is consistent

#### 2. Kubernetes Manifests Review & Validation
- [ ] **Review ALL Kubernetes manifests with fresh perspective**
  - Focus on lessons learned from recent endpoint and selector failures
  - Double-check: Service selectors match Deployment labels exactly
  - Verify: All port configurations are consistent across manifests
  - Confirm: Resource requests/limits are appropriate
- [ ] **Apply manifests to test cluster** - Validate they work without errors
- [ ] **Test service discovery and connectivity** - Ensure pods can communicate properly

#### 3. Strategic Documentation Review
- [ ] **Re-read Testing Plan thoughtfully** (`course_project/todo-backend/tests/TESTING_PLAN.md`)
  - Understand: What test scenarios are covered vs missing
  - Identify: Any gaps that could cause production issues
  - Plan: Additional test implementations if needed
- [ ] **Re-read GitHub Actions workflow with thought** (`.github/workflows/test.yml`)
  - Understand: Each step and why it's there
  - Verify: Workflow matches current project architecture
  - Optimize: Any inefficiencies or redundancies

#### 4. Comprehensive System Testing
- [ ] **Test complete local development setup**
  - Verify: docker-compose.yaml works end-to-end
  - Test: All services communicate properly
  - Confirm: Database connections and data persistence
- [ ] **Test Kubernetes deployment end-to-end**
  - Deploy: All manifests to test cluster
  - Verify: All pods are running and healthy
  - Test: Frontend can communicate with backend
  - Test: Backend can communicate with database
- [ ] **Run quality checks and fix any issues**
  - Execute: `./quality.sh` and fix any remaining linting issues
  - Review: Test coverage reports for gaps
  - Validate: All tests pass consistently

#### 5. Pre-Commit Validation Checklist
- [ ] **All GitHub Actions tests passing** ✅
- [ ] **All Kubernetes manifests deploy successfully** ✅
- [ ] **Local development environment fully functional** ✅
- [ ] **Code quality checks all green** ✅
- [ ] **Documentation updated and accurate** ✅

### 🎯 Success Criteria
Ready to commit when:
1. GitHub Actions pipeline is 100% green
2. Kubernetes manifests deploy without errors
3. All services communicate properly in K8s
4. Local development setup is fully functional
5. Code quality standards are met

---

# TODO: OpenAPI Documentation Automation

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

## Goal
Set up Azure Key Vault for secure secrets management when deploying microservices to AKS, replacing current local/SOPS approach with production-ready Azure-native solution.

## Key Concepts to Learn & Implement
- [ ] Azure Key Vault creation and configuration
- [ ] Workload Identity for pod-to-Azure authentication
- [ ] CSI Secrets Store Driver for mounting secrets in Kubernetes
- [ ] SecretProviderClass resource definition
- [ ] Database connection string management

## Current Status
- Services running locally with k3d/Docker
- Need to determine full specifications for AKS deployment
- Planning phase - not ready for implementation yet
- Target secrets: database passwords and connection strings

## Implementation Prerequisites
- [ ] Finalize AKS cluster requirements
- [ ] Determine database service specifications (Azure SQL, PostgreSQL, etc.)
- [ ] Design secret structure and naming conventions
- [ ] Plan Workload Identity setup approach

**Next Steps**: Complete local development, then tackle Azure resource setup and integration concepts.