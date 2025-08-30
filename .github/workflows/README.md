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
        E[PR to main] --> F(ci.yml<br>Tests & Builds Images);
        F -- On Success --> G(deploy-feature-branches.yml<br>Deploys to Feature Env);
        G -- On Success --> H(e2e-tests.yml<br>Runs E2E Tests);
    end

    subgraph "Production Deployment"
        I[Merge to main] --> J(ci-production.yml<br>Tests & Builds Prod Images);
        J -- On Success --> K(deploy-production.yml<br>Deploys to Production);
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
- **Purpose**: Acts as the primary Continuous Integration pipeline for pull requests. It validates code quality, runs tests, and builds container images for feature branches.
- **Trigger**: Runs on every push to a pull request targeting the `main` branch.
- **Process**:
    1. Runs code quality checks (linting, formatting).
    2. Executes backend and frontend unit and integration tests.
    3. Builds Docker images for the backend, frontend, and cron services.
    4. Tags the images with `{branch-name}-{commit-sha}`.
    5. Pushes the tagged images to Azure Container Registry (ACR).
- **Dependencies**: Triggers `deploy-feature-branches.yml` on successful completion.

#### 4. `deploy-feature-branches.yml`
- **Purpose**: Deploys the application to a dedicated, isolated Kubernetes environment for a feature branch.
- **Trigger**: Runs after `ci.yml` completes successfully for a non-`main` branch.
- **Process**:
    1. Uses the images built by `ci.yml`.
    2. Deploys the application to the pre-provisioned namespace for that branch.
    3. Posts a comment on the corresponding Pull Request with the URL and access details for the feature environment.
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
- **Purpose**: A dedicated CI pipeline that builds and pushes production-ready images.
- **Trigger**: Runs only on pushes to the `main` branch (i.e., after a PR is merged).
- **Process**:
    1. Runs the full suite of tests again to ensure integrity on `main`.
    2. Builds production-ready Docker images.
    3. Tags the images with `main-{commit-sha}`.
    4. Pushes the images to ACR.
- **Dependencies**: Triggers `deploy-production.yml` on successful completion.

#### 7. `deploy-production.yml`
- **Purpose**: Deploys the application to the production Kubernetes environment.
- **Trigger**: Runs after `ci-production.yml` completes successfully.
- **Process**:
    1. Verifies that the images tagged `main-{commit-sha}` exist in ACR.
    2. Applies the Kubernetes manifests to the production namespace, updating the running application to the new version.
    3. Performs health checks to ensure the deployment was successful.
- **Dependencies**: `ci-production.yml`.

### Documentation

#### 8. `deploy-docs.yaml`
- **Purpose**: Automatically builds and deploys the project documentation.
- **Trigger**: Runs on pushes to the `main` branch that include changes in the `docs/` directory.
- **Process**:
    1. Builds the documentation site.
    2. Deploys the static site to its hosting environment.
- **Depends On**: Push to `main` with `docs/` changes.
