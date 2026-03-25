from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from app.core.config import settings


def _parse_log_level(name: str) -> int:
    level = logging.getLevelNamesMapping().get(name.upper())
    return level if level is not None else logging.INFO


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def configure_logging() -> None:
    level = _parse_log_level(settings.LOG_LEVEL)

    def add_service_context(
        _logger: object,
        _method: str,
        event_dict: dict[str, Any],
    ) -> dict[str, Any]:
        event_dict.setdefault("service", settings.log_service_name)
        event_dict.setdefault("environment", settings.ENVIRONMENT)
        event_dict.setdefault("trace_id", None)
        event_dict.setdefault("span_id", None)

        return event_dict

    timestamper = structlog.processors.TimeStamper(
        fmt="iso",
        utc=True,
        key="@timestamp",
    )

    shared_processors: list[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_service_context,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: Any = (
        structlog.processors.JSONRenderer() if settings.LOG_JSON else structlog.dev.ConsoleRenderer(colors=True)
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.EventRenamer("message"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    for name in ("uvicorn", "uvicorn.error", "fastapi"):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    if not settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
