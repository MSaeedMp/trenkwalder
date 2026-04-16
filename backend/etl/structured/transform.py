import polars as pl

from app.models import Employee


def to_employees(df: pl.DataFrame) -> list[Employee]:
    """Validate rows and convert to Employee dataclass instances."""
    required = {"id", "name", "email", "department", "role", "manager", "start_date", "location"}
    missing = required - set(df.columns)
    if missing:
        msg = f"CSV missing columns: {sorted(missing)}"
        raise ValueError(msg)

    employees: list[Employee] = []
    for row in df.fill_null("").to_dicts():
        employees.append(
            Employee(
                id=str(row["id"]),
                name=str(row["name"]),
                email=str(row["email"]),
                department=str(row["department"]),
                role=str(row["role"]),
                manager=str(row["manager"]),
                start_date=str(row["start_date"]),
                location=str(row["location"]),
            )
        )
    return employees
