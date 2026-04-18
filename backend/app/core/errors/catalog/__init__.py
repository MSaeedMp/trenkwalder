from app.core.errors.catalog.base import BaseCatalog, ErrorSpec
from app.core.errors.catalog.directory import DirectoryErrors
from app.core.errors.catalog.framework import (
    CODE_HTTP_ERROR,
    CODE_INTERNAL_ERROR,
    CODE_VALIDATION_ERROR,
    MESSAGE_INTERNAL_ERROR,
    MESSAGE_VALIDATION_ERROR,
)
from app.core.errors.catalog.hr import HRErrors
from app.core.errors.catalog.ingestion import IngestionErrors
from app.core.errors.catalog.rag import RAGErrors
from app.core.errors.catalog.tool import ToolErrors

__all__ = [
    "CODE_HTTP_ERROR",
    "CODE_INTERNAL_ERROR",
    "CODE_VALIDATION_ERROR",
    "MESSAGE_INTERNAL_ERROR",
    "MESSAGE_VALIDATION_ERROR",
    "BaseCatalog",
    "DirectoryErrors",
    "ErrorSpec",
    "HRErrors",
    "IngestionErrors",
    "RAGErrors",
    "ToolErrors",
]
