from __future__ import annotations

from uuid import UUID

from fastapi import Request

from app.common.auth.permission_codes import permission_bitmap
from app.common.auth.principals import AuthPrincipal, ContextPrincipal, IdentityPrincipal
from app.exception.exception import (
    ContextTokenUnauthorizedException,
    ForbiddenException,
    UnauthorizedException,
)
from app.modules.role.application.role_query_service import RoleFetchSpec
from app.modules.role.role_dependency import RoleQueryServiceDep
from app.modules.user.application.user_query_service import UserFetchSpec
from app.modules.user.user_dependency import UserQueryServiceDep


def _get_auth_principal_or_none(request: Request) -> AuthPrincipal | None:
    principal = getattr(request.state, "auth_principal", None)
    if isinstance(principal, (IdentityPrincipal | ContextPrincipal)):
        return principal
    return None


def get_authenticated_principal(request: Request) -> AuthPrincipal:
    principal = _get_auth_principal_or_none(request)
    if principal is None:
        raise UnauthorizedException(headers={"WWW-Authenticate": "Bearer"})
    return principal


def require_context_permissions(*required_permission_codes: str):
    required_permissions = set(required_permission_codes)

    async def dependency(
        request: Request,
        user_query_service: UserQueryServiceDep,
        role_query_service: RoleQueryServiceDep,
    ) -> ContextPrincipal:
        principal = _get_auth_principal_or_none(request)
        if principal is None:
            raise UnauthorizedException(headers={"WWW-Authenticate": "Bearer"})
        if not isinstance(principal, ContextPrincipal):
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"})

        try:
            user_id = UUID(principal.subject)
        except ValueError as exc:
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"}) from exc

        user = await user_query_service.get_by_id(user_id, fetch_spec=UserFetchSpec(user_roles=True))
        if user.version != principal.user_version:
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"})

        matched_user_role = next(
            (
                item
                for item in (user.user_roles or [])
                if item.scope == principal.scope and item.tenant_id == principal.tenant_id
            ),
            None,
        )
        if matched_user_role is None or matched_user_role.version != principal.user_roles_version:
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"})

        roles = await role_query_service.find_all_by_ids(
            matched_user_role.role_ids, fetch_spec=RoleFetchSpec(permissions=False)
        )
        if not roles:
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"})

        current_role_versions = {role.id: role.version for role in roles if role.id is not None}
        if len(current_role_versions) != len(roles):
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"})
        if current_role_versions != principal.role_versions:
            raise ContextTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"})

        if required_permissions and not permission_bitmap.has_permissions(
            principal.permissions_bitmap, required_permissions
        ):
            raise ForbiddenException()

        return principal

    return dependency
