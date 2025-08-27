# Thin wrappers to make the two dev modes explicit and unmistakable.
# No refactors or moves; calls existing scripts/compose files in-place.

# Files
COMPOSE_FILE := course_project/docker-compose.yaml
BE_COMPOSE_FILE := course_project/todo-backend/docker-compose.dev.yml

# Styling
BOLD := \033[1m
DIM := \033[2m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

.DEFAULT_GOAL := help

.PHONY: help local-dev db-up db-down compose-up compose-down compose-logs azure-start azure-stop clean build-images quality test test-be test-fe test-e2e-local test-e2e-remote

help:
	@echo "$(BOLD)Available targets$(RESET)"
	@echo
	@echo "$(BOLD)Course Project — Dev modes$(RESET)"
	@echo "  $(BOLD)local-dev$(RESET)       $(DIM)Run FE/BE locally (uv) + dev DB via backend compose$(RESET)"
	@echo "  $(BOLD)db-up$(RESET)           $(DIM)Start only the dev database (backend compose)$(RESET)"
	@echo "  $(BOLD)db-down$(RESET)         $(DIM)Stop the dev database (backend compose)$(RESET)"
	@echo "  $(BOLD)compose-up$(RESET)      $(DIM)Run FE, BE, and DB via docker compose (attached)$(RESET)"
	@echo "  $(BOLD)compose-down$(RESET)    $(DIM)Stop all compose services$(RESET)"
	@echo "  $(BOLD)compose-logs$(RESET)    $(DIM)Follow logs for the compose stack$(RESET)"
	@echo
	@echo "$(BOLD)Course Project — Tests$(RESET)"
	@echo "  $(BOLD)test$(RESET)            $(DIM)Run all tests (requires dev and test DB containers)$(RESET)"
	@echo "  $(BOLD)test-be$(RESET)         $(DIM)Run backend tests (requires dev and test DB containers)$(RESET)"
	@echo "  $(BOLD)test-fe$(RESET)         $(DIM)Run frontend tests$(RESET)"
	@echo "  $(BOLD)test-e2e-local$(RESET)  $(DIM)Run E2E tests against local Docker Compose stack$(RESET)"
	@echo "  $(BOLD)test-e2e-remote$(RESET) $(DIM)Run E2E tests against remote URL (requires TARGET_URL)$(RESET)"
	@echo
	@echo "$(BOLD)Course Project — Build & Quality$(RESET)"
	@echo "  $(BOLD)build-images$(RESET)    $(DIM)Build FE/BE/cron images; pass TAG=... (updates compose images)$(RESET)"
	@echo "  $(BOLD)quality$(RESET)         $(DIM)Run ruff across FE/BE and lint E2E tests; pass CHECK=1 for check-only$(RESET)"
	@echo
	@echo "$(BOLD)General$(RESET)"
	@echo "  $(BOLD)azure-start$(RESET)     $(DIM)Start Azure resources (wrapper)$(RESET)"
	@echo "  $(BOLD)azure-stop$(RESET)      $(DIM)Stop Azure resources (wrapper)$(RESET)"
	@echo "  $(BOLD)clean$(RESET)           $(DIM)Clean local artifacts/containers (wrapper)$(RESET)"
	@echo
	@echo "$(YELLOW)Modes$(RESET)"
	@echo "  $(GREEN)local-dev$(RESET): $(BOLD)MODE: Local app code (uv) + Docker DB$(RESET)"
	@echo "  $(GREEN)compose-up$(RESET): $(BOLD)MODE: All services via docker-compose (containers)$(RESET)"

local-dev:
	@echo "$(GREEN)==> MODE: Local app code (uv) + Docker DB$(RESET)"
	@./scripts/local-dev.sh

# Dev database lifecycle (backend compose is the canonical dev DB)
db-up:
	@echo "$(GREEN)==> Starting dev database (backend compose)$(RESET)"
	@./scripts/db-up.sh

db-down:
	@echo "$(YELLOW)==> Stopping dev database (backend compose)$(RESET)"
	@./scripts/db-down.sh

# Full stack via docker compose (attached by default)
compose-up:
	@echo "$(GREEN)==> MODE: All services via docker-compose (attached)$(RESET)"
	@./scripts/compose-up.sh

compose-down:
	@echo "$(YELLOW)==> Stopping compose stack$(RESET)"
	@./scripts/compose-down.sh

compose-logs:
	@echo "$(GREEN)==> Following compose logs (Ctrl+C to stop)$(RESET)"
	@./scripts/compose-logs.sh

# Tests
test:
	@./scripts/test-all.sh

test-be:
	@./scripts/test-be.sh

test-fe:
	@./scripts/test-fe.sh

test-e2e-local:
	@echo "$(GREEN)==> Running E2E tests against local Docker Compose stack$(RESET)"
	@./scripts/test-e2e-local.sh

test-e2e-remote:
ifndef TARGET_URL
	$(error TARGET_URL is required. Usage: make test-e2e-remote TARGET_URL=https://example.com)
endif
	@echo "$(GREEN)==> Running E2E tests against remote URL: $(TARGET_URL)$(RESET)"
	@./scripts/test-e2e-remote.sh "$(TARGET_URL)"

# Build & Quality wrappers for course_project
# Usage: make build-images TAG=v1.2.3
build-images:
ifndef TAG
	$(error TAG is required. Usage: make build-images TAG=vX.Y.Z)
endif
	@./scripts/build-images.sh "$(TAG)"

# Usage: make quality or make quality CHECK=1
quality:
ifeq ($(CHECK),1)
	@./scripts/quality.sh --check
	@echo "$(GREEN)==> Checking E2E test code quality$(RESET)"
	@if [ -d "course_project/tests/e2e" ]; then \
		cd course_project/tests/e2e && npm run lint --if-present || echo "No linting configured for E2E tests"; \
	else \
		echo "E2E tests directory not found - skipping E2E quality checks"; \
	fi
else
	@./scripts/quality.sh
	@echo "$(GREEN)==> Checking E2E test code quality$(RESET)"
	@if [ -d "course_project/tests/e2e" ]; then \
		cd course_project/tests/e2e && npm run lint:fix --if-present || echo "No linting configured for E2E tests"; \
	else \
		echo "E2E tests directory not found - skipping E2E quality checks"; \
	fi
endif

azure-start:
	@./scripts/azure-start.sh

azure-stop:
	@./scripts/azure-stop.sh

clean:
	@./scripts/clean.sh
