# =========================
# Makefile for NewsBotAI Stack
# =========================

DOCKER_COMPOSE := docker compose --env-file .env -f docker-compose.yml

# Prefer uvicorn on PATH, otherwise fall back to venv/.venv
UVICORN := $(shell which uvicorn 2>/dev/null || ( [ -x venv/bin/uvicorn ] && echo venv/bin/uvicorn ) || ( [ -x .venv/bin/uvicorn ] && echo .venv/bin/uvicorn ) || echo venv/bin/uvicorn)

# -------------------------
# Help
# -------------------------
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build              # Build all Docker images"
	@echo "  make up                 # Start all containers"
	@echo "  make up-mongodb         # Start only MongoDB"
	@echo "  make up-mongoexp        # Start only Mongo Express"
	@echo "  make up-qdrant          # Start only Qdrant"
	@echo "  make down               # Stop all containers"
	@echo "  make restart            # Restart all containers"
	@echo "  make rebuild            # Build images then restart all containers"
	@echo "  make logs-mongodb       # MongoDB logs"
	@echo "  make logs-mongoexp      # Mongo Express logs"
	@echo "  make logs-qdrant        # Qdrant logs"
	@echo "  make logs-qdrantui      # Qdrant Dashboard logs"
	@echo "  make db-shell           # Connect to MongoDB shell"
	@echo "  make run                # Run API server with Uvicorn"
	@echo "  make run-dev            # Run API server with Uvicorn (reload)"
	@echo "  make urls               # Show URLs"
	@echo "  make spacy-model        # Install spaCy English model"

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

.PHONY: rebuild
rebuild:
	$(DOCKER_COMPOSE) build --no-cache
	@$(MAKE) restart

# -------------------------
# Run API (Uvicorn)
# -------------------------
.PHONY: run
run:
	@# Activate project's venv (if present) then run uvicorn
	@if [ -f venv/bin/activate ]; then \
		. venv/bin/activate; \
	elif [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate; \
	fi; \
	$(UVICORN) main:app --host 0.0.0.0 --port 8000

.PHONY: run-dev
run-dev:
	@# Activate project's venv (if present) then run uvicorn with reload
	@if [ -f venv/bin/activate ]; then \
		. venv/bin/activate; \
	elif [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate; \
	fi; \
	$(UVICORN) main:app --host 0.0.0.0 --port 8000 --reload

# -------------------------
# Start individual services
# -------------------------
.PHONY: up-mongodb
up-mongodb:
	$(DOCKER_COMPOSE) up -d mongodb

.PHONY: up-mongoexp
up-mongoexp:
	$(DOCKER_COMPOSE) up -d mongo-express

.PHONY: up-qdrant
up-qdrant:
	$(DOCKER_COMPOSE) up -d qdrant

# -------------------------
# Logs
# -------------------------
.PHONY: logs-mongodb
logs-mongodb:
	$(DOCKER_COMPOSE) logs -f mongodb

.PHONY: logs-mongoexp
logs-mongoexp:
	$(DOCKER_COMPOSE) logs -f mongo-express

.PHONY: logs-qdrant
logs-qdrant:
	$(DOCKER_COMPOSE) logs -f qdrant

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
	@echo "  - MongoDB URI:       mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@localhost:27017/"
	@echo "  - Mongo Express:     http://localhost:$$(grep MONGO_EXPRESS_PORT .env | cut -d '=' -f2)"
	@echo "  - Qdrant API:        http://localhost:6333"
	@echo "  - Qdrant Dashboard:  http://localhost:6333/dashboard"
	@echo ""

# -------------------------
# Install spaCy model
# -------------------------
.PHONY: spacy-model
spacy-model:
	@echo "⚡ Installing spaCy English model..."
	@if [ -x venv/bin/python ]; then \
		venv/bin/python -m spacy download en_core_web_sm; \
	elif [ -x .venv/bin/python ]; then \
		.venv/bin/python -m spacy download en_core_web_sm; \
	else \
		python -m spacy download en_core_web_sm; \
	fi
	@echo "✅ spaCy model installed."
