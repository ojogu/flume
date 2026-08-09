.PHONY: help migrate migrate-gen migrate-up rebuild/all deploy start stop restart logs

MESSAGE ?=

help:
	@echo "Flume Makefile"
	@echo ""
	@echo "Migrations:"
	@echo "  make migrate MESSAGE='<msg>'   Generate and apply migration"
	@echo "  make migrate-gen               Generate migration only"
	@echo "  make migrate-up                Apply pending migrations"
	@echo ""
	@echo "Rebuild (build + restart):"
	@echo "  make rebuild/backend            Rebuild and restart backend"
	@echo "  make rebuild/frontend           Rebuild and restart frontend"
	@echo "  make rebuild/docs              Rebuild and restart docs"
	@echo "  make rebuild/worker            Rebuild and restart worker"
	@echo "  make rebuild/all               Rebuild all components"
	@echo ""
	@echo "Deploy:"
	@echo "  make deploy                     Full deploy (down + rebuild all + up)"
	@echo ""
	@echo "Container Lifecycle:"
	@echo "  make start                      docker compose up -d"
	@echo "  make stop                       docker compose down"
	@echo "  make restart                    stop + start"
	@echo "  make logs                       docker compose logs -f"
	@echo "  make logs/backend              docker compose logs -f backend"
	@echo "  make logs/frontend             docker compose logs -f frontend"
	@echo "  make logs/docs                 docker compose logs -f docs"
	@echo ""
	@echo "Stop Individual Service:"
	@echo "  make down/backend              Stop backend"
	@echo "  make down/frontend             Stop frontend"
	@echo "  make down/docs                Stop docs"

# === Migrations ===

migrate:
ifndef MESSAGE
	@echo "ERROR: MESSAGE is required"
	@echo "Usage: make migrate MESSAGE='<description>'"
	@exit 1
endif
	cd backend && uv run alembic revision --autogenerate -m "$(MESSAGE)" && uv run alembic upgrade head

migrate-gen:
ifndef MESSAGE
	@echo "ERROR: MESSAGE is required"
	@echo "Usage: make migrate-gen MESSAGE='<description>'"
	@exit 1
endif
	cd backend && uv run alembic revision --autogenerate -m "$(MESSAGE)"

migrate-up:
	cd backend && uv run alembic upgrade head

# === Rebuild ===

rebuild/backend:
	docker compose up -d --build backend

rebuild/frontend:
	docker rmi --force flume-frontend
	docker compose up -d --build frontend

rebuild/docs:
	docker compose up -d --build docs

rebuild/worker:
	docker compose up -d --build worker

rebuild/all: rebuild/backend rebuild/frontend rebuild/docs rebuild/worker

# === Deploy ===

deploy: stop rebuild/all start

# === Container Lifecycle ===

start:
	docker compose up -d

stop:
	docker compose down

restart: stop start

logs:
	docker compose logs -f

logs/backend:
	docker compose logs -f backend

logs/frontend:
	docker compose logs -f frontend

logs/docs:
	docker compose logs -f docs

# === Stop Individual Service ===

down/backend:
	docker compose stop backend

down/frontend:
	docker compose stop frontend

down/docs:
	docker compose stop docs
