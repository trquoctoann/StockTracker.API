from __future__ import annotations

from starlette.types import ASGIApp, Receive, Scope, Send
from structlog.contextvars import bind_contextvars

from app.common.auth.context_token_codec import ContextTokenCodec
from app.common.auth.identity_token_codec import IdentityTokenCodec
from app.common.current_user import reset_current_user_id, set_current_user_id


class AuthContextMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        identity_codec: IdentityTokenCodec,
        context_codec: ContextTokenCodec,
    ):
        self.app = app
        self._identity_codec = identity_codec
        self._context_codec = context_codec

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        auth_header = headers.get(b"authorization")
        user_ctx_token = None
        if auth_header:
            token = self._extract_bearer_token(auth_header.decode("utf-8", errors="ignore"))
            if token:
                principal = (
                    self._context_codec.decode(token)
                    if ContextTokenCodec.is_context_token(token)
                    else await self._identity_codec.decode(token)
                )
                state = scope.setdefault("state", {})
                if isinstance(state, dict):
                    state["auth_principal"] = principal
                bind_contextvars(token_sub=principal.subject)
                user_ctx_token = set_current_user_id(principal.subject)
        try:
            await self.app(scope, receive, send)
        finally:
            if user_ctx_token is not None:
                reset_current_user_id(user_ctx_token)

    @staticmethod
    def _extract_bearer_token(authorization_header: str) -> str | None:
        parts = authorization_header.strip().split(" ", 1)
        if len(parts) != 2:
            return None
        scheme, token = parts
        if scheme.lower() != "bearer" or not token:
            return None
        return token.strip()
