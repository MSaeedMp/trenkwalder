import sys
from contextlib import AsyncExitStack, asynccontextmanager

import lancedb
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.api.v1.router import router as v1_router
from app.clients import MCPClient
from app.core.config import Settings
from app.core.errors import install_exception_handlers
from app.core.observability import AccessLogMiddleware, get_logger, setup_logger
from app.repositories import (
    ConversationRepository,
    EmployeeRepository,
    LanceDBVectorRepository,
)
from app.services.chat_service import ChatService
from app.services.directory_service import DirectoryService
from app.services.hr_service import HRService
from app.services.rag_service import RAGService
from app.tools.registry import Services, build_tool_declarations
from pipelines import run_all_pipelines
from pipelines.unstructured.transform import GeminiEmbeddingProvider

settings = Settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger(
        log_level=settings.log_level,
        json_format=settings.app_env != "development",
    )
    logger.info("app_starting", title=app.title, env=settings.app_env)

    # LanceDB + ETL pipelines
    db = lancedb.connect(settings.vector_store_path)
    run_all_pipelines(settings, db)

    # Repositories
    vector_repo = LanceDBVectorRepository(db)
    employee_repo = EmployeeRepository(db)
    conversation_repo = ConversationRepository(db)

    # MCP server + client
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
    logger.info("mcp_client_ready")

    # Embedding provider
    embedder = GeminiEmbeddingProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )

    # Services
    rag_service = RAGService(embedder=embedder, vector_repo=vector_repo)
    directory_service = DirectoryService(employee_repo=employee_repo)
    hr_service = HRService(mcp_client=mcp_client)
    services = Services(rag=rag_service, directory=directory_service, hr=hr_service)

    # Tool declarations
    tool_declarations = build_tool_declarations(mcp_client)

    # Gemini client
    genai_client = genai.Client(api_key=settings.gemini_api_key)

    # Chat service
    chat_service = ChatService(
        client=genai_client,
        services=services,
        tool_declarations=tool_declarations,
        conversation_repo=conversation_repo,
        model=settings.gemini_model,
    )

    # Only expose what endpoints need
    app.state.chat_service = chat_service
    app.state.conversation_repo = conversation_repo

    logger.info("app_ready")
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
