import json
from dataclasses import dataclass
from typing import Any

from google.genai import types

from app.clients.mcp_client import MCPClient
from app.core.observability import get_logger
from app.services.directory_service import DirectoryService
from app.services.hr_service import HRService
from app.services.rag_service import RAGService
from app.tools.descriptions import LOCAL_TOOLS

logger = get_logger(__name__)


@dataclass
class Services:
    rag: RAGService
    directory: DirectoryService
    hr: HRService


def build_tool_declarations(mcp_client: MCPClient) -> list[types.FunctionDeclaration]:
    """Merge local tool declarations with MCP-discovered ones."""
    mcp_tools = mcp_client.gemini_tool_declarations()
    all_tools = [*LOCAL_TOOLS, *mcp_tools]
    logger.info("tools_built", local=len(LOCAL_TOOLS), mcp=len(mcp_tools), total=len(all_tools))
    return all_tools


async def dispatch(name: str, args: dict[str, Any], services: Services) -> str:
    """Route a tool call to the correct service. Returns a JSON string."""
    logger.info("tool_dispatch", name=name)

    try:
        match name:
            case "search_documents":
                results = await services.rag.search(
                    query=str(args.get("query", "")),
                    source_filter=args.get("source_filter"),  # type: ignore[arg-type]
                )
                return json.dumps([r.model_dump() for r in results])

            case "find_employees":
                employees = await services.directory.find_employees(
                    name=args.get("name"),  # type: ignore[arg-type]
                    department=args.get("department"),  # type: ignore[arg-type]
                    role=args.get("role"),  # type: ignore[arg-type]
                )
                return json.dumps(
                    [
                        {
                            "id": e.id,
                            "name": e.name,
                            "email": e.email,
                            "department": e.department,
                            "role": e.role,
                            "location": e.location,
                        }
                        for e in employees
                    ]
                )

            case "get_department_headcount":
                result = await services.directory.get_department_headcount(
                    department=args.get("department"),  # type: ignore[arg-type]
                )
                return json.dumps(result)

            case _:
                return await services.hr.call(name, args)

    except ValueError as exc:
        return json.dumps({"error": str(exc)})
