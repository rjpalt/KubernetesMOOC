# Documentation and Developer Experience Roadmap

Purpose: make it obvious what to run, where docs live, and how to develop/test/deploy, without moving code now.

Status: draft (tracking checklist below). Scope is docs and DX wrappers only; no file moves; keep current paths. Manifests stay as-is; GitOps later.

## Context and constraints
- GitOps planned: manifests may move to a separate repo later. For now, only index/links, no relocations.
- Keep current paths for services and scripts; avoid churn. We’ll document mappings and standard names first.
- Shared env directory is low priority; keep per-service envs for now.

## Outcomes
- Single starting point for newcomers (repo map and onboarding).
- Canonical locations for testing docs (backend already has TEST_PLAN.md; add frontend; add project-wide testing overview including E2E).
- Clear script catalog: what each script does, where it lives, and the intended standard wrapper name.
- Optional task runner wrappers to unify commands later (make or just), without removing existing scripts.

## Phased plan

Phase 1 — Documentation skeleton (no code moves)
- [x] Top-level project docs index (links, not duplication)
  - [x] docs/overview/repo-map.md (what lives where, quick links)
  - [x] docs/overview/onboarding.md (install, run dev, run tests, where manifests/docs are)
- [x] Development docs
  - [x] docs/development/local-dev.md (how to start local dev; where DB/compose lives; clarify that BE compose is the authoritative DB for dev)
  - [x] docs/development/script-catalog.md (catalog + deprecation notes)
- [x] Testing docs
  - [x] docs/testing/index.md (project-wide testing model; links to FE and BE plans; E2E place-holder)
  - [x] course_project/todo-app/TEST_PLAN.md (frontend, mirroring backend structure)
  - [x] course_project/TESTING_OVERVIEW.md (project-level strategy + E2E positioning)
- [x] Platform docs
  - [x] docs/platform/manifests-index.md (where manifests are, their scope, GitOps note; no apply commands)
  - [ ] Tiny README pointers inside existing manifests folders to link back to the index (optional)

Phase 2 — Command UX (wrappers only)
- [x] Decide task runner (Makefile vs Just); do not remove existing scripts
- [x] Define target names and map to current scripts (see catalog below)
- [x] Add wrappers at the repo root (make/just) that call existing scripts by path

Phase 3 — Testing program alignment
- [x] Align FE test plan structure to BE’s TEST_PLAN.md (unit, integration, security if any)
- [ ] Define E2E approach in TESTING_OVERVIEW.md (tools, scope, environments)
- [ ] Ensure CI documentation references the same canonical docs

Phase 4 — Optional compose consolidation exploration (docs-only now)
- [ ] Document what a “top-level compose” would look like (course_project/compose/dev.yml)
- [x] For now, recommend wrappers that call BE’s compose file for DB and keep services’ own flows

Phase 5 — Pre-GitOps notes
- [x] Capture the migration plan and boundaries in manifests-index.md

## Script catalog (draft mapping)

Goal: explain what exists today, the intent, and the future standard wrapper name. We will not delete/move; wrappers will call these paths.

- Top-level
  - azure-start.sh / azure-stop.sh — ops: start/stop Azure resources (owner: ops). Proposed wrappers: make azure-start / make azure-stop
  - build-apps.sh — build: build project apps. Proposed: make build
  - build-pp-and-lo.sh — build: build ping-pong and log_output images. Proposed: make build-pp-lo
  - cleanup.sh — ops: clean local artifacts/containers (document exact scope). Proposed: make clean

- course_project/
  - start-services.sh — dev: convenience launcher for services. Proposed: make dev
  - test-all.sh — test: run all course_project tests. Proposed: make test
  - test-be.sh — test: backend tests. Proposed: make test-be
  - test-fe.sh — test: frontend tests. Proposed: make test-fe

- course_project/todo-backend/
  - docker-compose.dev.yml — dev: Postgres for local dev + ephemeral test DB. Canonical for BE dev DB.
  - start-dev.sh — dev: start backend in dev mode. Proposed: make be-dev
  - start-db.sh — dev: start only DB (via compose). Proposed: make db-up (wrapper calls this)
  - test-all.sh — test: run all backend tests. Proposed: make test-be

- ping-pong/
  - quality.sh — test/lint/quality for ping-pong. Proposed: make pp-quality

- log_output/
  - docker-compose.yml, dev helpers (document scope). Proposed: make logserver-up/down

Note: This is not exhaustive; docs/development/script-catalog.md will list all entries with purpose and current path. Mark deprecated/confusing scripts with clear “use X instead” guidance.

## Compose and DB policy (docs-only)
- Keep backend docker-compose.dev.yml as the source of truth for local Postgres. Document clearly in local-dev.md.
- For discoverability, add a wrapper target (e.g., make db-up) at the repo root that delegates to todo-backend/start-db.sh or docker-compose.dev.yml. No file moves now.
- Tests keep their own isolation logic; local dev DB is persistent and shared.

## Testing program shape
- Backend: canonical at course_project/todo-backend/tests/TEST_PLAN.md (already strong). All references should link here.
- Frontend: add course_project/todo-app/TEST_PLAN.md with same structure.
- Project-level: add course_project/TESTING_OVERVIEW.md covering categories (unit, integration, security, E2E), environments (local, CI), and ownership.
- E2E: independent of FE/BE; define location (e.g., course_project/e2e/) and tools later; include in TESTING_OVERVIEW.md first.

## Task runner recommendation
- Start with a Makefile at the repo root for maximum ubiquity. Keep targets thin; each calls existing scripts by path. Later we can switch to Just if desired.
- Implemented target names:
  - make local-dev, make db-up, make db-down
  - make compose-up, make compose-down, make compose-logs
  - make help (prints modes and target descriptions)

## Open decisions
- Task runner: Makefile (recommended) vs Just (optional later). Default: Makefile.
- E2E stack: decide on tool (Playwright vs Cypress vs pytest+httpx). Document in TESTING_OVERVIEW.md first.
- Frontend test tech: align with current stack; document in FE TEST_PLAN.md.

## Immediate next actions
- [x] Create docs/overview/repo-map.md and docs/overview/onboarding.md
- [x] Create docs/development/local-dev.md with DB/compose policy and clear links to BE compose
- [x] Create docs/development/script-catalog.md (first pass with the table above and more entries)
- [x] Create docs/testing/index.md and course_project/TESTING_OVERVIEW.md
- [x] Create course_project/todo-app/TEST_PLAN.md (skeleton mirroring BE)
- [x] Create docs/platform/manifests-index.md (index and GitOps note)
- [x] Decide task runner (tentatively Makefile) and define target list (no implementation yet)
- [x] Add Makefile wrappers for the two dev modes and DB helpers

## Conventions (docs)
- Avoid duplication: link to the canonical source (e.g., backend TEST_PLAN.md).
- Keep docs short; use links and checklists.
- Each manifests directory should briefly state scope and point to manifests-index.md.
