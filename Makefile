APP_NAME=fastapi_app
DC=docker compose

.PHONY: help build up down restart logs shell db-shell migrate makemigrations test clean

help:
	@echo "Available commands:"
	@echo "  make build           Build containers"
	@echo "  make up              Start services"
	@echo "  make down            Stop services"
	@echo "  make restart         Restart services"
	@echo "  make logs            Show logs"
	@echo "  make shell           Enter app container"
	@echo "  make db-shell        Enter postgres shell"
	@echo "  make migrate         Apply migrations"
	@echo "  make makemigrations  Create new migration"
	@echo "  make test            Run tests"
	@echo "  make clean           Remove containers & volumes"

build:
	$(DC) build

up:
	$(DC) up -d

down:
	$(DC) down

restart:
	$(DC) down && $(DC) up -d

logs:
	$(DC) logs -f

shell:
	$(DC) exec web bash

db-shell:
	$(DC) exec db psql -U postgres -d app_db

migrate:
	$(DC) exec web alembic upgrade head

makemigrations:
	$(DC) exec web alembic revision --autogenerate -m "auto migration"

test:
	$(DC) exec web pytest

clean:
	$(DC) down -v