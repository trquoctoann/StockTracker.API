from __future__ import annotations

from starlette.types import ASGIApp, Receive, Scope, Send
from structlog.contextvars import bind_contextvars

from app.common.auth.keycloak_jwt_decoder import KeycloakJwtDecoder
from app.common.current_user import reset_current_user_id, set_current_user_id
from app.core.config import settings


class AuthContextMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self._decoder = KeycloakJwtDecoder.build(
            server_url=settings.OIDC_KEYCLOAK_SERVER_URL,
            realm_name=settings.OIDC_KEYCLOAK_REALM,
            client_id=settings.OIDC_KEYCLOAK_CLIENT_ID,
            client_secret_key=settings.OIDC_KEYCLOAK_CLIENT_SECRET,
            verify=settings.OIDC_KEYCLOAK_VERIFY_TLS,
        )

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
                principal = await self._decoder.decode_access_token(token)
                state = scope.setdefault("state", {})
                if isinstance(state, dict):
                    state["token_principal"] = principal
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
