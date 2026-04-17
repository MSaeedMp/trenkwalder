# Agentic AI — Trenkwalder Challenge

A fullstack chatbot that answers questions from company documents (PDF, Markdown, TXT), queries an employee directory (CSV), and fetches live HR data (vacation balance, payroll) from an external MCP service.

Built for the Trenkwalder coding challenge.

## What It Does

Ask natural language questions and the agent decides which tool to use:

- **"What is the remote work policy?"** → searches the employee handbook (PDF) via vector search
- **"Who works in Engineering?"** → queries the employee directory (CSV → LanceDB)
- **"How many vacation days do I have?"** → calls the HR MCP server for live data
- **"Tell me a joke"** → politely declines, stays on topic

The agent uses Gemini 2.5 Flash with tool calling. It reads tool descriptions and decides which to invoke — no hardcoded routing.

## Architecture

```
Frontend (React + Vite)
    │ POST /api/v1/chat (AI SDK Data Stream Protocol v4)
    ▼
FastAPI Backend
    │
    ├─ ChatService → Gemini agentic loop (up to 5 tool rounds)
    │       │
    │       ├─ search_documents → RAGService → VectorRepository → LanceDB (chunks)
    │       ├─ find_employees   → DirectoryService → EmployeeRepository → LanceDB (employees)
    │       └─ get_vacation_*   → HRService → MCPClient → MCP server subprocess
    │
    ├─ Pipelines (ETL at startup)
    │       ├─ Structured:   CSV → polars → LanceDB employees table
    │       └─ Unstructured: PDF/MD/TXT → chunk → embed → LanceDB chunks table
    │
    └─ MCP Server (separate process, stdio)
            └─ get_vacation_balance, get_payroll_summary
```

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Google Gen AI SDK (Gemini), MCP, LanceDB, polars, structlog |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4, shadcn/ui, AI SDK v4 (`useChat`) |
| Data | LanceDB (vector + structured), no external database |
| External | Mock HR service via MCP over stdio |
| Quality | ruff, pyright (strict), ESLint, pytest |

## Quick Start

### Prerequisites

- A [Gemini API key](https://aistudio.google.com/apikey) (free)
- **Option A — Docker:** Just [Docker](https://docs.docker.com/get-docker/)
- **Option B — Local:** Python 3.11+, Node.js 20+, [uv](https://docs.astral.sh/uv/) (`brew install uv`), [pnpm](https://pnpm.io/) (`npm install -g pnpm`)

### Option A: Docker (fastest)

```bash
git clone <repo-url>
cd trenkwalder

cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your-key-here

docker compose up -d --build
```

Open http://localhost:5173 — done.

```bash
docker compose logs -f    # watch logs
docker compose down        # stop
```

### Option B: Local Setup

```bash
git clone <repo-url>
cd trenkwalder

cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your-key-here

# Install backend
cd backend
uv sync

# Install frontend
cd ../frontend
pnpm install
```

Terminal 1 — backend:
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend:
```bash
cd frontend
pnpm dev
```

Open http://localhost:5173

On first startup, the backend automatically:
1. Ingests documents from `backend/docs/` into LanceDB (structured + unstructured ETL)
2. Spawns the HR MCP server as a subprocess
3. Connects the MCP client and discovers tools

If you have Docker installed, you can skip the Python/Node setup entirely:

```bash
git clone <repo-url>
cd trenkwalder

cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your-key-here

docker compose up -d --build
```

That's it. Open http://localhost:5173

To check logs:
```bash
docker compose logs -f
```

To stop:
```bash
docker compose down
```

### Run Tests

```bash
cd backend
uv run pytest -v
```

9 tests covering: health endpoint, ETL chunking, vector search, employee repository, MCP server, services (RAG, directory, HR), and tool dispatch.

## Things to Try

| Question | Data Path |
|---|---|
| How many vacation days do I have left? | MCP → get_vacation_balance |
| What was my last payslip? | MCP → get_payroll_summary |
| What is the remote work policy? | RAG → employee_handbook.pdf |
| What health insurance options are available? | RAG → benefits.md |
| What should I do if I see a policy violation? | RAG → code_of_conduct.txt |
| Who works in the Engineering department? | Directory → employees.csv |
| How many people are in each department? | Directory → headcount |
| Find Maria Schmidt | Directory → name search |
| What's the capital of France? | Refused — off-topic |

## Project Structure

```
backend/
├── app/
│   ├── api/v1/chat.py          POST /api/v1/chat endpoint
│   ├── clients/mcp_client.py   MCPClient — connects to HR MCP server
│   ├── core/                   config, observability, errors
│   ├── domain/chat/            agentic loop, citations, system prompt
│   ├── models/                 DB table schemas (Employee, Chunk, Message, Conversation)
│   ├── repositories/           LanceDB data access (vector, employee, conversation)
│   ├── schemas/                API request/response models (Pydantic)
│   ├── services/               business logic (ChatService, RAGService, DirectoryService, HRService)
│   ├── tools/                  tool registry + Gemini function declarations
│   └── main.py                 FastAPI app + lifespan
├── pipelines/
│   ├── structured/             CSV → polars → LanceDB (extract, transform, load, trigger)
│   └── unstructured/           PDF/MD/TXT → chunk → embed → LanceDB
├── mcp_server/
│   └── server.py               Mock HR MCP server (FastMCP, stdio)
├── docs/                       Sample knowledge base (PDF, MD, TXT, CSV)
└── tests/                      unit + integration tests

frontend/
├── src/
│   ├── components/Chat.tsx     Main chat UI with useChat hook
│   ├── components/ui/          shadcn/ui components
│   ├── routes/                 TanStack Router (file-based)
│   └── lib/                    router, query client, utils
└── index.html
```

## Design Decisions

- **No router/classifier** — Gemini reads tool descriptions and decides which to call. Adding a new capability = adding a tool description + service method.
- **LanceDB for everything** — vectors (chunks), structured data (employees), conversations, messages. Single data store, file-backed, no external database. Designed to swap to Postgres + pgvector later (models define table schemas like SQLAlchemy).
- **ETL at startup** — pipelines run when LanceDB is empty, skip when populated. No manual ingest step.
- **MCP for external services** — the HR service is a real MCP server subprocess. The app connects via stdio, discovers tools dynamically, converts schemas to Gemini format.
- **Service/repository pattern** — even without SQL. Repositories wrap LanceDB, services hold business logic, the API layer is thin.

