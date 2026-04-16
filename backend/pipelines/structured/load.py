from dataclasses import asdict

import lancedb

from app.models import Employee


def write_employees(db: lancedb.DBConnection, employees: list[Employee]) -> None:
    """Write Employee records to the LanceDB employees table."""
    if not employees:
        return
    records = [asdict(e) for e in employees]
    db.create_table("employees", data=records, mode="overwrite")  # type: ignore[reportUnknownMemberType]
