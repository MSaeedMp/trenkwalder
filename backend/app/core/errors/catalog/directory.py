from app.core.errors.catalog.base import BaseCatalog, ErrorSpec
from app.core.errors.exceptions import BadRequest


class DirectoryErrors(BaseCatalog):
    MISSING_SEARCH_CRITERIA = ErrorSpec(
        message="At least one of name, department, or role is required",
        exception=BadRequest,
    )
