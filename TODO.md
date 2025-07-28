# TODO: Priority Tasks for Tomorrow's Assessment

## ⚡ IMMEDIATE PRIORITIES (Next Session)

### Project Validation & Kubernetes Deployment
Based on today's async PostgreSQL integration and testing foundation work, tomorrow's focus is on comprehensive project validation and Kubernetes deployment readiness.

#### 1. Foundation Verification
- [x] **Verify all project tests work** - Confirm 39/39 tests still passing after any changes
- [x] **Test GitHub Actions CI pipeline** - Ensure automated testing works in CI environment
- [x] **Review Docker implementations** - Go through Dockerfiles and docker-compose configurations

#### 2. Local Development Setup
- [ ] **Validate local database setup** - Confirm PostgreSQL containers work properly ✅ CONFIRMED: Database containers working
- [ ] **Test local project execution** - Ensure todo-app + todo-backend + database integration works ⚠️ PORT MISMATCH: Backend runs on 8000, docker-compose expects 8001
- [ ] **Build complete docker-compose.yaml** - Create unified docker-compose for all services (missing PostgreSQL database service)
- [ ] **Update quality.sh script** - Ensure code quality checks work with current project structure
- [ ] **Update GitHub Actions workflow** - Reflect current testing pipeline and project structure
- [ ] **Verify act commands** - Ensure local GitHub Actions testing works properly
- [ ] **Fix port configuration** - Backend currently runs on port 8000, but docker-compose.yaml configures port 8001

#### 3. Kubernetes Migration Planning
- [ ] **Design database Kubernetes manifests** - Create deployment specs for PostgreSQL in K8s
- [ ] **Update existing Kubernetes manifests** - Reflect current async database architecture
- [ ] **Remove redundant persistent volumes** - Clean up manifests made obsolete by database service
- [ ] **Implement SOPS encrypted secrets** - Create proper Secret files for database credentials
- [ ] **Validate Kubernetes deployment** - Test complete K8s deployment works end-to-end

### Current Project State (After Today's Work)
✅ **Completed**: 
- Async PostgreSQL integration (todo-backend)
- Container-based testing (39/39 tests passing)
- Test isolation with dependency injection
- Production-ready CI/CD pipeline
- Comprehensive testing documentation

✅ **Backend Testing Results**:
- Health endpoint: Working (/be-health returns service status + todo count)
- GET /todos: Working (retrieves all todos from PostgreSQL)
- POST /todos: Working (creates new todos in database)
- GET /todos/{id}: Working (retrieves specific todo by ID)
- Database integration: Fully functional with async operations

⚠️ **Known Issues**:
- Port mismatch: Backend runs on 8000, docker-compose expects 8001

📋 **Test Coverage Improvements Needed**:
- 🔴 **High Priority**: SQL injection prevention, database downtime handling, load/concurrency testing
- 🟡 **Medium Priority**: Container resource limits, input sanitization, graceful shutdown testing
- See `course_project/todo-backend/tests/TEST_PLAN.md` for detailed risk assessment and implementation examples

🎯 **Ready For**: Kubernetes deployment with proper database architecture

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