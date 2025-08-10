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

.PHONY: help local-dev db-up db-down compose-up compose-down compose-logs

help:
	@echo "$(BOLD)Available targets$(RESET)"
	@echo "  $(BOLD)local-dev$(RESET)     $(DIM)Run FE/BE locally (uv) + dev DB via backend compose$(RESET)"
	@echo "  $(BOLD)db-up$(RESET)         $(DIM)Start only the dev database (backend compose)$(RESET)"
	@echo "  $(BOLD)db-down$(RESET)       $(DIM)Stop the dev database (backend compose)$(RESET)"
	@echo "  $(BOLD)compose-up$(RESET)    $(DIM)Run FE, BE, and DB via docker compose (attached)$(RESET)"
	@echo "  $(BOLD)compose-down$(RESET)  $(DIM)Stop all compose services$(RESET)"
	@echo "  $(BOLD)compose-logs$(RESET)  $(DIM)Follow logs for the compose stack$(RESET)"
	@echo
	@echo "$(YELLOW)Modes$(RESET)"
	@echo "  $(GREEN)local-dev$(RESET): $(BOLD)MODE: Local app code (uv) + Docker DB$(RESET)"
	@echo "  $(GREEN)compose-up$(RESET): $(BOLD)MODE: All services via docker-compose (containers)$(RESET)"

local-dev:
	@echo "$(GREEN)==> MODE: Local app code (uv) + Docker DB$(RESET)"
	@./course_project/start-services.sh

# Dev database lifecycle (backend compose is the canonical dev DB)
db-up:
	@echo "$(GREEN)==> Starting dev database (backend compose)$(RESET)"
	@./course_project/todo-backend/start-db.sh

db-down:
	@echo "$(YELLOW)==> Stopping dev database (backend compose)$(RESET)"
	@docker compose -f $(BE_COMPOSE_FILE) down

# Full stack via docker compose (attached by default)
compose-up:
	@echo "$(GREEN)==> MODE: All services via docker-compose (attached)$(RESET)"
	@docker compose -f $(COMPOSE_FILE) up

compose-down:
	@echo "$(YELLOW)==> Stopping compose stack$(RESET)"
	@docker compose -f $(COMPOSE_FILE) down

compose-logs:
	@echo "$(GREEN)==> Following compose logs (Ctrl+C to stop)$(RESET)"
	@docker compose -f $(COMPOSE_FILE) logs -f
