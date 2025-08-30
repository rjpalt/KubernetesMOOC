# TODO - Project Tasks

## Current Sprint: Resource Management & Scaling (Exercises 3.11 & 3.12)

### Phase 0: Prerequisite Knowledge (You)
- [x] **Action:** Read the course section on scaling and watch the video. This will provide the necessary background for the next steps.

### Phase 1: Resource Governance (Exercise 3.11)
- [x] **Goal:** Establish resource limits and namespace quotas.
- [x] **Actions:**
    - [x] Define CPU/memory requests and limits for all project deployments.
    - [x] Implement ResourceQuota objects for production and feature namespaces.

### Phase 1.5: Debugging Feature Deployments
- [ ] **Goal:** Diagnose why `ResourceQuotas` were not enforced in feature branch deployments.
- [ ] **Actions:**
    - [ ] Investigate the deployment function's handling of kustomize overlays.
    - [ ] Verify that `resourcequota.yaml` is correctly included in the kustomize build.
    - [ ] Confirm the deployment function has sufficient permissions to apply `ResourceQuotas`.

### Phase 2: Monitoring & Autoscaling (Exercise 3.12)
- [ ] **Goal:** Enable monitoring and configure automatic scaling.
- [ ] **Actions:**
    - [ ] Enable Azure Monitor for containers on the AKS cluster.
    - [ ] Validate the logging pipeline by confirming logs are visible in Azure.
    - [ ] Implement the Horizontal Pod Autoscaler (HPA) for the backend and frontend.
    - [ ] Verify the Cluster Autoscaler is enabled for the AKS node pool.

### Phase 3: Validation & Learning
- [ ] **Goal:** See the system work.
- [ ] **Action:** Perform a simple load simulation to trigger and observe both pod and node scaling.

## Next Up
- [ ] **Review CI/CD Pipeline:** Audit the `main` branch's deployment workflow for optimizations and best practices.

## Future Enhancements
- [ ] **Security Hardening:**
    - [ ] Configure Dependabot for automated dependency updates.
    - [ ] Configure CodeQL for static analysis security scanning.
    - [ ] Enforce branch protection rules on `main`.
- [ ] **GitOps:** Implement a GitOps workflow using a separate configuration repository for tracking deployed state.
- [ ] **Advanced Preview Environments:** Replace `nip.io` with a proper DNS and certificate solution (ExternalDNS, cert-manager).
- [ ] **Documentation:** Automate OpenAPI documentation publishing.

## Recently Completed
- [x] **E2E Testing Foundation:** Implemented a comprehensive Playwright E2E test suite with support for local (Docker Compose) and remote (Kubernetes) execution environments.
- [x] **E2E Testing CI Integration:** Automated the execution of the Playwright E2E suite in a GitHub Actions workflow that runs after feature branch deployments, providing direct feedback on pull requests.
