import pytest

from app.models import Employee
from app.services import DirectoryService

EMPLOYEES = [
    Employee(
        "me",
        "Alex Johnson",
        "alex@t.com",
        "Engineering",
        "Senior Developer",
        "Maria",
        "2021-03-15",
        "Vienna",
    ),
    Employee(
        "e001", "Maria Schmidt", "maria@t.com", "Engineering", "Manager", "", "2019-06-01", "Vienna"
    ),
    Employee("e002", "David Kim", "david@t.com", "Sales", "Director", "", "2019-01-20", "Vienna"),
]


class FakeEmployeeRepo:
    def __init__(self, employees: list[Employee]) -> None:
        self._data = employees

    def find_by_name(self, name: str) -> list[Employee]:
        return [e for e in self._data if name.lower() in e.name.lower()]

    def filter_by_department(self, department: str) -> list[Employee]:
        return [e for e in self._data if e.department.lower() == department.lower()]

    def filter_by_role(self, role: str) -> list[Employee]:
        return [e for e in self._data if role.lower() in e.role.lower()]

    def count_by_department(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._data:
            counts[e.department] = counts.get(e.department, 0) + 1
        return counts

    def count_for_department(self, department: str) -> int:
        return len(self.filter_by_department(department))


@pytest.fixture
def svc() -> DirectoryService:
    return DirectoryService(FakeEmployeeRepo(EMPLOYEES))  # type: ignore[arg-type]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_by_name(svc: DirectoryService) -> None:
    results = await svc.find_employees(name="alex")
    assert len(results) == 1
    assert results[0].id == "me"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_by_department(svc: DirectoryService) -> None:
    results = await svc.find_employees(department="Engineering")
    assert len(results) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_requires_at_least_one_param(svc: DirectoryService) -> None:
    with pytest.raises(ValueError, match="At least one"):
        await svc.find_employees()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_deduplicates(svc: DirectoryService) -> None:
    results = await svc.find_employees(name="alex", department="Engineering")
    ids = [r.id for r in results]
    assert ids.count("me") == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_headcount_all(svc: DirectoryService) -> None:
    result = await svc.get_department_headcount()
    assert result == {"Engineering": 2, "Sales": 1}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_headcount_single(svc: DirectoryService) -> None:
    result = await svc.get_department_headcount(department="Sales")
    assert result == {"department": "Sales", "headcount": 1}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_headcount_nonexistent(svc: DirectoryService) -> None:
    result = await svc.get_department_headcount(department="Nonexistent")
    assert result == {"department": "Nonexistent", "headcount": 0}
