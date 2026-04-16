from app.core.errors.catalog.base import BaseCatalog, ErrorSpec
from app.core.errors.exceptions import NotFound, ServiceUnavailable


class RAGErrors(BaseCatalog):
    DOCUMENT_NOT_FOUND = ErrorSpec(
        message="Document {doc_id!r} not found in the index",
        exception=NotFound,
    )
    INDEX_NOT_LOADED = ErrorSpec(
        message="Vector index is not loaded — run ingest.py first",
        exception=ServiceUnavailable,
    )
