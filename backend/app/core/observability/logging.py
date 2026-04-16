import logging
import sys
from collections.abc import Iterable

import structlog
from asgi_correlation_id import CorrelationIdFilter
from structlog.types import EventDict, Processor, WrappedLogger


def _drop_color_message_key(
    _logger: WrappedLogger, _method_name: str, event_dict: EventDict
) -> EventDict:
    event_dict.pop("color_message", None)
    return event_dict


def _mask_pii_processor(
    _logger: WrappedLogger, _method_name: str, event_dict: EventDict
) -> EventDict:
    sensitive = ("password", "token", "authorization", "secret", "credit_card", "api_key", "apikey")
    for key in list(event_dict.keys()):
        if any(s in key.lower() for s in sensitive):
            event_dict[key] = "***MASKED***"
    return event_dict


def setup_logger(
    log_level: str = "INFO",
    log_name: str = "app",
    log_access_name: str = "app.access",
    json_format: bool = False,
    *,
    mask_pii: bool = True,
    extra_processors: Iterable[Processor] | None = None,
    enable_uvicorn_access_logs: bool = False,
) -> None:
    timestamper: Processor = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        _drop_color_message_key,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if mask_pii:
        shared_processors.append(_mask_pii_processor)

    if extra_processors:
        shared_processors.extend(list(extra_processors))

    if json_format:
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    renderer: Processor = (
        structlog.processors.JSONRenderer()
        if json_format
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIdFilter(uuid_length=32, default_value="-"))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level.upper())
    root_logger.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    for name in ("uvicorn", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = False
        uv_logger.setLevel(log_level.upper())
        uv_logger.addHandler(handler)

    uv_access = logging.getLogger("uvicorn.access")
    uv_access.handlers.clear()
    uv_access.propagate = False
    uv_access.setLevel(log_level.upper())
    uv_access.disabled = not enable_uvicorn_access_logs
    if enable_uvicorn_access_logs:
        uv_access.addHandler(handler)

    for name in (log_name, log_access_name):
        app_logger = logging.getLogger(name)
        app_logger.handlers.clear()
        app_logger.propagate = False
        app_logger.setLevel(log_level.upper())
        app_logger.addHandler(handler)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
