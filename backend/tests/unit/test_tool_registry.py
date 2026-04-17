import json
from typing import Any

import pytest

from app.models import Employee
from app.schemas.rag import ChunkResult
from app.tools.registry import Services, dispatch


class FakeRAG:
    async def search(
        self, query: str, source_filter: str | None = None, top_k: int = 5
    ) -> list[ChunkResult]:
        return [ChunkResult(text="found", source="doc.md")]


class FakeDirectory:
    async def find_employees(
        self, name: str | None = None, department: str | None = None, role: str | None = None
    ) -> list[Employee]:
        return [Employee("me", "Alex", "a@t.com", "Eng", "Dev", "", "2021-01-01", "Vienna")]

    async def get_department_headcount(self, department: str | None = None) -> dict[str, Any]:
        return {"Engineering": 3}


class FakeHR:
    async def call(self, name: str, args: dict[str, Any]) -> str:
        return '{"remaining_days": 18}'


@pytest.fixture
def services() -> Services:
    return Services(rag=FakeRAG(), directory=FakeDirectory(), hr=FakeHR())  # type: ignore[arg-type]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_routes_correctly(services: Services) -> None:
    rag_result = json.loads(await dispatch("search_documents", {"query": "test"}, services))
    assert rag_result[0]["text"] == "found"

    emp_result = json.loads(await dispatch("find_employees", {"department": "Eng"}, services))
    assert emp_result[0]["name"] == "Alex"

    hr_result = json.loads(await dispatch("get_vacation_balance", {}, services))
    assert hr_result["remaining_days"] == 18
