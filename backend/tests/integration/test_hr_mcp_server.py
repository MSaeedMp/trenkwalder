import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command=sys.executable,
    args=["-c", "from mcp_server.server import mcp; mcp.run(transport='stdio')"],
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mcp_tools_and_call() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = {t.name for t in (await session.list_tools()).tools}
            assert "get_vacation_balance" in tools
            assert "get_payroll_summary" in tools

            result = await session.call_tool("get_vacation_balance", {"employee_id": "me"})
            text = result.content[0].text  # type: ignore[union-attr]
            assert "18" in text
