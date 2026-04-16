from app.core.errors.catalog.base import BaseCatalog, ErrorSpec
from app.core.errors.exceptions import NotFound, ServiceUnavailable


class HRErrors(BaseCatalog):
    MCP_NOT_CONNECTED = ErrorSpec(
        message="HR MCP server is not connected",
        exception=ServiceUnavailable,
    )
    EMPLOYEE_NOT_FOUND = ErrorSpec(
        message="Employee {employee_id!r} not found",
        exception=NotFound,
    )
