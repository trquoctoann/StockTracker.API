from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.common.base_service import CRUDService
from app.common.enum import RecordStatus
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.exception.exception import InternalException
from app.modules.tenant.application.command.tenant_command import CreateTenantCommand, UpdateTenantCommand
from app.modules.tenant.application.tenant_query_service import TenantQueryService
from app.modules.tenant.domain.tenant_entity import TenantEntity
from app.modules.tenant.domain.tenant_repository import TenantRepository
from app.modules.user.application.user_domain_service import UserDomainService

_LOG = get_logger(__name__)


class TenantDomainService(CRUDService[TenantEntity]):
    def __init__(
        self,
        session: AsyncSession,
        tenant_repository: TenantRepository,
        query_service: TenantQueryService,
        user_domain_service: UserDomainService,
    ) -> None:
        self._session = session
        self._tenant_repository = tenant_repository
        self._query_service = query_service
        self._user_domain_service = user_domain_service

    async def create(self, command: CreateTenantCommand) -> TenantEntity:
        async with TransactionManager(self._session):
            _LOG.debug("TENANT_CREATING", command=command)

            await self.validate_command(command)

            entity = SchemaMapper.command_to_entity(
                command,
                TenantEntity,
                overrides={
                    "path": "__pending__",
                    "record_status": RecordStatus.ENABLED,
                },
            )
            created = await self._tenant_repository.bulk_create([entity])
            created_tenant = created[0]

            if created_tenant.id is None:
                raise InternalException(developer_message="Tenant ID must be generated after creating")

            created_tenant.path = await self._build_tenant_path(created_tenant.id, created_tenant.parent_tenant_id)
            saved = await self._tenant_repository.bulk_update([created_tenant])
            return saved[0]

    async def update(self, command: UpdateTenantCommand) -> TenantEntity:
        async with TransactionManager(self._session):
            _LOG.debug("TENANT_UPDATING", command=command)

            existing = await self._query_service.get_by_id(command.id)

            updating = SchemaMapper.merge_source_into_target(
                command,
                existing,
                forbidden=frozenset[str](
                    {
                        "id",
                        "path",
                        "record_status",
                        "parent_tenant_id",
                        "created_at",
                        "created_by",
                        "updated_at",
                        "updated_by",
                    }
                ),
            )
            updated = await self._tenant_repository.bulk_update([updating])
            return updated[0]

    async def delete(self, id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("TENANT_DELETING", id=id)

            existing = await self._query_service.get_by_id(id)
            existing.record_status = RecordStatus.DELETED
            await self._tenant_repository.bulk_update([existing])

            await self._user_domain_service.delete_user_roles_for_soft_deleted_tenant(id)

            _LOG.debug("TENANT_DELETED", id=id)

    async def validate_command(self, command: CreateTenantCommand | UpdateTenantCommand) -> None:
        if isinstance(command, UpdateTenantCommand):
            pass
        else:
            await self._validate_create_command(command)

    async def _validate_create_command(self, command: CreateTenantCommand) -> None:
        if command.parent_tenant_id is not None:
            await self._query_service.get_by_id(command.parent_tenant_id)

    async def _build_tenant_path(self, tenant_id: int, parent_tenant_id: int | None) -> str:
        if parent_tenant_id is None:
            return str(tenant_id)

        parent_tenant = await self._query_service.get_by_id(parent_tenant_id)
        if not parent_tenant.path:
            raise InternalException(developer_message=f"Parent tenant {parent_tenant_id} has empty path")
        return f"{parent_tenant.path}{tenant_id}."
