from collections import Counter
from typing import Any, cast

import lancedb

from app.core.observability import get_logger
from app.models import Employee

logger = get_logger(__name__)


def _row_to_employee(row: dict[str, Any]) -> Employee:
    return Employee(
        id=str(row.get("id", "")),
        name=str(row.get("name", "")),
        email=str(row.get("email", "")),
        department=str(row.get("department", "")),
        role=str(row.get("role", "")),
        manager=str(row.get("manager", "")),
        start_date=str(row.get("start_date", "")),
        location=str(row.get("location", "")),
    )


class EmployeeRepository:
    """Queries the LanceDB employees table."""

    def __init__(self, db: lancedb.DBConnection) -> None:
        self._db = db

    def _get_all(self) -> list[Employee]:
        table = self._db.open_table("employees")
        rows = cast(list[dict[str, Any]], table.to_arrow().to_pylist())  # type: ignore[reportUnknownMemberType]
        return [_row_to_employee(row) for row in rows]

    def find_by_name(self, name: str) -> list[Employee]:
        """Case-insensitive substring match on name."""
        needle = name.lower()
        return [e for e in self._get_all() if needle in e.name.lower()]

    def filter_by_department(self, department: str) -> list[Employee]:
        """Exact match, case-insensitive."""
        needle = department.lower()
        return [e for e in self._get_all() if e.department.lower() == needle]

    def filter_by_role(self, role: str) -> list[Employee]:
        """Case-insensitive substring match on role."""
        needle = role.lower()
        return [e for e in self._get_all() if needle in e.role.lower()]

    def count_by_department(self) -> dict[str, int]:
        """Full breakdown of employees per department."""
        return dict(Counter(e.department for e in self._get_all()))

    def count_for_department(self, department: str) -> int:
        """Count employees in a single department."""
        return len(self.filter_by_department(department))
