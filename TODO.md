# TODO: SOPS Implementation for Secret Encryption

## Goal
Encrypt Kubernetes secret files with SOPS to safely commit them to version control while maintaining security.

## Implementation Steps

### Phase 1: Install and Setup SOPS
- [ ] Install SOPS: `brew install sops` (macOS)
- [ ] Install age for encryption: `brew install age`
- [ ] Generate age key pair: `age-keygen -o ~/.config/sops/age/keys.txt`
- [ ] Note the public key from the output for .sops.yaml configuration

### Phase 2: Configure SOPS for Repository
- [ ] Create `.sops.yaml` in repository root with encryption rules:
  ```yaml
  creation_rules:
    - path_regex: .*-secret\.yaml$
      age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Your public key
  ```
- [ ] Test configuration with a sample secret file

### Phase 3: Encrypt Existing Secrets
- [ ] Backup current secret files (they're gitignored, so copy them somewhere safe)
- [ ] Encrypt each secret file in place:
  ```bash
  sops -e -i ping-pong/manifests/ping-pong/postgres-secret.yaml
  sops -e -i ping-pong/manifests/ping-pong/ping-pong-secret.yaml
  ```
- [ ] Verify encrypted files look correct (should show encrypted data)

### Phase 4: Update Gitignore and Workflow
- [ ] Remove secret file patterns from .gitignore:
  ```diff
  - # Ignore all Kubernetes secret YAML files (before SOPS encryption)
  - **/manifests/**/*-secret.yaml
  - **/*-secret.yaml
  ```
- [ ] Commit encrypted secret files to version control
- [ ] Update deployment workflow to use SOPS decryption:
  ```bash
  sops -d manifests/ping-pong/postgres-secret.yaml | kubectl apply -f -
  ```

### Phase 5: Team Collaboration Setup
- [ ] Share age private key securely with team members (outside of git)
- [ ] Document how team members should set up their local SOPS configuration
- [ ] Test that other team members can decrypt and apply secrets

### Phase 6: CI/CD Integration (Future)
- [ ] Store age private key in GitHub Secrets (when needed)
- [ ] Update GitHub Actions workflows to use SOPS for secret decryption
- [ ] Test automated deployments with encrypted secrets

## Key Commands Reference
```bash
# Encrypt a file in place
sops -e -i your-secret.yaml

# Decrypt and view (without modifying file)
sops -d your-secret.yaml

# Decrypt and apply to Kubernetes
sops -d your-secret.yaml | kubectl apply -f -

# Edit encrypted file (decrypts, opens editor, re-encrypts on save)
sops your-secret.yaml
```

## Security Notes
- Never commit the age private key to version control
- Store private key securely (password manager, encrypted backup)
- Rotate keys periodically in production environments
- Consider using cloud KMS (AWS KMS, Azure Key Vault) for production

**Next Steps**: Start with Phase 1 - install SOPS and age, then generate your key pair.

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

---

# TODO: Exercise 2.5 - ConfigMap Environment Variable Integration

## Current Status
- ConfigMap created with `information.txt` file mount ✅
- File-based ConfigMap working correctly ✅
- Need to migrate `LOG_APP_MESSAGE` environment variable to ConfigMap

## Next Steps
- [ ] Remove `LOG_APP_MESSAGE` from log-output-deployment.yaml env section
- [ ] Add ConfigMap reference using `envFrom` or `env.valueFrom.configMapKeyRef`
- [ ] Test that application reads message from ConfigMap instead of hardcoded env var
- [ ] Verify deployment works and submit exercise