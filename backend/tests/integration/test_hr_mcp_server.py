import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
def server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-c", "from mcp_server.server import mcp; mcp.run(transport='stdio')"],
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_tools(server_params: StdioServerParameters) -> None:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            tool_names = {t.name for t in result.tools}
            assert "get_vacation_balance" in tool_names
            assert "get_payroll_summary" in tool_names
            assert len(result.tools) >= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_vacation_balance(server_params: StdioServerParameters) -> None:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_vacation_balance", {"employee_id": "me"})
            assert len(result.content) > 0
            text = result.content[0].text  # type: ignore[union-attr]
            assert "remaining_days" in text
            assert "18" in text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_payroll_summary(server_params: StdioServerParameters) -> None:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_payroll_summary", {"employee_id": "me"})
            assert len(result.content) > 0
            text = result.content[0].text  # type: ignore[union-attr]
            assert "net_eur" in text
            assert "3850" in text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unknown_employee_returns_zeros(server_params: StdioServerParameters) -> None:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_vacation_balance", {"employee_id": "unknown"})
            text = result.content[0].text  # type: ignore[union-attr]
            assert '"remaining_days": 0' in text
