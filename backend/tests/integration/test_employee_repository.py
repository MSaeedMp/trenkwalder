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
        "Senior Dev",
        "Maria",
        "2021-03-15",
        "Vienna",
    ),
    Employee(
        "e001",
        "Maria Schmidt",
        "maria@test.com",
        "Engineering",
        "Manager",
        "",
        "2019-06-01",
        "Vienna",
    ),
    Employee(
        "e002", "David Kim", "david@test.com", "Sales", "Director", "", "2019-01-20", "Vienna"
    ),
]


@pytest.fixture
def repo() -> EmployeeRepository:
    db = lancedb.connect(tempfile.mkdtemp())
    db.create_table("employees", data=[asdict(e) for e in EMPLOYEES], mode="overwrite")  # type: ignore[reportUnknownMemberType]
    return EmployeeRepository(db)


@pytest.mark.integration
def test_find_and_filter(repo: EmployeeRepository) -> None:
    assert len(repo.find_by_name("alex")) == 1
    assert len(repo.filter_by_department("engineering")) == 2
    assert repo.count_by_department() == {"Engineering": 2, "Sales": 1}
