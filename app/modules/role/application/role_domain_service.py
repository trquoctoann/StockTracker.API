from __future__ import annotations

from typing import cast

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.common.base_service import CRUDService
from app.common.cache import CacheService
from app.common.cache_version_keys import get_role_version_cache_key
from app.common.enum import RecordStatus, RoleType
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.exception.exception import BusinessViolationException, InternalException
from app.modules.permission.application.permission_query_service import PermissionQueryService
from app.modules.permission.domain.permission_entity import PermissionEntity
from app.modules.role.application.command.role_command import (
    CreateRoleCommand,
    SetRolePermissionsCommand,
    UpdateRoleCommand,
)
from app.modules.role.application.role_query_service import RoleFetchSpec, RoleQueryService
from app.modules.role.domain.role_entity import RoleEntity
from app.modules.role.domain.role_repository import RoleRepository
from app.modules.role.infrastructure.persistence.role_repository_impl import RolePermissionRepository
from app.modules.user.application.user_domain_service import UserDomainService

_LOG = get_logger(__name__)


class RoleDomainService(CRUDService[RoleEntity]):
    def __init__(
        self,
        session: AsyncSession,
        role_repository: RoleRepository,
        role_permission_repository: RolePermissionRepository,
        query_service: RoleQueryService,
        permission_query_service: PermissionQueryService,
        user_domain_service: UserDomainService,
        cache: CacheService,
    ) -> None:
        self._session = session
        self._role_repository = role_repository
        self._role_permission_repository = role_permission_repository
        self._query_service = query_service
        self._permission_query_service = permission_query_service
        self._user_domain_service = user_domain_service
        self._cache = cache

    async def create(self, command: CreateRoleCommand) -> RoleEntity:
        async with TransactionManager(self._session):
            _LOG.debug("ROLE_CREATING", command=command)

            entity = SchemaMapper.command_to_entity(
                command,
                RoleEntity,
                overrides={
                    "type": RoleType.CUSTOM,
                    "record_status": RecordStatus.ENABLED,
                    "version": 1,
                },
            )

            created = await self._role_repository.bulk_create([entity])
            created_role = created[0]

            if command.permission_ids is not None:
                await self._set_role_permissions(role_id=created_role.id, permission_ids=command.permission_ids)

            return created_role

    async def update(self, command: UpdateRoleCommand) -> RoleEntity:
        async with TransactionManager(self._session):
            _LOG.debug("ROLE_UPDATING", command=command)

            existing = await self._query_service.get_by_id(command.id, fetch_spec=RoleFetchSpec(permissions=True))
            updating = SchemaMapper.merge_source_into_target(
                command,
                existing,
                forbidden=frozenset[str](
                    {
                        "id",
                        "type",
                        "scope",
                        "record_status",
                        "version",
                        "created_at",
                        "created_by",
                        "updated_at",
                        "updated_by",
                    }
                ),
            )

            permissions_changed = False
            if command.permission_ids is not None:
                current_permission_ids = {
                    permission.id for permission in (existing.permissions or []) if permission.id is not None
                }
                permissions_changed = current_permission_ids != command.permission_ids
            if permissions_changed:
                updating.version += 1
                await self._invalidate_role_version_cache(updating.id)

            saved = await self._role_repository.bulk_update([updating])
            saved_role = saved[0]

            if command.permission_ids is not None and permissions_changed:
                await self._set_role_permissions(role_id=saved_role.id, permission_ids=command.permission_ids)

            return saved_role

    async def delete(self, id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("ROLE_DELETING", id=id)

            existing = await self._query_service.get_by_id(id)
            existing.record_status = RecordStatus.DELETED
            existing.version += 1
            await self._role_repository.bulk_update([existing])

            await self._invalidate_role_version_cache(id)
            await self._user_domain_service.remove_soft_deleted_role_from_user_assignments(id)

            _LOG.debug("ROLE_DELETED", id=id)

    async def set_permissions(self, command: SetRolePermissionsCommand) -> RoleEntity:
        async with TransactionManager(self._session):
            _LOG.debug("ROLE_SET_PERMISSIONS", command=command)

            existing = await self._query_service.get_by_id(command.id, fetch_spec=RoleFetchSpec(permissions=True))
            current_permission_ids = {
                permission.id for permission in (existing.permissions or []) if permission.id is not None
            }
            permissions_changed = current_permission_ids != command.permission_ids
            if permissions_changed:
                existing.version += 1
                await self._role_repository.bulk_update([existing])
                await self._invalidate_role_version_cache(command.id)

            if permissions_changed:
                return await self._set_role_permissions(
                    role_id=command.id,
                    permission_ids=command.permission_ids,
                    return_enriched=True,
                )
            return existing

    async def _set_role_permissions(
        self,
        *,
        role_id: int | None,
        permission_ids: set[int],
        return_enriched: bool = False,
    ) -> RoleEntity:
        if role_id is None:
            raise InternalException(developer_message="Role ID is required to set permissions")

        if not permission_ids:
            permission_entities: list[PermissionEntity] = []
        else:
            permission_entities = await self._permission_query_service.find_all_by_ids(list(permission_ids))

        role_id_int = cast(int, role_id)
        role = await self._query_service.get_by_id(role_id_int)
        for p in permission_entities:
            if p.scope.value != role.scope.value:
                raise BusinessViolationException(
                    message_key="errors.business.role.permission_scope_mismatch",
                    params={"role_scope": str(role.scope), "permission_code": p.code},
                )

        await self._role_permission_repository.delete_by_role_id(role_id=role_id_int)
        await self._role_permission_repository.create_many_for_role(role_id=role_id_int, permission_ids=permission_ids)

        if return_enriched:
            return await self._query_service.get_by_id(role_id_int, fetch_spec=RoleFetchSpec(permissions=True))
        return await self._query_service.get_by_id(role_id_int)

    async def _invalidate_role_version_cache(self, role_id: int) -> None:
        await self._cache.delete(get_role_version_cache_key(role_id))
