# GitHub Actions Workflows

This document provides an overview of the GitHub Actions workflows used in this project, explaining their purpose, triggers, and how they connect to form a complete CI/CD and feature environment lifecycle.

## Workflow Diagram

The following Mermaid diagram illustrates the dependency chain between the different workflows:

```mermaid
graph TD
    subgraph "Branch Lifecycle"
        A[Branch Creation<br>(ex-*, feature-*)] --> B(create-k8s-env-on-branch.yml<br>Provisions DB & Namespace);
        C[Branch Deletion<br>(ex-*, feature-*)] --> D(deprovision-feature-environment.yml<br>Cleans up DB & Namespace);
    end

    subgraph "Pull Request & Feature Deployment"
        E[PR to main] --> F(ci.yml<br>Parallel Testing & Push);
        F -- Tests Pass --> F1[Push Backend];
        F -- Tests Pass --> F2[Push Frontend];
        F -- Tests Pass --> F3[Push Cron];
        F -- Tests Pass --> F4[Push Broadcaster];
        F1 & F2 & F3 & F4 --> F5[Build Summary];
        F5 -- On Success --> G(deploy-feature-branches.yml<br>Deploys to Feature Env);
        G -- On Success --> H(e2e-tests.yml<br>Runs E2E Tests);
    end

    subgraph "Production Deployment"
        I[Merge to main] --> J(ci-production.yml<br>Parallel Testing & Push);
        J -- Tests Pass --> J1[Push Backend];
        J -- Tests Pass --> J2[Push Frontend];
        J -- Tests Pass --> J3[Push Cron];
        J -- Tests Pass --> J4[Push Broadcaster];
        J1 & J2 & J3 & J4 --> J5[Build Summary];
        J5 -- On Success --> K(deploy-production.yml<br>Deploys to Production);
    end

    subgraph "Documentation"
        L[Push to main<br>(docs/ folder)] --> M(deploy-docs.yaml<br>Deploys Docs);
    end

    style A fill:#c9ffc9,stroke:#333,stroke-width:2px
    style C fill:#ffc9c9,stroke:#333,stroke-width:2px
    style E fill:#d1e7ff,stroke:#333,stroke-width:2px
    style I fill:#d1e7ff,stroke:#333,stroke-width:2px
    style L fill:#fff2cc,stroke:#333,stroke-width:2px
```

## CI/CD Architecture Overview

### Parallel Execution Model

Both `ci.yml` and `ci-production.yml` have been optimized to use a parallel execution architecture that significantly improves performance while maintaining safety:

#### Job Execution Flow
```
Code Quality (Matrix: backend, frontend, broadcaster)
    ↓
Test Execution (Optimized Dependencies)
├── Backend Tests (after code quality)
├── Frontend Tests (after backend - contract dependency)
└── Broadcaster Tests (after code quality)
    ↓
Service Integration Tests (builds & caches images)
    ↓
Parallel Image Push (4 simultaneous jobs)
├── Push Backend (cache hit ~30s)
├── Push Frontend (cache hit ~30s)  
├── Push Cron (optimized rebuild)
└── Push Broadcaster (optimized rebuild)
    ↓
Build Summary (comprehensive status)
```

#### Performance Improvements
- **40-60% faster pipeline execution** through parallel push operations
- **Near-instantaneous pushes** for backend/frontend via GitHub Actions cache hits
- **Optimized resource utilization** with concurrent job execution
- **Enhanced developer experience** through faster feedback cycles

#### Cache Strategy
- **GitHub Actions Cache**: `type=gha` with `mode=max` for optimal layer reuse
- **Cross-job sharing**: Integration tests build and cache images for push jobs
- **Intelligent reuse**: Backend/frontend get cache hits, cron/broadcaster get fast rebuilds

## Workflow Descriptions

### Environment Provisioning

#### 1. `create-k8s-env-on-branch.yml`
- **Purpose**: Automatically provisions the necessary backend infrastructure (PostgreSQL database and Kubernetes namespace) for a new feature branch.
- **Trigger**: Runs when a new branch is created with a name starting with `ex-` or `feature-`.
- **Process**:
    1. A developer creates a new branch (e.g., `feature-new-login`).
    2. The workflow triggers and calls an Azure Function.
    3. The Azure Function creates a dedicated, isolated database and a Kubernetes namespace for the branch.
- **Depends On**: Branch creation event.

#### 2. `deprovision-feature-environment.yml`
- **Purpose**: Automatically deprovisions and cleans up all resources associated with a feature branch.
- **Trigger**: Runs when a branch starting with `ex-` or `feature-` is deleted.
- **Process**:
    1. A developer deletes a feature branch after merging it.
    2. The workflow triggers and calls an Azure Function.
    3. The Azure Function deletes the database and Kubernetes namespace associated with that branch, ensuring no orphaned resources are left behind.
- **Depends On**: Branch deletion event.

### CI & Feature Deployment

#### 3. `ci.yml`
- **Purpose**: Acts as the primary Continuous Integration pipeline for pull requests. It validates code quality, runs tests, and builds container images for feature branches using a parallel execution architecture.
- **Trigger**: Runs on every push to a pull request targeting the `main` branch.
- **Process**:
    1. **Code Quality** (parallel matrix): Runs code quality checks (linting, formatting) across all services simultaneously.
    2. **Unit & Integration Tests** (optimized parallel): 
       - Backend tests run after code quality passes
       - Frontend tests run after backend (contract dependency)
       - Broadcaster tests run after code quality passes (independent)
    3. **Service Integration Tests**: Builds and caches Docker images for backend and frontend using GitHub Actions cache.
    4. **Parallel Image Push**: Four independent push jobs run simultaneously:
       - `push-backend`: Pushes backend image (cache hit from integration tests)
       - `push-frontend`: Pushes frontend image (cache hit from integration tests) 
       - `push-cron`: Builds and pushes cron image (with cache optimization)
       - `push-broadcaster`: Builds and pushes broadcaster image (with cache optimization)
    5. **Build Summary**: Aggregates results and provides comprehensive pipeline status.
    6. Tags all images with `{branch-name}-{commit-sha}`.
- **Architecture Benefits**: 
    - **40-60% faster execution** through parallel push operations
    - **Near-instantaneous pushes** for backend/frontend via GitHub Actions cache hits
    - **Enhanced visibility** with per-service status reporting
    - **Improved reliability** through isolated job failures
- **Dependencies**: Triggers `deploy-feature-branches.yml` on successful completion.

#### 4. `deploy-feature-branches.yml`
- **Purpose**: Deploys the application to a dedicated, isolated Kubernetes environment for a feature branch.
- **Trigger**: Runs after `ci.yml` completes successfully for a non-`main` branch.
- **Process**:
    1. Uses the images built by `ci.yml`.
    2. Deploys the application to the pre-provisioned namespace for that branch.
    3. **NEW**: Deploys Azure monitoring configuration using `azure-feature` overlay with dynamic namespace replacement.
    4. Posts a comment on the corresponding Pull Request with the URL and access details for the feature environment.
- **Dependencies**: `ci.yml`. Triggers `e2e-tests.yml` on successful completion.

#### 5. `e2e-tests.yml`
- **Purpose**: Runs end-to-end (E2E) tests using Playwright against the live, deployed feature environment.
- **Trigger**: Runs after `deploy-feature-branches.yml` completes successfully.
- **Process**:
    1. Downloads the deployment URL from the previous workflow.
    2. Executes the Playwright test suite against the live application.
    3. Posts a comment on the PR with the test results (pass or fail).
- **Dependencies**: `deploy-feature-branches.yml`.

### Production Deployment

#### 6. `ci-production.yml`
- **Purpose**: A dedicated CI pipeline that builds and pushes production-ready images using the same optimized parallel architecture as the PR pipeline.
- **Trigger**: Runs only on pushes to the `main` branch (i.e., after a PR is merged), with manual trigger capability via `workflow_dispatch`.
- **Process**:
    1. **Code Quality** (parallel matrix): Validates code quality across all services simultaneously.
    2. **Comprehensive Testing** (optimized parallel):
       - Backend and frontend tests run with optimized dependency chain
       - Broadcaster tests run independently after code quality
    3. **Service Integration Tests**: Builds and caches production images using GitHub Actions cache.
    4. **Parallel Production Push**: Four independent push jobs execute simultaneously:
       - `push-backend`: Pushes production backend image with cache optimization
       - `push-frontend`: Pushes production frontend image with cache optimization
       - `push-cron`: Builds and pushes production cron image
       - `push-broadcaster`: Builds and pushes production broadcaster image
    5. **Build Summary**: Provides comprehensive production deployment status.
    6. Tags all images with `main-{commit-sha}`.
- **Architecture Benefits**:
    - **Consistent performance** with PR pipeline (40-60% faster execution)
    - **Production safety** through rigorous test-first approach
    - **Cache efficiency** reduces build times and registry load
    - **Manual override capability** for emergency deployments
- **Dependencies**: Triggers `deploy-production.yml` on successful completion.

#### 7. `deploy-production.yml`
- **Purpose**: Deploys the application to the production Kubernetes environment.
- **Trigger**: Runs after `ci-production.yml` completes successfully.
- **Process**:
    1. Verifies that the images tagged `main-{commit-sha}` exist in ACR.
    2. Applies the Kubernetes manifests to the production namespace, updating the running application to the new version.
    3. **NEW**: Deploys Azure monitoring configuration using `azure-production` overlay.
    4. Performs health checks to ensure the deployment was successful.
- **Dependencies**: `ci-production.yml`.

### Documentation

#### 8. `deploy-docs.yaml`
- **Purpose**: Automatically builds and deploys the project documentation.
- **Trigger**: Runs on pushes to the `main` branch that include changes in the `docs/` directory.
- **Process**:
    1. Builds the documentation site.
    2. Deploys the static site to its hosting environment.
- **Depends On**: Push to `main` with `docs/` changes.
