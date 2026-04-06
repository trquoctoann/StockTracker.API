from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends
from jose import JWTError, jwt

from app.common.auth.principals import AuthTokenType, ContextPrincipal
from app.common.enum import RoleScope
from app.core.config import settings
from app.exception.exception import (
    ContextTokenUnauthorizedException,
)


@dataclass(frozen=True, slots=True)
class ContextTokenPayload:
    subject: str
    scope: RoleScope
    tenant_id: int | None
    user_version: int
    user_roles_version: int
    role_versions: dict[int, int]
    permissions_bitmap: int


class ContextTokenCodec(ABC):
    @abstractmethod
    def encode(self, payload: ContextTokenPayload) -> tuple[str, int]:
        pass

    @abstractmethod
    def decode(self, token: str) -> ContextPrincipal:
        pass

    @staticmethod
    def is_context_token(token: str) -> bool:
        try:
            claims = jwt.get_unverified_claims(token)
        except JWTError:
            return False
        return claims.get("token_type") == AuthTokenType.CONTEXT.value


class ContextTokenCodecImpl(ContextTokenCodec):
    def encode(self, payload: ContextTokenPayload) -> tuple[str, int]:
        now = datetime.now(tz=UTC)
        expires = now + timedelta(seconds=settings.AUTH_CONTEXT_TOKEN_TTL_SECONDS)
        claims = {
            "token_type": AuthTokenType.CONTEXT.value,
            "sub": payload.subject,
            "scope": payload.scope.value,
            "tid": payload.tenant_id,
            "uv": payload.user_version,
            "urv": payload.user_roles_version,
            "rvs": payload.role_versions,
            "pbm": payload.permissions_bitmap,
            "iss": settings.AUTH_CONTEXT_TOKEN_ISSUER,
            "iat": int(now.timestamp()),
            "exp": int(expires.timestamp()),
        }
        token = jwt.encode(claims, settings.AUTH_CONTEXT_TOKEN_SECRET, algorithm=settings.AUTH_CONTEXT_TOKEN_ALGORITHM)
        return token, settings.AUTH_CONTEXT_TOKEN_TTL_SECONDS

    def decode(self, token: str) -> ContextPrincipal:
        try:
            claims = jwt.decode(
                token,
                settings.AUTH_CONTEXT_TOKEN_SECRET,
                algorithms=[settings.AUTH_CONTEXT_TOKEN_ALGORITHM],
                issuer=settings.AUTH_CONTEXT_TOKEN_ISSUER,
                options={"verify_aud": False},
            )
        except JWTError as exc:
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"}) from exc

        if claims.get("token_type") != AuthTokenType.CONTEXT.value:
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"})

        try:
            raw_role_versions = claims["rvs"]
            if not isinstance(raw_role_versions, dict):
                raise TypeError()
            role_versions = {int(role_id): int(version) for role_id, version in raw_role_versions.items()}

            return ContextPrincipal(
                subject=str(claims["sub"]),
                scope=RoleScope(str(claims["scope"])),
                tenant_id=claims.get("tid"),
                user_version=int(claims["uv"]),
                user_roles_version=int(claims["urv"]),
                role_versions=role_versions,
                permissions_bitmap=int(claims["pbm"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"}) from exc


def get_context_token_codec() -> ContextTokenCodec:
    return ContextTokenCodecImpl()


ContextTokenCodecDep = Annotated[ContextTokenCodec, Depends(get_context_token_codec)]
