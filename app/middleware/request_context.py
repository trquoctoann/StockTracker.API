from __future__ import annotations

import time
import uuid

from starlette.types import ASGIApp, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.logger import get_logger

_LOG = get_logger(__name__)

_REQUEST_ID_HEADERS = ("x-request-id", "x-correlation-id", "traceparent")


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self._quiet_paths = {"/health", "/health/"}

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()

        headers = dict(scope.get("headers") or [])
        path = scope.get("path", "")
        method = scope.get("method", "GET")

        request_id = self._extract_request_id(headers)

        client = scope.get("client")
        client_host = client[0] if client is not None else None

        bind_contextvars(request_id=request_id, http_method=method, http_path=path, client_host=client_host)

        status_code = 500
        error: Exception | None = None

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            error = exc
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 3)

            log_fn = self._select_log_level(path, status_code, error)

            log_fn(
                "HTTP_REQUEST",
                status_code=status_code,
                duration_ms=duration_ms,
                outcome="ERROR" if error else "COMPLETE",
            )

            clear_contextvars()

    def _select_log_level(self, path: str, status: int, error: Exception | None):
        if path in self._quiet_paths:
            return _LOG.debug
        if error or status >= 500:
            return _LOG.error
        if status >= 400:
            return _LOG.warning
        return _LOG.info

    @staticmethod
    def _extract_request_id(headers: dict[bytes, bytes]) -> str:
        def get_header(name: str) -> str | None:
            raw = headers.get(name.encode())
            if not raw:
                return None
            value = raw.decode().strip()
            return value or None

        traceparent = get_header("traceparent")
        if traceparent and traceparent.startswith("00-"):
            parts = traceparent.split("-")
            if len(parts) >= 2 and len(parts[1]) == 32:
                return parts[1]

        request_id = get_header("x-request-id")
        if request_id:
            return request_id

        correlation_id = get_header("x-correlation-id")
        if correlation_id:
            return correlation_id
        return str(uuid.uuid4())
