# TODO: Priority Tasks for Tomorrow

## Exercise 3.4: Gateway API Route Rewriting (IMMEDIATE)
- [ ] **Build and push new images**: `./build-apps.sh v3.4`
- [ ] **Import to cluster**: `k3d image import ping-pong-app:v3.4 log-output-app:v3.4 -c <cluster-name>`
- [ ] **Update HTTPRoute manifest**: Add `filters` with `URLRewrite` + `ReplacePrefixMatch` to rewrite `/pingpong` → `/`
- [ ] **Apply changes**: `kubectl apply -f ping-pong/manifests/ping-pong/ping-pong-route.yaml`
- [ ] **Test**: External `/pingpong` should hit internal `/` (ping-pong app now responds at root path)

**Status**: App-level changes complete (moved `/pingpong` → `/`), Gateway route rewriting pending.

---

## Tomorrow's Assessment
- [ ] **Re-read GitHub Actions workflow with thought** (`.github/workflows/test.yml`)
  - Understand: Each step and why it's there
  - Verify: Workflow matches current project architecture
  - Optimize: Any inefficiencies or redundancies

---

# TODO: Container Registry Integration for Local Development

## Goal
Optimize development workflow by pushing locally-built Docker images to a container registry, then having CI/CD pull those pre-built images instead of rebuilding from scratch.

## Current Situation
- **Local Development**: Build images with `./build-images.sh v1.2.3`
- **CI/CD Pipeline**: Rebuilds the same images from source code
- **Inefficiency**: Duplicate build time and compute resources
- **Feedback Loop**: Slower CI/CD due to build overhead

## Proposed Workflow
1. **Local Build & Push**: `./build-images.sh v1.2.3 --push`
2. **CI/CD Pull**: Use pre-built images from registry
3. **Faster Testing**: Integration tests start immediately
4. **Consistency**: Test exact same artifacts used locally

## Implementation Considerations

### Registry Options
- **GitHub Container Registry (ghcr.io)**: Free, integrated with repository
- **Docker Hub**: Popular, but rate limits on free tier
- **Azure Container Registry**: If planning AKS deployment
- **Local Registry**: For air-gapped development

### Build Script Enhancements Needed
- [ ] Add `--push` flag to build-images.sh
- [ ] Add `--registry` parameter for flexibility
- [ ] Registry authentication handling
- [ ] Error handling for push failures
- [ ] Registry-specific image tagging

### CI/CD Workflow Changes
- [ ] Add step to pull pre-built images instead of building
- [ ] Handle case where registry images don't exist (fallback to build)
- [ ] Environment variable to specify image source (registry vs build)
- [ ] Image existence checking before pull attempts

### Questions to Resolve
1. **Authentication Strategy**: How to handle registry login in CI/CD?
2. **Fallback Mechanism**: What if registry images are missing/corrupted?
3. **Tag Management**: How to coordinate tags between local and CI/CD?
4. **Image Cleanup**: How to prevent registry bloat over time?
5. **Security**: Image vulnerability scanning before use?
6. **Cost**: Registry storage costs vs build compute costs?

### Development Workflow Impact
- **Positive**: Faster CI/CD feedback loops
- **Positive**: Test exact artifacts used in production
- **Consideration**: Requires registry setup and authentication
- **Consideration**: Additional complexity in build process

### Kubernetes Learning Aspects
- **Registry Integration**: How Kubernetes pulls images in production
- **Image Management**: Tagging strategies and lifecycle management
- **Security**: Image scanning and trusted registries
- **GitOps**: Artifact promotion through environments

## Implementation Priority
- **Phase 1**: Research and design decisions
- **Phase 2**: Enhance build-images.sh with push capability
- **Phase 3**: Update CI/CD workflow to pull images
- **Phase 4**: Add fallback mechanisms and error handling

**Status**: Planning phase - need to resolve authentication and workflow questions before implementation.

---
**Next Steps**: Research registry authentication options and define tag coordination strategy.

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