import json
from typing import Any

import pytest
from google.genai import types

from app.models import Employee
from app.schemas.rag import ChunkResult
from app.tools.descriptions import LOCAL_TOOLS
from app.tools.registry import Services, build_tool_declarations, dispatch


class FakeRAGService:
    async def search(
        self, query: str, source_filter: str | None = None, top_k: int = 5
    ) -> list[ChunkResult]:
        return [ChunkResult(text="found it", source="doc.md", page=1, section="Intro")]


class FakeDirectoryService:
    async def find_employees(
        self, name: str | None = None, department: str | None = None, role: str | None = None
    ) -> list[Employee]:
        if not any([name, department, role]):
            msg = "At least one of name, department, or role is required"
            raise ValueError(msg)
        return [Employee("me", "Alex", "a@t.com", "Eng", "Dev", "", "2021-01-01", "Vienna")]

    async def get_department_headcount(self, department: str | None = None) -> dict[str, Any]:
        if department:
            return {"department": department, "headcount": 3}
        return {"Engineering": 3, "Sales": 2}


class FakeHRService:
    async def call(self, name: str, args: dict[str, Any]) -> str:
        return json.dumps({"employee_id": "me", "remaining_days": 18})


class FakeMCPClient:
    def gemini_tool_declarations(self) -> list[types.FunctionDeclaration]:
        return [
            types.FunctionDeclaration(
                name="get_vacation_balance",
                description="Get vacation balance",
                parameters=types.Schema(type=types.Type.OBJECT, properties={}),
            ),
        ]


@pytest.fixture
def services() -> Services:
    return Services(
        rag=FakeRAGService(),  # type: ignore[arg-type]
        directory=FakeDirectoryService(),  # type: ignore[arg-type]
        hr=FakeHRService(),  # type: ignore[arg-type]
    )


@pytest.mark.unit
def test_build_tool_declarations_merges() -> None:
    fake_mcp = FakeMCPClient()
    result = build_tool_declarations(fake_mcp)  # type: ignore[arg-type]
    assert len(result) == len(LOCAL_TOOLS) + 1
    names = {d.name for d in result}
    assert "search_documents" in names
    assert "find_employees" in names
    assert "get_department_headcount" in names
    assert "get_vacation_balance" in names


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_search_documents(services: Services) -> None:
    result = await dispatch("search_documents", {"query": "vacation policy"}, services)
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["text"] == "found it"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_find_employees(services: Services) -> None:
    result = await dispatch("find_employees", {"department": "Eng"}, services)
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["name"] == "Alex"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_headcount(services: Services) -> None:
    result = await dispatch("get_department_headcount", {}, services)
    parsed = json.loads(result)
    assert parsed["Engineering"] == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_unknown_forwards_to_hr(services: Services) -> None:
    result = await dispatch("get_vacation_balance", {"employee_id": "me"}, services)
    parsed = json.loads(result)
    assert parsed["remaining_days"] == 18


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_find_employees_no_params_returns_error(services: Services) -> None:
    result = await dispatch("find_employees", {}, services)
    parsed = json.loads(result)
    assert "error" in parsed
    assert "At least one" in parsed["error"]
