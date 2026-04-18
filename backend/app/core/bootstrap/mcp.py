import sys
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.clients import MCPClient
from app.core.observability import get_logger

logger = get_logger(__name__)


async def connect_mcp(stack: AsyncExitStack) -> MCPClient:
    """Spawn the HR MCP server subprocess and return a connected client."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-c", "from mcp_server.server import mcp; mcp.run(transport='stdio')"],
    )
    read, write = await stack.enter_async_context(stdio_client(server_params))
    session = await stack.enter_async_context(ClientSession(read, write))
    client = MCPClient(session)
    await client.initialize()
    logger.info("mcp_client_ready")
    return client
