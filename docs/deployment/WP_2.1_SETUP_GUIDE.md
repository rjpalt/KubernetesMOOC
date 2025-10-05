# Work Package 2.1 Setup Guide
## Automated Staging Deployment - Manual Configuration Steps

This guide covers the manual configuration steps required to complete WP 2.1: Automated Staging Deployment.

## Overview

The automated staging deployment workflow has been implemented and consists of:
- GitHub Actions workflow: `.github/workflows/deploy-staging.yml`
- ArgoCD Application manifest: `cluster-manifests/staging-app.yaml`
- Updated workflow documentation in `.github/workflows/README.md`

The following manual steps are required to activate the staging deployment pipeline.

---

## Step 1: Configure GitHub Environment

### Create Staging Environment

1. Navigate to your GitHub repository
2. Go to **Settings** → **Environments**
3. Click **New environment**
4. Name: `staging`
5. Click **Configure environment**

### Configure Environment Protection Rules

**Branch Protection:**
1. Under **Deployment branches**, select **Selected branches**
2. Add branch pattern: `main`
3. This ensures only merges to main can deploy to staging

**Optional: Approval Gates**
- For now, leave approval gates disabled (automated deployment)
- Can be enabled later when mature deployment process is established

### Configure Environment Secrets

Add the following secrets to the `staging` environment:

**Note:** These secrets may already exist at the repository level. Environment-specific secrets override repository secrets.

Currently, no staging-specific secrets are required as the workflow inherits from repository-level secrets:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `ACR_LOGIN_SERVER` (from variables)
- `AKS_CLUSTER_NAME` (from variables)
- `AKS_RESOURCE_GROUP` (from variables)

**Future Enhancement:** If staging needs different credentials (e.g., separate Azure identity), add them as environment-specific secrets.

---

## Step 2: Deploy ArgoCD Staging Application

### Prerequisites
- AKS cluster access configured (`kubectl` connected)
- ArgoCD installed and accessible in the cluster
- Staging namespace manifests committed to Git (from WP 2.0)

### Deploy Staging Application

```bash
# Ensure you're connected to the correct AKS cluster
kubectl config current-context

# Deploy the ArgoCD staging application
kubectl apply -f cluster-manifests/staging-app.yaml

# Verify the application was created
kubectl get application staging-app -n argocd

# Check application status
kubectl describe application staging-app -n argocd
```

### Verify ArgoCD Configuration

1. Access ArgoCD UI:
   ```bash
   # Get ArgoCD URL (if using LoadBalancer)
   kubectl get svc argocd-server -n argocd
   ```

2. Login to ArgoCD UI

3. Find the `staging-app` application

4. Verify configuration:
   - **Source Repository**: `https://github.com/rjpalt/KubernetesMOOC.git`
   - **Target Revision**: `main`
   - **Path**: `course_project/manifests/overlays/staging`
   - **Destination Namespace**: `staging`
   - **Sync Policy**: Automated (prune, self-heal enabled)

### Initial Sync

The first sync should happen automatically. If not:

```bash
# Manually trigger sync (optional)
argocd app sync staging-app

# Or via kubectl
kubectl patch application staging-app -n argocd \
  --type merge \
  -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{"revision":"main"}}}'
```

---

## Step 3: Validate Staging Deployment

### Verify Namespace and Resources

```bash
# Check staging namespace exists
kubectl get namespace staging

# Verify namespace has required labels
kubectl get namespace staging -o yaml | grep -A 5 labels

# Expected labels:
# - dev-gateway-access: allowed  (for AGC gateway)
# - app.kubernetes.io/name: staging
# - environment: staging

# Check all staging resources
kubectl get all -n staging

# Expected resources:
# - deployments: todo-app-be, todo-app-fe, broadcaster, nats
# - services: todo-app-be-svc, todo-app-fe-svc, nats, nats-headless
# - pods: Running pods for all deployments
# - cronjob: todo-cron (if applicable)
```

### Verify HTTPRoute Configuration

```bash
# Check HTTPRoute in staging namespace
kubectl get httproute -n staging

# Verify route configuration
kubectl describe httproute todo-app -n staging

# Expected configuration:
# - Parent Gateway: agc-feature-gateway (agc-shared namespace)
# - Hostnames: staging.23.98.101.23.nip.io
# - Backend refs: todo-app-be-svc, todo-app-fe-svc
```

### Test Staging Application

```bash
# Test staging URL
curl -I http://staging.23.98.101.23.nip.io

# Expected: HTTP 200 OK

# Test backend health endpoint
curl http://staging.23.98.101.23.nip.io/be-health

# Expected: JSON health status with todo count

# Test frontend
curl http://staging.23.98.101.23.nip.io/

# Expected: HTML response (todo application)
```

---

## Step 4: Trigger Test Deployment

### Automated Trigger (Recommended)

The staging deployment will trigger automatically on the next merge to `main`:

1. Create a test PR with a small change
2. Wait for CI to pass
3. Merge PR to `main`
4. Monitor workflows:
   - `ci-production.yml` runs first
   - `deploy-staging.yml` triggers after CI success
   - `deploy-production.yml` also triggers (parallel)

### Manual Trigger (Testing)

For immediate testing without merging:

1. Go to GitHub Actions tab
2. Select **Staging Deployment** workflow
3. Click **Run workflow**
4. Select branch: `main`
5. Click **Run workflow**

**Note:** Manual triggers are useful for testing but won't have image tag updates from CI.

---

## Step 5: Monitor Deployment

### GitHub Actions Monitoring

1. Go to **Actions** tab in GitHub
2. Find the **Staging Deployment** workflow run
3. Monitor execution steps:
   - Image validation
   - Kustomization update
   - Git commit
   - Deployment validation
   - Artifact generation

### ArgoCD Monitoring

1. Access ArgoCD UI
2. Select `staging-app`
3. Monitor sync status:
   - **Sync Status**: Should show "Synced"
   - **Health Status**: Should show "Healthy"
   - **Last Sync**: Recent timestamp after workflow completes

### Kubernetes Monitoring

```bash
# Watch staging pods
kubectl get pods -n staging -w

# Check deployment rollout status
kubectl rollout status deployment/todo-app-be -n staging
kubectl rollout status deployment/todo-app-fe -n staging
kubectl rollout status deployment/broadcaster -n staging

# Check recent events
kubectl get events -n staging --sort-by='.lastTimestamp'
```

---

## Step 6: Verify Artifact Generation

### Staging URL Artifact

The workflow generates a `staging-deployment-url` artifact for test integration (WP 2.2):

1. Go to completed workflow run in GitHub Actions
2. Scroll to **Artifacts** section
3. Verify `staging-deployment-url` artifact exists
4. Download and verify contents:
   ```
   http://staging.23.98.101.23.nip.io
   ```

This artifact will be consumed by the test suite workflow in WP 2.2.

---

## Troubleshooting

### Workflow Not Triggering

**Problem:** Staging deployment doesn't trigger after merge to main

**Solutions:**
1. Verify GitHub Environment `staging` exists
2. Check `ci-production.yml` completed successfully
3. Verify workflow file is committed to `main` branch
4. Check workflow logs for errors

### ArgoCD Not Syncing

**Problem:** ArgoCD doesn't sync staging changes

**Solutions:**
```bash
# Check application status
kubectl get application staging-app -n argocd -o yaml

# Look for sync errors
kubectl describe application staging-app -n argocd

# Manually trigger sync
argocd app sync staging-app --force

# Check ArgoCD logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

### Staging Application Not Accessible

**Problem:** Cannot access staging URL

**Solutions:**
1. Verify namespace has `dev-gateway-access=allowed` label
2. Check HTTPRoute exists and is configured correctly:
   ```bash
   kubectl get httproute -n staging
   kubectl describe httproute todo-app -n staging
   ```
3. Verify gateway exists:
   ```bash
   kubectl get gateway agc-feature-gateway -n agc-shared
   ```
4. Check pod status:
   ```bash
   kubectl get pods -n staging
   kubectl logs <pod-name> -n staging
   ```

### Image Not Found

**Problem:** Workflow fails with "image not found" error

**Solutions:**
1. Verify `ci-production.yml` completed successfully before staging deployment
2. Check ACR for images:
   ```bash
   az acr repository show-tags --name kubemooc --repository todo-app-be
   ```
3. Verify image tag format: `main-{commit-sha}`

---

## Success Criteria Checklist

Use this checklist to verify WP 2.1 is fully operational:

- [ ] GitHub `staging` environment created with protection rules
- [ ] Environment restricted to `main` branch deployments
- [ ] ArgoCD `staging-app` application deployed to cluster
- [ ] ArgoCD application shows "Synced" and "Healthy" status
- [ ] Staging namespace exists with `dev-gateway-access=allowed` label
- [ ] All staging pods are running and healthy
- [ ] HTTPRoute configured for `staging.23.98.101.23.nip.io`
- [ ] Staging application accessible via browser
- [ ] Backend health endpoint responding
- [ ] Workflow triggers automatically on merge to main
- [ ] Staging deployment completes successfully
- [ ] Staging URL artifact generated for test integration
- [ ] Production and staging deploy in parallel from same images

---

## Next Steps

Once WP 2.1 is validated:

1. **WP 2.2**: Integrate L2/L3 test suite with staging deployment
2. **Epic 3**: Implement production promotion workflow based on staging validation
3. **Monitoring**: Set up staging-specific monitoring and alerting

---

## Reference

- **Workflow File**: `.github/workflows/deploy-staging.yml`
- **ArgoCD Application**: `cluster-manifests/staging-app.yaml`
- **Staging Overlay**: `course_project/manifests/overlays/staging/`
- **Staging URL**: http://staging.23.98.101.23.nip.io
- **Gateway**: `agc-feature-gateway` (namespace: `agc-shared`)
- **Database**: `kubemooc-postgres-feature` (Azure DBaaS)
