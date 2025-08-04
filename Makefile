.PHONY: help build up down logs test clean install dev demo

help:
	@echo "MCP Memory Server - Comandi disponibili:"
	@echo "  make install  - Installa dipendenze Python"
	@echo "  make build    - Costruisce container Docker"
	@echo "  make up       - Avvia servizi con Docker Compose"
	@echo "  make down     - Ferma servizi"
	@echo "  make logs     - Mostra log dei servizi"
	@echo "  make test     - Esegue test"
	@echo "  make demo     - Esegue demo client"
	@echo "  make clean    - Pulisce tutto"
	@echo "  make dev      - Avvia in modalità sviluppo"

install:
	pip install -r requirements.txt

build:
	docker compose build

up:
	docker compose up -d
	@echo "✅ Servizi avviati!"
	@echo "📊 MongoDB Express: http://localhost:8081"
	@echo "🔍 Log: make logs"

down:
	docker compose down

logs:
	docker compose logs -f

test:
	pytest tests/ -v

demo:
	python examples/mcp_client.py

clean:
	docker compose down -v
	docker system prune -f
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

dev:
	python main.py

# Production commands
prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d

# Backup and restore
backup:
	docker compose exec mongodb mongodump --out /data/backup

restore:
	docker compose exec mongodb mongorestore /data/backup

# Health checks
health:
	@echo "🔍 Controllo salute servizi..."
	docker compose ps
	@echo "📊 Health check MongoDB..."
	docker compose exec mongodb mongosh --eval "db.adminCommand('ping')"
	@echo "🧠 Health check Memory Server..."
	python -c "import asyncio; from src.services import memory_service; print(asyncio.run(memory_service.health_check()))" 