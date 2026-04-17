import pytest
from mcp.types import Tool as MCPTool

from app.clients.mcp_client import convert_schema, mcp_tool_to_declaration


@pytest.mark.unit
def test_convert_simple_schema() -> None:
    schema = {
        "type": "object",
        "properties": {
            "employee_id": {"type": "string", "description": "The employee ID"},
        },
    }
    result = convert_schema(schema)
    assert str(result.type) == "Type.OBJECT"
    assert "employee_id" in (result.properties or {})


@pytest.mark.unit
def test_convert_schema_strips_noise() -> None:
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": False,
        "type": "object",
        "properties": {"x": {"type": "string"}},
    }
    result = convert_schema(schema)
    assert str(result.type) == "Type.OBJECT"


@pytest.mark.unit
def test_convert_empty_schema() -> None:
    result = convert_schema({})
    assert str(result.type) == "Type.OBJECT"


@pytest.mark.unit
def test_mcp_tool_to_declaration() -> None:
    tool = MCPTool(
        name="get_vacation_balance",
        description="Returns vacation days remaining",
        inputSchema={
            "type": "object",
            "properties": {
                "employee_id": {"type": "string"},
            },
        },
    )
    fd = mcp_tool_to_declaration(tool)
    assert fd.name == "get_vacation_balance"
    assert fd.description == "Returns vacation days remaining"
    assert fd.parameters is not None
    assert "employee_id" in (fd.parameters.properties or {})


@pytest.mark.unit
def test_mcp_tool_no_input_schema() -> None:
    tool = MCPTool(
        name="ping",
        description="Health check",
        inputSchema={},
    )
    fd = mcp_tool_to_declaration(tool)
    assert fd.name == "ping"
    assert fd.parameters is not None
