from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.common.base_service import CRUDService
from app.common.enum import RecordStatus
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.exception.exception import InternalException
from app.modules.market_index.application.command.market_index_command import (
    CreateMarketIndexCommand,
    UpdateMarketIndexCommand,
)
from app.modules.market_index.application.market_index_query_service import (
    MarketIndexFetchSpec,
    MarketIndexQueryService,
)
from app.modules.market_index.domain.market_index_entity import MarketIndexEntity
from app.modules.market_index.domain.market_index_repository import IndexCompositionRepository, MarketIndexRepository

_LOG = get_logger(__name__)


class MarketIndexDomainService(CRUDService[MarketIndexEntity]):
    def __init__(
        self,
        session: AsyncSession,
        market_index_repository: MarketIndexRepository,
        index_composition_repository: IndexCompositionRepository,
        query_service: MarketIndexQueryService,
    ) -> None:
        self._session = session
        self._market_index_repository = market_index_repository
        self._index_composition_repository = index_composition_repository
        self._query_service = query_service

    async def create(self, command: CreateMarketIndexCommand) -> MarketIndexEntity:
        async with TransactionManager(self._session):
            _LOG.debug("MARKET_INDEX_CREATING", command=command)

            entity = SchemaMapper.command_to_entity(
                command,
                MarketIndexEntity,
                overrides={"record_status": RecordStatus.ENABLED},
            )

            created = await self._market_index_repository.bulk_create([entity])
            created_index = created[0]

            if command.stock_ids is not None:
                await self._set_index_stocks(market_index_id=created_index.id, stock_ids=command.stock_ids)

            _LOG.debug("MARKET_INDEX_CREATED", entity_id=created_index.id)
            return created_index

    async def update(self, command: UpdateMarketIndexCommand) -> MarketIndexEntity:
        async with TransactionManager(self._session):
            _LOG.debug("MARKET_INDEX_UPDATING", command=command)

            existing = await self._query_service.get_by_id(command.id, fetch_spec=MarketIndexFetchSpec(stocks=True))
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

            saved = await self._market_index_repository.bulk_update([updating])
            saved_index = saved[0]

            if command.stock_ids is not None:
                current_stock_ids = {stock.id for stock in (existing.stocks or []) if stock.id is not None}
                if current_stock_ids != command.stock_ids:
                    await self._set_index_stocks(
                        market_index_id=saved_index.id,
                        stock_ids=command.stock_ids,
                        current_stock_ids=current_stock_ids,
                    )

            _LOG.debug("MARKET_INDEX_UPDATED", entity_id=saved_index.id)
            return saved_index

    async def delete(self, id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("MARKET_INDEX_DELETING", id=id)

            existing = await self._query_service.get_by_id(id)
            existing.record_status = RecordStatus.DELETED
            await self._market_index_repository.bulk_update([existing])

            _LOG.debug("MARKET_INDEX_DELETED", id=id)

    async def _set_index_stocks(
        self, *, market_index_id: int | None, stock_ids: set[int], current_stock_ids: set[int] | None = None
    ) -> None:
        if market_index_id is None:
            raise InternalException(developer_message="Market Index ID is required to set stocks")

        if current_stock_ids is None:
            existing_compositions = await self._index_composition_repository.find_all_by_market_index_ids(
                [market_index_id]
            )
            current_stock_ids = {x.stock_id for x in existing_compositions if x.stock_id is not None}

        to_delete = current_stock_ids - stock_ids
        to_create = stock_ids - current_stock_ids

        if to_delete:
            await self._index_composition_repository.delete_by_market_index_id_and_stock_ids(
                market_index_id=market_index_id, stock_ids=to_delete
            )
        if to_create:
            await self._index_composition_repository.create_many_for_index(
                market_index_id=market_index_id, stock_ids=to_create
            )
