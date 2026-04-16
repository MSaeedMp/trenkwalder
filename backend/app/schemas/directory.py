from pydantic import BaseModel


class EmployeeResponse(BaseModel):
    id: str
    name: str
    email: str
    department: str
    role: str
    manager: str
    start_date: str
    location: str
