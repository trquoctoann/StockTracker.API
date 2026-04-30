from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.modules.company_profile.application.command.company_profile_command import UpsertCompanyProfileCommand
from app.modules.company_profile.application.company_profile_query_service import CompanyProfileQueryService
from app.modules.company_profile.domain.company_profile_entity import CompanyProfileEntity
from app.modules.company_profile.domain.company_profile_repository import CompanyProfileRepository
from app.modules.stock.application.stock_query_service import StockQueryService

_LOG = get_logger(__name__)


class CompanyProfileDomainService:
    def __init__(
        self,
        session: AsyncSession,
        company_profile_repository: CompanyProfileRepository,
        query_service: CompanyProfileQueryService,
        stock_query_service: StockQueryService,
    ) -> None:
        self._session = session
        self._company_profile_repository = company_profile_repository
        self._query_service = query_service
        self._stock_query_service = stock_query_service

    async def upsert(self, command: UpsertCompanyProfileCommand) -> CompanyProfileEntity:
        async with TransactionManager(self._session):
            _LOG.debug("COMPANY_PROFILE_UPSERTING", stock_id=command.stock_id)

            await self._stock_query_service.get_by_id(command.stock_id)

            existing = await self._query_service.find_by_stock_id(command.stock_id)

            if existing:
                _LOG.debug("COMPANY_PROFILE_UPDATING", id=existing.id)
                updating = SchemaMapper.merge_source_into_target(
                    command,
                    existing,
                    forbidden=frozenset[str]({"id"}),
                )
                saved = await self._company_profile_repository.bulk_update([updating])
                saved_entity = saved[0]
            else:
                _LOG.debug("COMPANY_PROFILE_CREATING")
                entity = SchemaMapper.command_to_entity(command, CompanyProfileEntity)
                created = await self._company_profile_repository.bulk_create([entity])
                saved_entity = created[0]

            _LOG.debug("COMPANY_PROFILE_UPSERTED", entity_id=saved_entity.id)
            return saved_entity

    async def delete_by_stock_id(self, stock_id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("COMPANY_PROFILE_DELETING", stock_id=stock_id)
            await self._company_profile_repository.delete_by_stock_id(stock_id)
            _LOG.debug("COMPANY_PROFILE_DELETED", stock_id=stock_id)
