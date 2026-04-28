from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.common.base_service import CRUDService
from app.common.enum import RecordStatus
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.exception.exception import InternalException
from app.modules.stock.application.command.stock_command import CreateStockCommand, UpdateStockCommand
from app.modules.stock.application.stock_query_service import StockFetchSpec, StockQueryService
from app.modules.stock.domain.stock_entity import StockEntity
from app.modules.stock.domain.stock_repository import StockIndustryRepository, StockRepository

_LOG = get_logger(__name__)


class StockDomainService(CRUDService[StockEntity]):
    def __init__(
        self,
        session: AsyncSession,
        stock_repository: StockRepository,
        stock_industry_repository: StockIndustryRepository,
        query_service: StockQueryService,
    ) -> None:
        self._session = session
        self._stock_repository = stock_repository
        self._stock_industry_repository = stock_industry_repository
        self._query_service = query_service

    async def create(self, command: CreateStockCommand) -> StockEntity:
        async with TransactionManager(self._session):
            _LOG.debug("STOCK_CREATING", command=command)

            entity = SchemaMapper.command_to_entity(
                command,
                StockEntity,
                overrides={"record_status": RecordStatus.ENABLED},
            )

            created = await self._stock_repository.bulk_create([entity])
            created_stock = created[0]

            if command.industry_ids is not None:
                await self._set_stock_industries(stock_id=created_stock.id, industry_ids=command.industry_ids)

            _LOG.debug("STOCK_CREATED", entity_id=created_stock.id)
            return created_stock

    async def update(self, command: UpdateStockCommand) -> StockEntity:
        async with TransactionManager(self._session):
            _LOG.debug("STOCK_UPDATING", command=command)

            existing = await self._query_service.get_by_id(command.id, fetch_spec=StockFetchSpec(industries=True))
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

            saved = await self._stock_repository.bulk_update([updating])
            saved_stock = saved[0]

            if command.industry_ids is not None:
                current_industry_ids = {
                    industry.id for industry in (existing.industries or []) if industry.id is not None
                }
                if current_industry_ids != command.industry_ids:
                    await self._set_stock_industries(
                        stock_id=saved_stock.id,
                        industry_ids=command.industry_ids,
                        current_industry_ids=current_industry_ids,
                    )

            _LOG.debug("STOCK_UPDATED", entity_id=saved_stock.id)
            return saved_stock

    async def delete(self, id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("STOCK_DELETING", id=id)

            existing = await self._query_service.get_by_id(id)
            existing.record_status = RecordStatus.DELETED
            await self._stock_repository.bulk_update([existing])

            _LOG.debug("STOCK_DELETED", id=id)

    async def _set_stock_industries(
        self, *, stock_id: int | None, industry_ids: set[int], current_industry_ids: set[int] | None = None
    ) -> None:
        if stock_id is None:
            raise InternalException(developer_message="Stock ID is required to set industries")

        if current_industry_ids is None:
            existing_industries = await self._stock_industry_repository.find_all_by_stock_ids([stock_id])
            current_industry_ids = {x.industry_id for x in existing_industries if x.industry_id is not None}

        to_delete = current_industry_ids - industry_ids
        to_create = industry_ids - current_industry_ids

        if to_delete:
            await self._stock_industry_repository.delete_by_stock_id_and_industry_ids(
                stock_id=stock_id, industry_ids=to_delete
            )
        if to_create:
            await self._stock_industry_repository.create_many_for_stock(stock_id=stock_id, industry_ids=to_create)
