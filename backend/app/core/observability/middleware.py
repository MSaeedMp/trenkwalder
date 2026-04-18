import time
from typing import TypedDict, cast

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from uvicorn._types import HTTPScope
from uvicorn.protocols.utils import get_path_with_query_string

_SKIP_PATHS = frozenset({"/health", "/metrics", "/favicon.ico"})


class _AccessInfo(TypedDict, total=False):
    status_code: int
    start_time: float


class AccessLogMiddleware:
    """Log one compact access event for each HTTP request."""

    def __init__(self, app: ASGIApp, log_name: str = "app.access") -> None:
        self.app = app
        self.access_logger = structlog.stdlib.get_logger(log_name)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        http_scope: HTTPScope = cast(HTTPScope, scope)

        path = http_scope.get("path", "")
        if path in _SKIP_PATHS:
            await self.app(scope, receive, send)
            return

        info: _AccessInfo = {"start_time": time.perf_counter()}

        async def inner_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                info["status_code"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, inner_send)
        except Exception:
            info["status_code"] = 500
            raise
        finally:
            duration_ms = (time.perf_counter() - info.get("start_time", 0.0)) * 1000
            client = http_scope.get("client")
            client_ip = client[0] if client else None

            log = (
                self.access_logger.info
                if info.get("status_code", 500) < 500
                else self.access_logger.error
            )
            log(
                "http_request",
                client_ip=client_ip,
                method=http_scope.get("method"),
                path=path,
                status_code=info.get("status_code"),
                url=get_path_with_query_string(http_scope),
                duration_ms=round(duration_ms, 2),
            )
