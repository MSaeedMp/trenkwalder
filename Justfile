set dotenv-load := true

# List all available commands
default:
    @just --list

# --- Backend -----------------------------------------------------------------

# Install backend dependencies
install:
    cd backend && uv sync

# Run the backend with hot-reload: just dev [port=8000]
dev port="8000":
    cd backend && uv run uvicorn app.main:app --reload --port {{port}}

# Format + lint
lint:
    cd backend && uv run ruff format . && uv run ruff check . --fix

# Type-check
typecheck:
    cd backend && uv run pyright .

# Run all tests
test:
    cd backend && uv run pytest -v

# Run unit tests only (fast, no I/O)
unit:
    cd backend && uv run pytest -v -m unit

# Run integration tests only (real I/O)
integration:
    cd backend && uv run pytest -v -m integration

# Run tests with coverage report
test-cov:
    cd backend && uv run pytest -v --cov=app --cov=etl --cov-report=term-missing

# Run lint + typecheck + tests
ci:
    just lint
    just typecheck
    just test

# --- Frontend ----------------------------------------------------------------

# Install all frontend dependencies
frontend-install:
    cd frontend && pnpm install

# Start the web dev server (port 5173)
frontend-dev:
    cd frontend && pnpm dev

# Production build
frontend-build:
    cd frontend && pnpm build

# Lint all frontend code
frontend-lint:
    cd frontend && pnpm lint

# TypeScript type-check
frontend-typecheck:
    cd frontend && pnpm typecheck

# Run frontend tests
frontend-test:
    cd frontend && pnpm test

# --- Docker ------------------------------------------------------------------

# Build all Docker images
build:
    docker compose build

# Build and start all services
build-up:
    docker compose up -d --build

# Start all services
up:
    docker compose up -d

# Stop all services
down:
    docker compose down

# Show logs (all services, follow mode)
logs service="":
    {{ if service == "" { "docker compose logs -f" } else { "docker compose logs -f " + service } }}

# --- Local -------------------------------------------------------------------

# Start backend + frontend locally (no Docker)
dev-local:
    @echo "Starting backend on :8000 and frontend on :5173..."
    @just dev &
    @just frontend-dev

# Copy .env.example -> .env (initial setup)
init:
    cp -n .env.example .env || true
    @echo "Done. Set GEMINI_API_KEY in .env, then: just dev"

# Inspect the HR MCP server directly
mcp-dev:
    cd backend && uv run mcp dev mcp_server/server.py
