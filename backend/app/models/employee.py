from dataclasses import dataclass


@dataclass(frozen=True)
class Employee:
    id: str
    name: str
    email: str
    department: str
    role: str
    manager: str
    start_date: str
    location: str
