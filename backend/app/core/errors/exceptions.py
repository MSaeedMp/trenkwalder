from typing import Any


class BusinessError(Exception):
    status_code: int = 500
    default_code: str = "BUSINESS_ERROR"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code
        self.metadata = metadata or {}


class BadRequest(BusinessError):
    status_code = 400
    default_code = "BAD_REQUEST"


class NotFound(BusinessError):
    status_code = 404
    default_code = "NOT_FOUND"


class Conflict(BusinessError):
    status_code = 409
    default_code = "CONFLICT"


class ServiceUnavailable(BusinessError):
    status_code = 503
    default_code = "SERVICE_UNAVAILABLE"
