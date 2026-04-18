from typing import Any, cast

from google.genai import types
from mcp import ClientSession
from mcp.types import Tool as MCPTool

from app.core.observability import get_logger

logger = get_logger(__name__)

JSON_SCHEMA_NOISE = {"$schema", "additionalProperties", "$id", "$ref", "$defs"}
JSON_TYPE_TO_GEMINI: dict[str, types.Type] = {
    "string": types.Type.STRING,
    "number": types.Type.NUMBER,
    "integer": types.Type.INTEGER,
    "boolean": types.Type.BOOLEAN,
    "array": types.Type.ARRAY,
    "object": types.Type.OBJECT,
}


def convert_schema(schema: dict[str, Any]) -> types.Schema:
    """Map the JSON Schema subset MCP tools use into Gemini's schema type."""
    clean: dict[str, Any] = {k: v for k, v in schema.items() if k not in JSON_SCHEMA_NOISE}
    schema_type = JSON_TYPE_TO_GEMINI.get(str(clean.get("type", "object")), types.Type.OBJECT)

    properties: dict[str, types.Schema] | None = None
    raw_props = clean.get("properties")
    if isinstance(raw_props, dict):
        typed_props = cast(dict[str, Any], raw_props)
        properties = {}
        for k, v in typed_props.items():
            if isinstance(v, dict):
                properties[k] = convert_schema(cast(dict[str, Any], v))

    return types.Schema(
        type=schema_type,
        properties=properties or {},
        description=str(clean.get("description", "")),
    )


def mcp_tool_to_declaration(tool: MCPTool) -> types.FunctionDeclaration:
    """Convert an MCP Tool to a Gemini FunctionDeclaration."""
    input_schema = tool.inputSchema or {}
    params = (
        convert_schema(input_schema)
        if input_schema
        else types.Schema(type=types.Type.OBJECT, properties={})
    )
    return types.FunctionDeclaration(
        name=tool.name,
        description=tool.description or "",
        parameters=params,
    )


class MCPClient:
    """Connects to an already-running MCP server and forwards tool calls."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session
        self._tools: list[MCPTool] = []
        self._declarations: list[types.FunctionDeclaration] = []

    async def initialize(self) -> None:
        """Initialize the session and discover tools."""
        await self._session.initialize()
        result = await self._session.list_tools()
        self._tools = list(result.tools)
        self._declarations = [mcp_tool_to_declaration(t) for t in self._tools]
        logger.info(
            "mcp_tools_discovered", count=len(self._tools), names=[t.name for t in self._tools]
        )

    def gemini_tool_declarations(self) -> list[types.FunctionDeclaration]:
        return list(self._declarations)

    async def call(self, name: str, args: dict[str, Any]) -> str:
        logger.info("mcp_call", tool=name, args=args)
        result = await self._session.call_tool(name, args)
        parts = [getattr(c, "text", str(c)) for c in result.content]
        return "\n".join(parts)
