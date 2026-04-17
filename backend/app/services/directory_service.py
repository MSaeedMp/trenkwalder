from typing import Any

from app.core.observability import get_logger
from app.models import Employee
from app.repositories.employee_repository import EmployeeRepository

logger = get_logger(__name__)


class DirectoryService:
    """Search the employee directory and get headcount breakdowns."""

    def __init__(self, employee_repo: EmployeeRepository) -> None:
        self._repo = employee_repo

    async def find_employees(
        self,
        name: str | None = None,
        department: str | None = None,
        role: str | None = None,
    ) -> list[Employee]:
        """Search the employee directory by any combination of name, department, or role."""
        if not any([name, department, role]):
            msg = "At least one of name, department, or role is required"
            raise ValueError(msg)

        results: list[Employee] = []
        if name:
            results.extend(self._repo.find_by_name(name))
        if department:
            results.extend(self._repo.filter_by_department(department))
        if role:
            results.extend(self._repo.filter_by_role(role))

        seen: set[str] = set()
        unique: list[Employee] = []
        for e in results:
            if e.id not in seen:
                seen.add(e.id)
                unique.append(e)

        logger.info(
            "directory_lookup", name=name, department=department, role=role, results=len(unique)
        )
        return unique

    async def get_department_headcount(
        self,
        department: str | None = None,
    ) -> dict[str, Any]:
        """Get the number of employees per department, or for a specific department."""
        if department:
            count = self._repo.count_for_department(department)
            return {"department": department, "headcount": count}
        return self._repo.count_by_department()
