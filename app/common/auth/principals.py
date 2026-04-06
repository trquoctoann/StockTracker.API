from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, EmailStr

from app.common.enum import RoleScope


class AuthTokenType(StrEnum):
    IDENTITY = "identity"
    CONTEXT = "context"


class IdentityPrincipal(BaseModel):
    token_type: Literal[AuthTokenType.IDENTITY] = AuthTokenType.IDENTITY
    subject: str
    username: str | None = None
    email: EmailStr | None = None


class ContextPrincipal(BaseModel):
    token_type: Literal[AuthTokenType.CONTEXT] = AuthTokenType.CONTEXT
    subject: str
    scope: RoleScope
    tenant_id: int | None = None
    user_version: int
    user_roles_version: int
    role_versions: dict[int, int]
    permissions_bitmap: int


AuthPrincipal = IdentityPrincipal | ContextPrincipal
