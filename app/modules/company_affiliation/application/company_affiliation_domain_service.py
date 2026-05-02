from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.modules.company_affiliation.application.command.company_affiliation_command import (
    CreateCompanyAffiliationCommand,
)
from app.modules.company_affiliation.application.company_affiliation_query_service import (
    CompanyAffiliationQueryService,
)
from app.modules.company_affiliation.application.query.company_affiliation_query import (
    CompanyAffiliationFilterField,
    CompanyAffiliationFilterParameter,
)
from app.modules.company_affiliation.domain.company_affiliation_entity import CompanyAffiliationEntity
from app.modules.company_affiliation.domain.company_affiliation_repository import CompanyAffiliationRepository
from app.modules.stock.application.stock_query_service import StockQueryService

_LOG = get_logger(__name__)


class CompanyAffiliationDomainService:
    def __init__(
        self,
        session: AsyncSession,
        company_affiliation_repository: CompanyAffiliationRepository,
        query_service: CompanyAffiliationQueryService,
        stock_query_service: StockQueryService,
    ) -> None:
        self._session = session
        self._company_affiliation_repository = company_affiliation_repository
        self._query_service = query_service
        self._stock_query_service = stock_query_service

    async def sync_affiliations(
        self, stock_id: int, commands: Sequence[CreateCompanyAffiliationCommand]
    ) -> list[CompanyAffiliationEntity]:
        async with TransactionManager(self._session):
            _LOG.debug("COMPANY_AFFILIATION_SYNCING", stock_id=stock_id, count=len(commands))

            await self._stock_query_service.get_by_id(stock_id)

            existing_entities = await self._query_service.find_all(
                CompanyAffiliationFilterParameter(eq={CompanyAffiliationFilterField.stock_id: stock_id})
            )
            existing_map: dict[tuple[int, str], CompanyAffiliationEntity] = {
                (e.stock_id, e.data_source_id): e for e in existing_entities if e.data_source_id
            }

            to_create: list[CompanyAffiliationEntity] = []
            to_update: list[CompanyAffiliationEntity] = []
            for command in commands:
                command.stock_id = stock_id

                key = (stock_id, command.data_source_id) if command.data_source_id else None
                if key and key in existing_map:
                    existing_entity = existing_map.pop(key)
                    update_data = command.model_dump(exclude_unset=True)
                    for field, value in update_data.items():
                        setattr(existing_entity, field, value)
                    to_update.append(existing_entity)
                else:
                    entity = SchemaMapper.command_to_entity(command, CompanyAffiliationEntity)
                    to_create.append(entity)

            to_delete_ids = [e.id for e in existing_map.values() if e.id is not None]
            if to_delete_ids:
                await self._company_affiliation_repository.bulk_delete(
                    filter_param=CompanyAffiliationFilterParameter(
                        in_={CompanyAffiliationFilterField.id: list[int](set[int](to_delete_ids))}  # pyright: ignore[reportCallIssue]
                    )
                )

            if to_create:
                await self._company_affiliation_repository.bulk_create(to_create)

            if to_update:
                await self._company_affiliation_repository.bulk_update(to_update)

            _LOG.debug("COMPANY_AFFILIATION_SYNCED", stock_id=stock_id)
            return to_create + to_update

    async def delete_by_stock_id(self, stock_id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("COMPANY_AFFILIATION_DELETING", stock_id=stock_id)
            await self._company_affiliation_repository.delete_by_stock_id(stock_id)
            _LOG.debug("COMPANY_AFFILIATION_DELETED", stock_id=stock_id)
