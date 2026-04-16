from app.core.errors.catalog.base import BaseCatalog, ErrorSpec
from app.core.errors.exceptions import BusinessError


class IngestionError(BusinessError):
    status_code = 500
    default_code = "INGESTION_ERROR"


class IngestionErrors(BaseCatalog):
    UNSUPPORTED_FORMAT = ErrorSpec(
        message="Unsupported document format: {format!r}",
        exception=IngestionError,
    )
    PARSE_FAILED = ErrorSpec(
        message="Failed to parse {source!r}: {reason}",
        exception=IngestionError,
    )
    EMBEDDING_FAILED = ErrorSpec(
        message="Embedding failed for {source!r}: {reason}",
        exception=IngestionError,
    )
