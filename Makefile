# =========================
# Makefile for Local MongoDB Stack
# =========================

DOCKER_COMPOSE := docker compose --env-file .env -f docker-compose.yml

# -------------------------
# Help
# -------------------------
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build             # Build all Docker images"
	@echo "  make up                # Start all containers"
	@echo "  make up-mongodb        # Start only MongoDB"
	@echo "  make up-mongoexp       # Start only Mongo Express"
	@echo "  make down              # Stop all containers"
	@echo "  make restart           # Restart all containers"
	@echo "  make rebuild           # Build images then restart all containers"
	@echo "  make logs-mongodb      # MongoDB logs"
	@echo "  make logs-mongoexp     # Mongo Express logs"
	@echo "  make db-shell          # Connect to MongoDB shell"
	@echo "  make run               # Run API server with Uvicorn"
	@echo "  make run-dev           # Run API server with Uvicorn (reload)"
	@echo "  make urls              # Show URLs"

# -------------------------
# Build
# -------------------------
.PHONY: build
build:
	$(DOCKER_COMPOSE) build

# -------------------------
# Up / Down / Restart
# -------------------------
.PHONY: up
up:
	$(DOCKER_COMPOSE) up -d
	@$(MAKE) urls

.PHONY: down
down:
	$(DOCKER_COMPOSE) down

.PHONY: restart
restart: down up

# -------------------------
# Run API (Uvicorn)
# -------------------------
.PHONY: run
run:
	uvicorn main:app --host 0.0.0.0 --port 8000

.PHONY: run-dev
run-dev:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# -------------------------
# Start individual services
# -------------------------
.PHONY: up-mongodb
up-mongodb:
	$(DOCKER_COMPOSE) up -d mongodb

.PHONY: up-mongoexp
up-mongoexp:
	$(DOCKER_COMPOSE) up -d mongo-express

# -------------------------
# Logs
# -------------------------
.PHONY: logs-mongodb
logs-mongodb:
	$(DOCKER_COMPOSE) logs -f mongodb

.PHONY: logs-mongoexp
logs-mongoexp:
	$(DOCKER_COMPOSE) logs -f mongo-express

# -------------------------
# Mongo Shell
# -------------------------
.PHONY: db-shell
db-shell:
	$(DOCKER_COMPOSE) exec mongodb mongosh -u ${MONGO_INITDB_ROOT_USERNAME} -p ${MONGO_INITDB_ROOT_PASSWORD}

# -------------------------
# Show URLs
# -------------------------
.PHONY: urls
urls:
	@echo ""
	@echo "🌐 Available interfaces:"
	@echo "  - MongoDB URI:   mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@localhost:27017/"
	@echo "  - Mongo Express: http://localhost:$(shell grep MONGO_EXPRESS_PORT .env | cut -d '=' -f2)"
	@echo ""
