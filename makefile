# ============================================================================
# VocaLearn AI Services - Makefile
# Convenient commands for Docker operations
# ============================================================================

.PHONY: help build up down restart logs shell clean test

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================
help: ## Show this help message
	@echo "VocaLearn AI Services - Docker Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Docker Build & Run
# ============================================================================
build: ## Build Docker image
	@echo "Building VocaLearn AI image..."
	docker build -t vocalearn-ai:latest .

build-no-cache: ## Build Docker image without cache
	@echo "Building VocaLearn AI image (no cache)..."
	docker build --no-cache -t vocalearn-ai:latest .

up: ## Start all services
	@echo "Starting VocaLearn AI services..."
	docker-compose up -d

up-build: ## Build and start all services
	@echo "Building and starting VocaLearn AI services..."
	docker-compose up -d --build

down: ## Stop all services
	@echo "Stopping VocaLearn AI services..."
	docker-compose down

restart: ## Restart all services
	@echo "Restarting VocaLearn AI services..."
	docker-compose restart

stop: ## Stop services without removing containers
	@echo "Stopping services..."
	docker-compose stop

start: ## Start stopped services
	@echo "Starting services..."
	docker-compose start

# ============================================================================
# Logs & Monitoring
# ============================================================================
logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View logs from API service only
	docker-compose logs -f vocalearn-ai

logs-redis: ## View logs from Redis
	docker-compose logs -f redis

# ============================================================================
# Container Access
# ============================================================================
shell: ## Open shell in API container
	docker-compose exec vocalearn-ai /bin/bash

shell-root: ## Open shell as root in API container
	docker-compose exec -u root vocalearn-ai /bin/bash

# ============================================================================
# Development
# ============================================================================
dev: ## Run in development mode with hot reload
	@echo "Starting development mode..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

test: ## Run tests inside container
	docker-compose exec vocalearn-ai pytest tests/ -v

# ============================================================================
# Maintenance
# ============================================================================
clean: ## Remove containers, networks, and volumes
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f

clean-all: ## Remove everything including images
	@echo "Removing all Docker artifacts..."
	docker-compose down -v --rmi all
	docker system prune -af --volumes

ps: ## Show running containers
	docker-compose ps

stats: ## Show container resource usage
	docker stats

health: ## Check health of services
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health && echo "\n✅ API is healthy" || echo "\n❌ API is unhealthy"

# ============================================================================
# Database & Cache
# ============================================================================
redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

redis-flush: ## Flush Redis cache
	docker-compose exec redis redis-cli FLUSHALL

# ============================================================================
# Production
# ============================================================================
prod-up: ## Start in production mode
	@echo "Starting production services..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-logs: ## View production logs
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

prod-down: ## Stop production services
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down


# Backup & Restore

backup: ## Backup volumes
	@echo "Creating backup..."
	@mkdir -p backups
	docker run --rm -v vocalearn-redis-data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/redis-backup-$$(date +%Y%m%d-%H%M%S).tar.gz -C /data .

restore: ## Restore from latest backup
	@echo "Restoring from backup..."
	@docker run --rm -v vocalearn-redis-data:/data -v $(PWD)/backups:/backup alpine sh -c "cd /data && tar xzf /backup/$$(ls -t /backup/*.tar.gz | head -1)"


# Debugging

inspect: ## Inspect API container
	docker inspect vocalearn-ai-service

top: ## Show running processes in API container
	docker-compose top vocalearn-ai

port: ## Show port mappings
	docker-compose port vocalearn-ai 8000

# CI/CD

ci-build: ## Build for CI/CD
	docker build --target builder -t vocalearn-ai:builder .
	docker build -t vocalearn-ai:latest .

ci-test: ## Run tests in CI/CD
	docker run --rm vocalearn-ai:latest pytest tests/ -v --cov


# Quick Commands

quick-start: build up logs ## Build, start, and show logs

quick-restart: down up logs ## Stop, start, and show logs

quick-clean: down clean ## Stop and clean everything