import tempfile
from dataclasses import asdict

import lancedb
import pytest

from app.models import Employee
from app.repositories import EmployeeRepository

EMPLOYEES = [
    Employee(
        "me",
        "Alex Johnson",
        "alex@test.com",
        "Engineering",
        "Senior Developer",
        "Maria",
        "2021-03-15",
        "Vienna",
    ),
    Employee(
        "e001",
        "Maria Schmidt",
        "maria@test.com",
        "Engineering",
        "Engineering Manager",
        "",
        "2019-06-01",
        "Vienna",
    ),
    Employee(
        "e002",
        "Thomas Weber",
        "thomas@test.com",
        "Engineering",
        "Backend Developer",
        "Maria",
        "2022-01-10",
        "Vienna",
    ),
    Employee(
        "e003", "David Kim", "david@test.com", "Sales", "Sales Director", "", "2019-01-20", "Vienna"
    ),
    Employee(
        "e004",
        "Emma Wilson",
        "emma@test.com",
        "Sales",
        "Account Manager",
        "David",
        "2020-07-14",
        "Linz",
    ),
]


@pytest.fixture
def repo() -> EmployeeRepository:
    tmpdir = tempfile.mkdtemp()
    db = lancedb.connect(tmpdir)
    db.create_table("employees", data=[asdict(e) for e in EMPLOYEES], mode="overwrite")  # type: ignore[reportUnknownMemberType]
    return EmployeeRepository(db)


@pytest.mark.integration
def test_find_by_name(repo: EmployeeRepository) -> None:
    results = repo.find_by_name("alex")
    assert len(results) == 1
    assert results[0].id == "me"


@pytest.mark.integration
def test_find_by_name_partial(repo: EmployeeRepository) -> None:
    results = repo.find_by_name("sch")
    assert len(results) == 1
    assert results[0].name == "Maria Schmidt"


@pytest.mark.integration
def test_filter_by_department(repo: EmployeeRepository) -> None:
    results = repo.filter_by_department("engineering")
    assert len(results) == 3


@pytest.mark.integration
def test_filter_by_department_case_insensitive(repo: EmployeeRepository) -> None:
    results = repo.filter_by_department("SALES")
    assert len(results) == 2


@pytest.mark.integration
def test_filter_by_role(repo: EmployeeRepository) -> None:
    results = repo.filter_by_role("manager")
    assert len(results) == 2
    roles = {r.role for r in results}
    assert "Engineering Manager" in roles
    assert "Account Manager" in roles


@pytest.mark.integration
def test_count_by_department(repo: EmployeeRepository) -> None:
    counts = repo.count_by_department()
    assert counts["Engineering"] == 3
    assert counts["Sales"] == 2


@pytest.mark.integration
def test_count_for_department(repo: EmployeeRepository) -> None:
    assert repo.count_for_department("Sales") == 2
    assert repo.count_for_department("Nonexistent") == 0
