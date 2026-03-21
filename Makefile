.PHONY: help local local-api local-frontend docker docker-build docker-down prod prod-build prod-down seed migrate logs

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────
# Local dev (SQLite, no Docker)
# ──────────────────────────────────────────────

local-setup: ## Set up local dev (create venvs, install deps, migrate, load fixtures)
	cd api-server && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
	cd frontend-server && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
	cd api-server && DJANGO_ENV=local .venv/bin/python manage.py migrate
	cd api-server && DJANGO_ENV=local .venv/bin/python manage.py seed_superuser
	cd api-server && DJANGO_ENV=local .venv/bin/python manage.py import_fixtures

local-api: ## Run API server locally (SQLite)
	cd api-server && DJANGO_ENV=local .venv/bin/python manage.py runserver 8000

local-frontend: ## Run frontend server locally
	cd frontend-server && DJANGO_ENV=local .venv/bin/python manage.py runserver 8001

local-mobile: ## Run mobile app (Expo)
	cd mobile && npx expo start

local-migrate: ## Run migrations locally
	cd api-server && DJANGO_ENV=local .venv/bin/python manage.py migrate

local-makemigrations: ## Create new migrations locally
	cd api-server && DJANGO_ENV=local .venv/bin/python manage.py makemigrations

# ──────────────────────────────────────────────
# Local Docker (Postgres)
# ──────────────────────────────────────────────

docker: ## Start local Docker environment
	docker compose up

docker-build: ## Build and start local Docker environment
	docker compose up --build

docker-down: ## Stop local Docker environment
	docker compose down

docker-migrate: ## Run migrations in Docker
	docker compose exec api python manage.py migrate

docker-makemigrations: ## Create migrations in Docker
	docker compose exec api python manage.py makemigrations

docker-seed: ## Seed data in Docker
	docker compose exec api python manage.py seed_data

docker-logs: ## View Docker logs
	docker compose logs -f

docker-shell: ## Open shell in API container
	docker compose exec api python manage.py shell

# ──────────────────────────────────────────────
# Data sync (fixtures — keeps SQLite & Postgres in sync)
# ──────────────────────────────────────────────

local-export: ## Export data from local SQLite to fixtures
	cd api-server && DJANGO_ENV=local .venv/bin/python manage.py export_fixtures

local-import: ## Import fixtures into local SQLite
	cd api-server && DJANGO_ENV=local .venv/bin/python manage.py import_fixtures

docker-export: ## Export data from Docker Postgres to fixtures
	docker compose exec api python manage.py export_fixtures

docker-import: ## Import fixtures into Docker Postgres
	docker compose exec api python manage.py import_fixtures

sync-to-local: ## Sync: export from Docker Postgres, import into local SQLite
	$(MAKE) docker-export
	$(MAKE) local-import

sync-to-docker: ## Sync: export from local SQLite, import into Docker Postgres
	$(MAKE) local-export
	$(MAKE) docker-import

# ──────────────────────────────────────────────
# Production Docker
# ──────────────────────────────────────────────

prod: ## Start production environment
	docker compose -f docker-compose.prod.yml up -d

prod-build: ## Build and start production environment
	docker compose -f docker-compose.prod.yml up -d --build

prod-down: ## Stop production environment
	docker compose -f docker-compose.prod.yml down

prod-migrate: ## Run migrations in production
	docker compose -f docker-compose.prod.yml exec api python manage.py migrate

prod-logs: ## View production logs
	docker compose -f docker-compose.prod.yml logs -f

prod-shell: ## Open shell in production API container
	docker compose -f docker-compose.prod.yml exec api python manage.py shell
