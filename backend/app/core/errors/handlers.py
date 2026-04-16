from typing import cast

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ExceptionHandler

from app.core.errors.catalog import (
    CODE_HTTP_ERROR,
    CODE_INTERNAL_ERROR,
    CODE_VALIDATION_ERROR,
    MESSAGE_INTERNAL_ERROR,
    MESSAGE_VALIDATION_ERROR,
)
from app.core.errors.exceptions import BusinessError
from app.core.observability import get_logger
from app.schemas.error import ErrorResponse

logger = get_logger(__name__)


def business_error(_request: Request, exc: BusinessError) -> JSONResponse:
    logger.warning(
        "business_error",
        code=exc.code,
        message=exc.message,
        metadata=exc.metadata,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            metadata=exc.metadata,
        ).model_dump(),
    )


def validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("validation_error", errors=jsonable_encoder(exc.errors()))
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            code=CODE_VALIDATION_ERROR,
            message=MESSAGE_VALIDATION_ERROR,
            metadata={"errors": jsonable_encoder(exc.errors())},
        ).model_dump(),
    )


def http_exception(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning("http_exception", status=exc.status_code, detail=str(exc.detail))
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=CODE_HTTP_ERROR,
            message=str(exc.detail),
        ).model_dump(),
    )


def unhandled_error(_request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code=CODE_INTERNAL_ERROR,
            message=MESSAGE_INTERNAL_ERROR,
        ).model_dump(),
    )


def install_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BusinessError, cast(ExceptionHandler, business_error))
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_error),
    )
    app.add_exception_handler(
        StarletteHTTPException,
        cast(ExceptionHandler, http_exception),
    )
    app.add_exception_handler(Exception, unhandled_error)
