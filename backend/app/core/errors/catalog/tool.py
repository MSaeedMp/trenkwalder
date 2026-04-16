from app.core.errors.catalog.base import BaseCatalog, ErrorSpec
from app.core.errors.exceptions import BusinessError, NotFound


class ToolError(BusinessError):
    status_code = 500
    default_code = "TOOL_ERROR"


class ToolErrors(BaseCatalog):
    TOOL_NOT_FOUND = ErrorSpec(
        message="Tool {tool_name!r} is not registered",
        exception=NotFound,
    )
    TOOL_DISPATCH_FAILED = ErrorSpec(
        message="Tool {tool_name!r} failed: {reason}",
        exception=ToolError,
    )
    TOOL_TIMEOUT = ErrorSpec(
        message="Tool {tool_name!r} timed out after {seconds}s",
        exception=ToolError,
    )
