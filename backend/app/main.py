from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.core.bootstrap import lifespan
from app.core.config import Settings
from app.core.errors import install_exception_handlers
from app.core.observability import AccessLogMiddleware

settings = Settings()

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
