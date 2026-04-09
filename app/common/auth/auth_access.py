from __future__ import annotations

from uuid import UUID

from fastapi import Request

from app.common.auth.permission_codes import permission_bitmap
from app.common.auth.principals import AuthPrincipal, ContextPrincipal, IdentityPrincipal
from app.common.cache import CacheService, CacheServiceDep
from app.common.cache_version_keys import (
    get_role_version_cache_key,
    get_user_role_version_cache_key,
    get_user_version_cache_key,
)
from app.common.enum import RoleScope
from app.exception.exception import (
    ContextTokenUnauthorizedException,
    ForbiddenException,
    UnauthorizedException,
)
from app.modules.role.application.role_query_service import RoleFetchSpec, RoleQueryService
from app.modules.role.role_query_dependency import RoleQueryServiceDep
from app.modules.user.application.user_query_service import UserFetchSpec, UserQueryService
from app.modules.user.user_query_dependency import UserQueryServiceDep

_UNAUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


def _get_auth_principal_or_none(request: Request) -> AuthPrincipal | None:
    principal = getattr(request.state, "auth_principal", None)
    if isinstance(principal, (IdentityPrincipal | ContextPrincipal)):
        return principal
    return None


def get_authenticated_principal(request: Request) -> AuthPrincipal:
    principal = _get_auth_principal_or_none(request)
    if principal is None:
        raise UnauthorizedException(headers=_UNAUTH_HEADERS)
    return principal


def _safe_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def require_context_permissions(
    *required_permission_codes: str,
    allowed_scopes: frozenset[RoleScope] | None = None,
):
    required_permissions = set(required_permission_codes)

    async def dependency(
        request: Request,
        cache: CacheServiceDep,
        user_query_service: UserQueryServiceDep,
        role_query_service: RoleQueryServiceDep,
    ) -> ContextPrincipal:
        principal = _get_auth_principal_or_none(request)
        if principal is None:
            raise UnauthorizedException(headers=_UNAUTH_HEADERS)
        if not isinstance(principal, ContextPrincipal):
            raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)

        if allowed_scopes is not None and principal.scope not in allowed_scopes:
            raise ForbiddenException()

        try:
            user_id = UUID(principal.subject)
        except ValueError as exc:
            raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS) from exc

        if required_permissions and not permission_bitmap.has_permissions(
            principal.permissions_bitmap, required_permissions
        ):
            raise ForbiddenException()

        await _validate_token_versions(principal, user_id, cache, user_query_service, role_query_service)

        return principal

    return dependency


async def _validate_token_versions(
    principal: ContextPrincipal,
    user_id: UUID,
    cache: CacheService,
    user_query_service: UserQueryService,
    role_query_service: RoleQueryService,
) -> None:
    role_ids = sorted(principal.role_versions.keys())
    cache_keys = [
        get_user_version_cache_key(str(user_id)),
        get_user_role_version_cache_key(user_id, principal.scope.value, principal.tenant_id),
        *[get_role_version_cache_key(rid) for rid in role_ids],
    ]

    cached_values = await cache.get_many(*cache_keys)

    cached_user_ver = _safe_int(cached_values[0])
    if cached_user_ver is not None and cached_user_ver != principal.user_version:
        raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)

    cached_ur_ver = _safe_int(cached_values[1])
    if cached_ur_ver is not None and cached_ur_ver != principal.user_roles_version:
        raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)

    has_cache_miss = cached_user_ver is None or cached_ur_ver is None

    for i, role_id in enumerate(role_ids):
        cached_rv = _safe_int(cached_values[2 + i])
        if cached_rv is not None and cached_rv != principal.role_versions[role_id]:
            raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)
        if cached_rv is None:
            has_cache_miss = True

    if not has_cache_miss:
        return

    await _validate_token_versions_via_db(principal, user_id, user_query_service, role_query_service)


async def _validate_token_versions_via_db(
    principal: ContextPrincipal,
    user_id: UUID,
    user_query_service: UserQueryService,
    role_query_service: RoleQueryService,
) -> None:
    user = await user_query_service.get_by_id(user_id, fetch_spec=UserFetchSpec(user_roles=True))
    if user.version != principal.user_version:
        raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)

    matched_user_role = next(
        (
            item
            for item in (user.user_roles or [])
            if item.scope == principal.scope and item.tenant_id == principal.tenant_id
        ),
        None,
    )
    if matched_user_role is None or matched_user_role.version != principal.user_roles_version:
        raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)

    roles = await role_query_service.find_all_by_ids(
        matched_user_role.role_ids, fetch_spec=RoleFetchSpec(permissions=False)
    )
    if not roles:
        raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)

    current_role_versions = {role.id: role.version for role in roles if role.id is not None}
    if len(current_role_versions) != len(roles):
        raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)
    if current_role_versions != principal.role_versions:
        raise ContextTokenUnauthorizedException(headers=_UNAUTH_HEADERS)
