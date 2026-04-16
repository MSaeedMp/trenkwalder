# Trenkwalder Chatbot Challenge

FastAPI + React monorepo for the Trenkwalder chatbot challenge.

The current implementation provides the application foundation: a FastAPI backend with structured logging, correlation IDs, standard JSON error handling, a React/Vite frontend, Docker Compose startup, and backend/frontend quality checks.

## Stack

| Area | Technology |
| --- | --- |
| Backend | FastAPI, Pydantic, structlog, uv |
| Frontend | React 19, TypeScript, Vite, TanStack Router, TanStack Query, shadcn-style UI primitives |
| Tests | pytest, Vitest |
| Quality | Ruff, Pyright, ESLint, TypeScript |
| Runtime | Docker Compose |
| Task runner | just |

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                  FastAPI routers
│   │   ├── core/                 config, errors, observability
│   │   ├── repositories/         repository layer placeholders
│   │   ├── schemas/              Pydantic schemas
│   │   ├── services/             service layer placeholders
│   │   └── main.py               FastAPI app
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── src/
│   │   ├── components/ui/        UI primitives
│   │   ├── lib/                  router, query client, utilities
│   │   ├── routes/               TanStack Router routes
│   │   └── types/
│   ├── Dockerfile
│   ├── package.json
│   └── pnpm-lock.yaml
├── docker-compose.yml
├── Justfile
├── .env.example
└── README.md
```

## Prerequisites

- Docker Desktop
- `just`
- `uv`
- `pnpm`

On macOS:

```bash
brew install just
brew install uv
npm install -g pnpm
```

## Environment

This project uses a single environment file at the repo root.

```bash
just init
```

That creates `.env` from `.env.example` if it does not already exist. Set `GEMINI_API_KEY` in `.env` when working on the Gemini-backed chatbot features.

Important variables:

| Variable | Description |
| --- | --- |
| `APP_ENV` | `development`, `test`, or `production` |
| `DEBUG` | Enables FastAPI docs when true |
| `LOG_LEVEL` | Backend log level |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_MODEL` | Gemini model name |
| `DOCS_DIR` | Static document directory |
| `VECTOR_STORE_PATH` | LanceDB storage path |
| `CORS_ORIGINS` | Allowed frontend origins |

Do not commit `.env`.

## Run With Docker

```bash
just up
```

This starts:

| Service | URL |
| --- | --- |
| Backend | http://localhost:8000 |
| Backend health | http://localhost:8000/health |
| Backend docs | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |

Container names:

```text
trenkwalder-backend
trenkwalder-frontend
```

Useful Docker commands:

```bash
just logs
just logs backend
just logs frontend
just down
```

## Run Locally

Backend:

```bash
just install
just dev
```

Frontend:

```bash
just frontend-install
just frontend-dev
```

The frontend dev server proxies `/api` requests to `http://localhost:8000`.

## Checks

Backend:

```bash
just ci
```

This runs Ruff format/check, Pyright, and pytest.

Frontend:

```bash
just frontend-lint
just frontend-typecheck
just frontend-test
just frontend-build
```

Security checks used during review:

```bash
cd backend && uv run --with pip-audit pip-audit
rg -n "(API[_-]?KEY|SECRET|PASSWORD|TOKEN|PRIVATE[_-]?KEY|BEGIN (RSA|OPENSSH|PRIVATE)|GEMINI_API_KEY|sk-[A-Za-z0-9])" \
  -g '!node_modules' \
  -g '!backend/.venv' \
  -g '!frontend/node_modules' \
  -g '!frontend/dist' \
  -g '!backend/.pytest_cache' .
```

`pnpm audit` currently returns `410 Gone` from npm's retired audit endpoint for this pnpm version. For a public GitHub repository, enable Dependabot/security alerts for frontend dependency scanning.

## API

Implemented endpoint:

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "service": "trenkwalder-chatbot"
}
```

All API routes are mounted under `/api/v1` as they are added.

## Observability

The backend uses:

- `X-Correlation-ID` support via `asgi-correlation-id`
- structured logs with `structlog`
- request logging middleware
- standard JSON error envelopes

Health, metrics, and favicon requests are skipped in access logs to reduce noise.

## Notes For Reviewers

- The repo intentionally keeps only the root `.env.example`; local secrets belong in root `.env`.
- Docker Compose builds and starts the backend and frontend with `just up`.
- The project does not currently include Postgres, Redis, Alembic migrations, or a separate test-infra compose file.
