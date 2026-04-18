from typing import Any

import pytest

from app.core.errors.exceptions import BadRequest, ServiceUnavailable
from app.models import Chunk, Employee
from app.services.directory_service import DirectoryService
from app.services.hr_service import HRService
from app.services.rag_service import RAGService


class FakeEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


class FakeVectorRepo:
    def search(
        self, query_vector: list[float], top_k: int = 5, source_filter: str | None = None
    ) -> list[Chunk]:
        return [
            Chunk(
                id="a:0:0", text="policy text", source="handbook.pdf", format="pdf", section="Leave"
            )
        ]


class FakeEmployeeRepo:
    def find_by_name(self, name: str) -> list[Employee]:
        return [Employee("me", "Alex", "a@t.com", "Eng", "Dev", "Maria", "2021-01-01", "Vienna")]

    def filter_by_department(self, department: str) -> list[Employee]:
        return self.find_by_name("")

    def filter_by_role(self, role: str) -> list[Employee]:
        return []

    def count_by_department(self) -> dict[str, int]:
        return {"Engineering": 3, "Sales": 2}

    def count_for_department(self, department: str) -> int:
        return 3


class FakeMCPClient:
    def __init__(self, error: Exception | None = None) -> None:
        self._error = error

    async def call(self, name: str, args: dict[str, Any]) -> str:
        if self._error:
            raise self._error
        return '{"remaining_days": 18}'


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rag_service_search() -> None:
    svc = RAGService(embedder=FakeEmbedder(), vector_repo=FakeVectorRepo())  # type: ignore[arg-type]
    results = await svc.search("vacation policy")
    assert len(results) == 1
    assert results[0].source == "handbook.pdf"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_directory_service_find_and_headcount() -> None:
    svc = DirectoryService(employee_repo=FakeEmployeeRepo())  # type: ignore[arg-type]

    employees = await svc.find_employees(name="Alex")
    assert employees[0].name == "Alex"

    headcount = await svc.get_department_headcount()
    assert headcount["Engineering"] == 3

    with pytest.raises(BadRequest, match="At least one"):
        await svc.find_employees()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hr_service_forwards_and_wraps_errors() -> None:
    svc = HRService(mcp_client=FakeMCPClient())  # type: ignore[arg-type]
    result = await svc.call("get_vacation_balance", {})
    assert "18" in result

    svc_err = HRService(mcp_client=FakeMCPClient(error=RuntimeError("down")))  # type: ignore[arg-type]
    with pytest.raises(ServiceUnavailable, match="down"):
        await svc_err.call("get_vacation_balance", {})
