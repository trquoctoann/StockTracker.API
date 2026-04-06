from __future__ import annotations

from uuid import UUID

from app.common.auth.auth_access import permission_bitmap
from app.common.auth.context_token_codec import ContextTokenCodec, ContextTokenPayload
from app.common.enum import RoleScope
from app.exception.exception import BusinessViolationException, ForbiddenException
from app.modules.role.application.role_query_service import RoleFetchSpec, RoleQueryService
from app.modules.user.application.user_domain_service import UserDomainService
from app.modules.user.application.user_query_service import UserFetchSpec, UserQueryService
from app.modules.user.domain.user_entity import UserEntity


class AccountDomainService:
    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_query_service: UserQueryService,
        role_query_service: RoleQueryService,
        context_token_codec: ContextTokenCodec,
    ) -> None:
        self._user_domain_service = user_domain_service
        self._user_query_service = user_query_service
        self._role_query_service = role_query_service
        self._context_token_codec = context_token_codec

    async def update_profile(
        self,
        current_user: UserEntity,
        *,
        first_name: str,
        last_name: str | None,
    ) -> UserEntity:
        return await self._user_domain_service.update_profile(
            current_user.id,
            first_name=first_name,
            last_name=last_name,
        )

    async def update_password(self, current_user: UserEntity, *, new_password: str) -> None:
        await self._user_domain_service.update_password(current_user.id, new_password=new_password)

    async def switch_context(
        self,
        *,
        user_id: UUID,
        scope: RoleScope,
        tenant_id: int | None,
    ) -> tuple[str, int]:
        if scope == RoleScope.TENANT and tenant_id is None:
            raise BusinessViolationException(message_key="errors.business.account.scope_tenant_tenant_id_required")
        if scope == RoleScope.ADMIN and tenant_id is not None:
            raise BusinessViolationException(message_key="errors.business.account.scope_admin_tenant_id_not_allowed")

        user = await self._user_query_service.get_by_id(user_id, fetch_spec=UserFetchSpec(user_roles=True))
        matched_user_role = next(
            (item for item in (user.user_roles or []) if item.scope == scope and item.tenant_id == tenant_id),
            None,
        )
        if matched_user_role is None:
            raise ForbiddenException()

        roles = await self._role_query_service.find_all_by_ids(
            matched_user_role.role_ids, fetch_spec=RoleFetchSpec(permissions=True)
        )
        if not roles:
            raise ForbiddenException()

        permission_codes = {permission.code for role in roles for permission in (role.permissions or [])}
        permissions_bitmap = permission_bitmap.to_bitmap(permission_codes)
        role_versions = {role.id: role.version for role in roles if role.id is not None}
        if len(role_versions) != len(roles):
            raise ForbiddenException()

        access_token, expires_in = self._context_token_codec.encode(
            ContextTokenPayload(
                subject=str(user.id),
                scope=scope,
                tenant_id=tenant_id,
                user_version=user.version,
                user_roles_version=matched_user_role.version,
                role_versions=role_versions,
                permissions_bitmap=permissions_bitmap,
            )
        )
        return access_token, expires_in
