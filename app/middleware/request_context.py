from __future__ import annotations

import time
import uuid

from starlette.types import ASGIApp, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, clear_contextvars

_REQUEST_ID_HEADERS = ("x-request-id", "x-correlation-id", "traceparent")


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

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
        client_ip = client[0] if client else None

        bind_contextvars(
            request_id=request_id,
            http_method=method,
            http_path=path,
            client_ip=client_ip,
            request_start_perf=start,
        )

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration_ms = round((time.perf_counter() - start) * 1000, 2)
                bind_contextvars(
                    status_code=message["status"],
                    duration_ms=duration_ms,
                )
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            clear_contextvars()

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
