from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request

from app.common.auth.auth_access import get_authenticated_principal
from app.exception.exception import UnauthorizedException
from app.modules.role.application.role_query_service import RoleFetchSpec, RoleQueryService
from app.modules.role.role_dependency import RoleQueryServiceDep
from app.modules.user.application.user_query_service import UserFetchSpec, UserQueryService
from app.modules.user.domain.user_entity import UserEntity
from app.modules.user.user_dependency import UserQueryServiceDep

_current_user_id_ctx: ContextVar[str | None] = ContextVar("current_user_id", default=None)


def get_current_user_id() -> str:
    uid = _current_user_id_ctx.get()
    return uid if uid else ""


def set_current_user_id(user_id: str) -> Token:
    return _current_user_id_ctx.set(user_id)


def reset_current_user_id(token: Token) -> None:
    _current_user_id_ctx.reset(token)


class CurrentUserService:
    def __init__(
        self,
        request: Request,
        user_query_service: UserQueryService,
        role_query_service: RoleQueryService,
    ) -> None:
        self._request = request
        self._user_query_service = user_query_service
        self._role_query_service = role_query_service
        self._cached_user: UserEntity | None = None

    async def get_current_user(self) -> UserEntity:
        if self._cached_user is not None:
            return self._cached_user

        principal = get_authenticated_principal(self._request)
        try:
            user_id = UUID(principal.subject)
        except ValueError as exc:
            raise UnauthorizedException(headers={"WWW-Authenticate": "Bearer"}) from exc

        self._cached_user = await self._user_query_service.get_by_id(user_id, fetch_spec=UserFetchSpec(user_roles=True))
        return self._cached_user

    async def has_permissions(self, permission_codes: set[str]) -> bool:
        if not permission_codes:
            return True

        user = await self.get_current_user()
        user_roles = user.user_roles or []
        role_ids = {role_id for user_role in user_roles for role_id in user_role.role_ids}
        if not role_ids:
            return False
        roles = await self._role_query_service.find_all_by_ids(
            list(role_ids), fetch_spec=RoleFetchSpec(permissions=True)
        )
        granted_codes = {permission.code for role in roles for permission in (role.permissions or [])}
        return permission_codes.issubset(granted_codes)


def get_current_user_service(
    request: Request,
    user_query_service: UserQueryServiceDep,
    role_query_service: RoleQueryServiceDep,
) -> CurrentUserService:
    return CurrentUserService(request, user_query_service, role_query_service)


CurrentUserServiceDep = Annotated[CurrentUserService, Depends(get_current_user_service)]
