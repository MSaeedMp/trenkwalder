from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI

from app.core.bootstrap.database import init_database
from app.core.bootstrap.mcp import connect_mcp
from app.core.bootstrap.services import init_services
from app.core.config import Settings
from app.core.observability import get_logger, setup_logger

settings = Settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Boot all dependencies, yield, then tear down."""
    setup_logger(
        log_level=settings.log_level,
        json_format=settings.app_env != "development",
    )
    logger.info("app_starting", title=app.title, env=settings.app_env)

    repos = init_database(settings)

    stack = AsyncExitStack()
    await stack.__aenter__()
    mcp_client = await connect_mcp(stack)

    chat_service = init_services(settings, repos, mcp_client)

    app.state.chat_service = chat_service
    app.state.conversation_repo = repos.conversation

    logger.info("app_ready")
    try:
        yield
    finally:
        await stack.aclose()
        logger.info("app_shutting_down")
