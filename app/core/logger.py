from __future__ import annotations

import logging
import os
import sys
import threading
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

import structlog
from colorama import Fore, Style
from sqlalchemy import event
from structlog.contextvars import get_contextvars

from app.core.config import settings

LEVEL_COLOR = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
}

MAX_SQL_LENGTH = 4000
_MAX_TRACEBACK_FRAMES_FULL = 8
_TRACE_HEAD = 2
_TRACE_TAIL = 4

_CONSOLE_MSG_EXCLUDED_KEYS = frozenset(
    {
        "level",
        "logger",
        "source",
        "message",
        "timestamp",
        "@timestamp",
        "service",
        "env",
        "request_id",
        "method",
        "path",
        "duration_ms",
        "thread",
        "http_method",
        "http_path",
        "error",
        "exception",
        "exception_cause",
        "event",
        "trace_id",
        "status_code",
        "client_ip",
        "request_start_perf",
        "_record",
        "func_name",
        "lineno",
        "filename",
        "level_number",
        "exc_info",
        "stack_info",
    }
)


def map_logger_name(_, __, event_dict):
    if "logger_name" in event_dict:
        event_dict["logger"] = event_dict.pop("logger_name")
    return event_dict


def map_source(_, __, event_dict):
    # Source = logger name (module/object that logs), without func_name.
    logger = event_dict.get("logger") or event_dict.get("name") or "-"
    if logger == "root":
        logger = "-"
    event_dict["source"] = logger
    return event_dict


def inject_logger_name(_, __, event_dict):
    if "logger" not in event_dict or event_dict["logger"] == "-":
        rec = event_dict.get("_record")
        if rec is not None and getattr(rec, "name", None):
            event_dict["logger"] = rec.name
        else:
            event_dict["logger"] = "-"
    return event_dict


def _shorten_path(path_str: str) -> str:
    try:
        return Path(path_str).name
    except (OSError, ValueError):
        return path_str.split(os.sep)[-1] if path_str else "?"


def _compact_traceback(tb) -> tuple[str, list[str]]:
    # Shorten stack but still enough for debugging: head + ... + tail + exception type/message.
    extracted = traceback.extract_tb(tb)
    if not extracted:
        return "", []

    frames: list[str] = []
    for f in extracted:
        fn = _shorten_path(f.filename)
        frames.append(f"{fn}:{f.lineno}:{f.name}")

    n = len(frames)
    if n <= _MAX_TRACEBACK_FRAMES_FULL:
        chain = " -> ".join(frames)
    else:
        head = frames[:_TRACE_HEAD]
        tail = frames[-_TRACE_TAIL:]
        omitted = n - _TRACE_HEAD - _TRACE_TAIL
        chain = " -> ".join(head) + f" -> ... ({omitted} frames) ... -> " + " -> ".join(tail)

    return chain, frames


def format_exc_info(_, __, event_dict):
    exc_info = event_dict.pop("exc_info", None)

    if not exc_info:
        return event_dict

    if exc_info is True:
        exc_info = sys.exc_info()
    elif isinstance(exc_info, BaseException):
        exc_info = (type(exc_info), exc_info, exc_info.__traceback__)

    if not isinstance(exc_info, tuple) or len(exc_info) != 3:
        return event_dict

    exc_type, exc_value, tb_obj = exc_info

    type_name = exc_type.__name__ if exc_type else "Exception"
    msg = str(exc_value) if exc_value is not None else ""
    event_dict["error"] = f"{type_name}: {msg}"

    if tb_obj is not None:
        chain, _frames = _compact_traceback(tb_obj)
        if chain:
            event_dict["exception"] = chain
        cause = exc_value.__cause__ if exc_value is not None else None
        if cause is not None:
            ctb = getattr(cause, "__traceback__", None)
            if ctb is not None:
                cc, _ = _compact_traceback(ctb)
                if cc:
                    event_dict["exception_cause"] = f"{type(cause).__name__}: {cause} @ {cc}"

    return event_dict


def normalize_fields(_, __, event_dict):
    event_dict["service"] = event_dict.get("service", settings.log_service_name)
    event_dict["env"] = event_dict.get("env", settings.ENVIRONMENT)

    event_dict["level"] = event_dict.get("level", "info").upper()

    event_dict["logger"] = event_dict.get("logger", "-")
    event_dict["source"] = event_dict.get("source", event_dict["logger"])

    ctx = get_contextvars()
    event_dict["request_id"] = event_dict.get("request_id") or ctx.get("request_id") or "-"

    event_dict["method"] = event_dict.get("http_method") or ctx.get("http_method") or "-"
    event_dict["path"] = event_dict.get("http_path") or ctx.get("http_path") or "-"

    dur = event_dict.get("duration_ms")
    if dur is None or dur == "-":
        start = ctx.get("request_start_perf") or event_dict.get("request_start_perf")
        if start is not None:
            event_dict["duration_ms"] = round((time.perf_counter() - start) * 1000, 2)
        else:
            event_dict["duration_ms"] = "-"

    event_dict["thread"] = threading.current_thread().name

    return event_dict


def console_renderer(_, __, event_dict):
    ts = event_dict.get("@timestamp")
    if not ts:
        ts = datetime.now(UTC).isoformat()

    level = event_dict.get("level", settings.LOG_LEVEL).upper()
    color = LEVEL_COLOR.get(level, "")

    source = event_dict.get("source", "-")
    request_id = event_dict.get("request_id", "-")
    method = event_dict.get("method", "-")
    path = event_dict.get("path", "-")
    duration = event_dict.get("duration_ms", "-")
    thread = event_dict.get("thread", "-")

    dur_str = f"{duration:.2f}" if isinstance(duration, float) else str(duration)

    msg = event_dict.get("message") or event_dict.get("event") or ""
    if msg is None:
        msg = ""

    extra_bits: list[str] = []
    for key, val in event_dict.items():
        if key in _CONSOLE_MSG_EXCLUDED_KEYS:
            continue
        if val is None or str(val) == "":
            continue
        extra_bits.append(f"{key}={val!r}")

    if extra_bits:
        msg = f"{msg}({', '.join(extra_bits)})" if msg else f"({', '.join(extra_bits)})"

    http_part = f"{method} {path}" if path not in ("-", "", None) else str(method)

    line = (
        f"{ts} "
        f"{color}[{level:^8}]{Style.RESET_ALL} | "
        f"{Fore.BLUE}{source:<50}{Style.RESET_ALL} "
        f"{Fore.WHITE}[ {thread} ]{Style.RESET_ALL} | "
        f"{Fore.MAGENTA}{request_id}{Style.RESET_ALL} | "
        f"{Fore.CYAN}{http_part}{Style.RESET_ALL} | "
        f"{Fore.YELLOW}{dur_str}{Style.RESET_ALL}ms | "
        f"{Fore.WHITE}{msg}{Style.RESET_ALL}"
    )

    if "error" in event_dict:
        line += f"\n{Fore.RED}{event_dict['error']}{Style.RESET_ALL}"

    if "exception" in event_dict:
        line += f"\n{Fore.YELLOW}{event_dict['exception']}{Style.RESET_ALL}"

    if "exception_cause" in event_dict:
        line += f"\n{Fore.YELLOW}caused by: {event_dict['exception_cause']}{Style.RESET_ALL}"

    return line


def json_renderer():
    return structlog.processors.JSONRenderer()


class DropNoiseFilter(logging.Filter):
    # Don't filter INFO+ (structlog usually leaves empty getMessage() before ProcessorFormatter).

    def filter(self, record):
        if record.levelno > logging.DEBUG:
            return True
        msg = record.getMessage()
        return bool(msg and msg.strip())


class DropEmptyDebugFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if not msg or not msg.strip():
            return False
        return not (record.levelno <= logging.DEBUG and not msg.strip())


class AppFocusedLogFilter(logging.Filter):
    # Only show logs from application (app.*) or warnings/errors anywhere; skip INFO/DEBUG from framework.
    # Allows adding one line of access log (uvicorn.access).

    _APP_PREFIX = "app."

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno >= logging.WARNING:
            return True
        name = record.name
        return bool(name.startswith(self._APP_PREFIX))


def setup_sql_logging(engine) -> None:
    if not settings.LOG_SQL:
        return

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def _before_cursor_execute(conn, _cursor, _statement, _parameters, _context, _executemany):
        conn.info["sql_start_time"] = time.perf_counter()

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def _after_cursor_execute(conn, _cursor, statement, _parameters, _context, _executemany):
        raw = (statement or "").strip()
        if not raw or raw.upper().startswith(("BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT", "RELEASE")):
            return

        start = conn.info.pop("sql_start_time", None)
        duration_ms = round((time.perf_counter() - start) * 1000, 2) if start else None

        sql = " ".join(raw.split())
        if len(sql) > MAX_SQL_LENGTH:
            sql = sql[:MAX_SQL_LENGTH] + "..."

        log = structlog.get_logger("app.database.sql").bind(
            service=settings.log_service_name,
            env=settings.ENVIRONMENT,
        )
        ctx = get_contextvars()
        log = log.bind(**{k: v for k, v in ctx.items() if k in ("request_id", "http_method", "http_path")})
        log.info(
            sql,
            duration_ms=duration_ms if duration_ms is not None else "-",
        )


def format_exception_for_response(exc: BaseException) -> str:
    lines: list[str] = [f"{type(exc).__name__}: {exc}"]
    tb = exc.__traceback__
    if tb is not None:
        chain, _ = _compact_traceback(tb)
        if chain:
            lines.append(chain)
    cause = exc.__cause__
    if cause is not None:
        lines.append(f"Caused by: {type(cause).__name__}: {cause}")
        ctb = getattr(cause, "__traceback__", None)
        if ctb is not None:
            cc, _ = _compact_traceback(ctb)
            if cc:
                lines.append(cc)
    return "\n".join(lines)


def setup_logging() -> None:
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        inject_logger_name,
        map_logger_name,
        map_source,
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="@timestamp"),
        normalize_fields,
        structlog.processors.EventRenamer("message"),
        format_exc_info,
    ]

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=console_renderer if not settings.LOG_JSON else json_renderer(),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(DropNoiseFilter())
    handler.addFilter(DropEmptyDebugFilter())
    handler.addFilter(AppFocusedLogFilter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(log_level)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True

    # Reduce noise from framework (startup / proactor / watch) while keeping ERROR/WARNING.
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("aio_pika").setLevel(logging.WARNING)
    logging.getLogger("aiormq").setLevel(logging.WARNING)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    return structlog.get_logger(name).bind(
        service=settings.log_service_name,
        env=settings.ENVIRONMENT,
    )
