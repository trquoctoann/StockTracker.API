from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.common.base_service import CRUDService
from app.common.enum import RecordStatus
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.modules.industry.application.command.industry_command import CreateIndustryCommand, UpdateIndustryCommand
from app.modules.industry.application.industry_query_service import IndustryQueryService
from app.modules.industry.domain.industry_entity import IndustryEntity
from app.modules.industry.domain.industry_repository import IndustryRepository

_LOG = get_logger(__name__)


class IndustryDomainService(CRUDService[IndustryEntity]):
    def __init__(
        self,
        session: AsyncSession,
        industry_repository: IndustryRepository,
        query_service: IndustryQueryService,
    ) -> None:
        self._session = session
        self._industry_repository = industry_repository
        self._query_service = query_service

    async def create(self, command: CreateIndustryCommand) -> IndustryEntity:
        async with TransactionManager(self._session):
            _LOG.debug("INDUSTRY_CREATING", command=command)

            entity = SchemaMapper.command_to_entity(
                command,
                IndustryEntity,
                overrides={"record_status": RecordStatus.ENABLED},
            )

            created = await self._industry_repository.bulk_create([entity])
            created_entity = created[0]

            _LOG.debug("INDUSTRY_CREATED", entity_id=created_entity.id)
            return created_entity

    async def update(self, command: UpdateIndustryCommand) -> IndustryEntity:
        async with TransactionManager(self._session):
            _LOG.debug("INDUSTRY_UPDATING", command=command)

            existing = await self._query_service.get_by_id(command.id)
            updating = SchemaMapper.merge_source_into_target(
                command,
                existing,
                forbidden=frozenset[str](
                    {
                        "id",
                        "record_status",
                        "created_at",
                        "created_by",
                        "updated_at",
                        "updated_by",
                    }
                ),
            )

            saved = await self._industry_repository.bulk_update([updating])
            saved_entity = saved[0]

            _LOG.debug("INDUSTRY_UPDATED", entity_id=saved_entity.id)
            return saved_entity

    async def delete(self, id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("INDUSTRY_DELETING", id=id)

            existing = await self._query_service.get_by_id(id)
            existing.record_status = RecordStatus.DELETED
            await self._industry_repository.bulk_update([existing])

            _LOG.debug("INDUSTRY_DELETED", id=id)
