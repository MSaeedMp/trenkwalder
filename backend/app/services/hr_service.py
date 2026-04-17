import time
from typing import Any

from app.clients.mcp_client import MCPClient
from app.core.errors import ToolErrors
from app.core.observability import get_logger

logger = get_logger(__name__)


class HRService:
    """Forward HR tool calls to the MCP client with logging and error handling."""

    def __init__(self, mcp_client: MCPClient) -> None:
        self._mcp = mcp_client

    async def call(self, name: str, args: dict[str, Any]) -> str:
        """Call an HR tool via MCP and return the JSON result string."""
        start = time.perf_counter()
        try:
            result = await self._mcp.call(name, args)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info("hr_tool_called", tool=name, duration_ms=duration_ms)
            return result
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error("hr_tool_failed", tool=name, duration_ms=duration_ms, exc_info=exc)
            raise ToolErrors.TOOL_DISPATCH_FAILED.build(tool_name=name, reason=str(exc)) from exc
