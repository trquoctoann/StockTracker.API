from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.common.cache import CacheService
from app.common.cache_version_keys import get_price_history_bars_cache_key
from app.common.enum import PriceInterval
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.modules.stock.application.stock_query_service import StockQueryService
from app.modules.stock_price_history.application.command.stock_price_history_command import (
    UpsertStockPriceHistoryCommand,
)
from app.modules.stock_price_history.domain.stock_price_history_entity import StockPriceHistoryEntity
from app.modules.stock_price_history.domain.stock_price_history_repository import StockPriceHistoryRepository

_LOG = get_logger(__name__)


class StockPriceHistoryDomainService:
    def __init__(
        self,
        session: AsyncSession,
        stock_price_history_repository: StockPriceHistoryRepository,
        stock_query_service: StockQueryService,
        cache_service: CacheService,
    ) -> None:
        self._session = session
        self._repository = stock_price_history_repository
        self._stock_query_service = stock_query_service
        self._cache = cache_service

    async def sync_price_history(
        self,
        stock_id: int,
        interval: PriceInterval,
        commands: Sequence[UpsertStockPriceHistoryCommand],
    ) -> int:
        async with TransactionManager(self._session):
            _LOG.debug("STOCK_PRICE_HISTORY_SYNCING", stock_id=stock_id, interval=interval, count=len(commands))

            await self._stock_query_service.get_by_id(stock_id)

            entities: list[StockPriceHistoryEntity] = []
            for cmd in commands:
                cmd.stock_id = stock_id
                cmd.interval = interval

                entity = SchemaMapper.command_to_entity(cmd, StockPriceHistoryEntity)
                entities.append(entity)

            if entities:
                await self._repository.bulk_upsert(entities)

            _LOG.debug("STOCK_PRICE_HISTORY_SYNCED", stock_id=stock_id, interval=interval, count=len(entities))

        await self._cache.delete(get_price_history_bars_cache_key(stock_id, interval.value))
        return len(entities)

    async def delete_by_stock_id(self, stock_id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("STOCK_PRICE_HISTORY_DELETING", stock_id=stock_id)
            await self._repository.delete_by_stock_id(stock_id)
            _LOG.debug("STOCK_PRICE_HISTORY_DELETED", stock_id=stock_id)
