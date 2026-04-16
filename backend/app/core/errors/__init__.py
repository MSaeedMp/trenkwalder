from app.core.errors.catalog import (
    BaseCatalog,
    ErrorSpec,
    HRErrors,
    IngestionErrors,
    RAGErrors,
    ToolErrors,
)
from app.core.errors.exceptions import BusinessError, Conflict, NotFound, ServiceUnavailable
from app.core.errors.handlers import install_exception_handlers

__all__ = [
    "BaseCatalog",
    "BusinessError",
    "Conflict",
    "ErrorSpec",
    "HRErrors",
    "IngestionErrors",
    "NotFound",
    "RAGErrors",
    "ServiceUnavailable",
    "ToolErrors",
    "install_exception_handlers",
]
