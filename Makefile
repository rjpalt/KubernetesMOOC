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

.PHONY: help local-dev db-up db-down compose-up compose-down compose-logs azure-start azure-stop clean build-images quality test test-be test-fe

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
	@echo
	@echo "$(BOLD)Course Project — Build & Quality$(RESET)"
	@echo "  $(BOLD)build-images$(RESET)    $(DIM)Build FE/BE/cron images; pass TAG=... (updates compose images)$(RESET)"
	@echo "  $(BOLD)quality$(RESET)         $(DIM)Run ruff across FE/BE; pass CHECK=1 for check-only$(RESET)"
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
else
	@./scripts/quality.sh
endif

azure-start:
	@./scripts/azure-start.sh

azure-stop:
	@./scripts/azure-stop.sh

clean:
	@./scripts/clean.sh
