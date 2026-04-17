import sys
from contextlib import AsyncExitStack, asynccontextmanager

import lancedb
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.api.v1.router import router as v1_router
from app.clients import MCPClient
from app.core.config import Settings
from app.core.errors import install_exception_handlers
from app.core.observability import AccessLogMiddleware, get_logger, setup_logger
from pipelines import run_all_pipelines

settings = Settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger(
        log_level=settings.log_level,
        json_format=settings.app_env != "development",
    )
    logger.info("app_starting", title=app.title, env=settings.app_env)

    db = lancedb.connect(settings.vector_store_path)
    run_all_pipelines(settings, db)
    app.state.db = db

    # Spawn the MCP server and connect the client
    stack = AsyncExitStack()
    await stack.__aenter__()
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-c", "from mcp_server.server import mcp; mcp.run(transport='stdio')"],
    )
    read, write = await stack.enter_async_context(stdio_client(server_params))
    session = await stack.enter_async_context(ClientSession(read, write))

    mcp_client = MCPClient(session)
    await mcp_client.initialize()
    app.state.mcp_client = mcp_client
    logger.info("mcp_client_ready")

    yield

    await stack.aclose()
    logger.info("app_shutting_down", title=app.title)


app = FastAPI(
    title="Trenkwalder Chatbot",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AccessLogMiddleware, log_name="app.access")
app.add_middleware(CorrelationIdMiddleware)

install_exception_handlers(app)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "trenkwalder-chatbot"}
