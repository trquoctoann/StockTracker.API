from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.modules.company_shareholder.application.command.company_shareholder_command import (
    CreateCompanyShareholderCommand,
)
from app.modules.company_shareholder.application.company_shareholder_query_service import (
    CompanyShareholderQueryService,
)
from app.modules.company_shareholder.application.query.company_shareholder_query import (
    CompanyShareholderFilterField,
    CompanyShareholderFilterParameter,
)
from app.modules.company_shareholder.domain.company_shareholder_entity import CompanyShareholderEntity
from app.modules.company_shareholder.domain.company_shareholder_repository import CompanyShareholderRepository
from app.modules.stock.application.stock_query_service import StockQueryService

_LOG = get_logger(__name__)


class CompanyShareholderDomainService:
    def __init__(
        self,
        session: AsyncSession,
        company_shareholder_repository: CompanyShareholderRepository,
        stock_query_service: StockQueryService,
        query_service: CompanyShareholderQueryService,
    ) -> None:
        self._session = session
        self._company_shareholder_repository = company_shareholder_repository
        self._query_service = query_service
        self._stock_query_service = stock_query_service

    async def sync_shareholders(
        self, stock_id: int, commands: Sequence[CreateCompanyShareholderCommand]
    ) -> list[CompanyShareholderEntity]:
        async with TransactionManager(self._session):
            _LOG.debug("COMPANY_SHAREHOLDER_SYNCING", stock_id=stock_id, count=len(commands))

            await self._stock_query_service.get_by_id(stock_id)

            existing_entities = await self._query_service.find_all(
                CompanyShareholderFilterParameter(eq={CompanyShareholderFilterField.stock_id: stock_id})
            )
            existing_map: dict[tuple[int, str], CompanyShareholderEntity] = {
                (e.stock_id, e.data_source_id): e for e in existing_entities if e.data_source_id
            }

            to_create: list[CompanyShareholderEntity] = []
            to_update: list[CompanyShareholderEntity] = []
            for command in commands:
                command.stock_id = stock_id

                key = (stock_id, command.data_source_id) if command.data_source_id else None
                if key and key in existing_map:
                    existing_entity = existing_map.pop(key)
                    update_data = SchemaMapper.merge_source_into_target(
                        command,
                        existing_entity,
                        forbidden=frozenset[str]({"id", "stock_id"}),
                    )
                    to_update.append(update_data)
                else:
                    entity = SchemaMapper.command_to_entity(command, CompanyShareholderEntity)
                    to_create.append(entity)

            to_delete_ids = [e.id for e in existing_map.values() if e.id is not None]
            if to_delete_ids:
                await self._company_shareholder_repository.bulk_delete(
                    filter_param=CompanyShareholderFilterParameter(
                        in_={CompanyShareholderFilterField.id: list[int](set[int](to_delete_ids))}  # pyright: ignore[reportCallIssue]
                    )
                )

            if to_create:
                await self._company_shareholder_repository.bulk_create(to_create)

            if to_update:
                await self._company_shareholder_repository.bulk_update(to_update)

            _LOG.debug("COMPANY_SHAREHOLDER_SYNCED", stock_id=stock_id)
            return to_create + to_update

    async def delete_by_stock_id(self, stock_id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("COMPANY_SHAREHOLDER_DELETING", stock_id=stock_id)
            await self._company_shareholder_repository.delete_by_stock_id(stock_id)
            _LOG.debug("COMPANY_SHAREHOLDER_DELETED", stock_id=stock_id)
