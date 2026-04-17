import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.clients import MCPClient

SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["-c", "from mcp_server.server import mcp; mcp.run(transport='stdio')"],
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_discovers_tools() -> None:
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            client = MCPClient(session)
            await client.initialize()
            declarations = client.gemini_tool_declarations()
            assert len(declarations) >= 2
            names = {d.name for d in declarations}
            assert "get_vacation_balance" in names
            assert "get_payroll_summary" in names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_call_vacation_balance() -> None:
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            client = MCPClient(session)
            await client.initialize()
            result = await client.call("get_vacation_balance", {"employee_id": "me"})
            assert "remaining_days" in result
            assert "18" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_call_payroll_summary() -> None:
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            client = MCPClient(session)
            await client.initialize()
            result = await client.call("get_payroll_summary", {"employee_id": "me"})
            assert "net_eur" in result
            assert "3850" in result
