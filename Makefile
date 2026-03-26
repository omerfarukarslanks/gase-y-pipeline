.PHONY: help dev up down build migrate seed test lint

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---- Docker ----
up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build all containers
	docker compose build

logs: ## View logs
	docker compose logs -f

# ---- Development ----
dev-backend: ## Run backend in dev mode
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend: ## Run frontend in dev mode
	cd frontend && npm run dev

dev-worker: ## Run Celery worker
	cd backend && celery -A app.workers.celery_app worker -l info

dev-infra: ## Start DB + Redis only
	docker compose up -d db redis

# ---- Database ----
migrate: ## Run database migrations
	cd backend && alembic upgrade head

migration: ## Create a new migration (usage: make migration msg="description")
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ---- Testing ----
test-backend: ## Run backend tests
	cd backend && pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

test: test-backend ## Run all tests

# ---- Setup ----
setup: ## Initial project setup
	cp -n .env.example .env || true
	docker compose up -d db redis
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "Setup complete! Run 'make dev-backend' and 'make dev-frontend' to start."
