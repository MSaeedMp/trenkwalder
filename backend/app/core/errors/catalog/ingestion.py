from app.core.errors.catalog.base import BaseCatalog, ErrorSpec
from app.core.errors.exceptions import BadRequest, ServiceUnavailable


class IngestionErrors(BaseCatalog):
    UNSUPPORTED_FORMAT = ErrorSpec(
        message="Unsupported document format: {format!r}",
        exception=BadRequest,
    )
    PARSE_FAILED = ErrorSpec(
        message="Failed to parse {source!r}: {reason}",
        exception=ServiceUnavailable,
    )
    EMBEDDING_FAILED = ErrorSpec(
        message="Embedding failed for {source!r}: {reason}",
        exception=ServiceUnavailable,
    )
