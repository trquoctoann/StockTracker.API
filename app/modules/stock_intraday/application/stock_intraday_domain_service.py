from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.common.cache import CacheService
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.modules.stock.application.stock_query_service import StockQueryService
from app.modules.stock_intraday.application.command.stock_intraday_command import UpsertStockIntradayCommand
from app.modules.stock_intraday.domain.stock_intraday_entity import StockIntradayEntity
from app.modules.stock_intraday.domain.stock_intraday_repository import StockIntradayRepository

_LOG = get_logger(__name__)


class StockIntradayDomainService:
    def __init__(
        self,
        session: AsyncSession,
        stock_intraday_repository: StockIntradayRepository,
        stock_query_service: StockQueryService,
        cache_service: CacheService,
    ) -> None:
        self._session = session
        self._repository = stock_intraday_repository
        self._stock_query_service = stock_query_service
        self._cache = cache_service

    async def sync_intraday(
        self,
        stock_id: int,
        commands: Sequence[UpsertStockIntradayCommand],
    ) -> int:
        async with TransactionManager(self._session):
            _LOG.debug("STOCK_INTRADAY_SYNCING", stock_id=stock_id, count=len(commands))

            await self._stock_query_service.get_by_id(stock_id)

            entities: list[StockIntradayEntity] = []
            for cmd in commands:
                cmd.stock_id = stock_id
                entity = SchemaMapper.command_to_entity(cmd, StockIntradayEntity)
                entities.append(entity)

            if entities:
                await self._repository.bulk_upsert(entities)

            _LOG.debug("STOCK_INTRADAY_SYNCED", stock_id=stock_id, count=len(entities))

        return len(entities)

    async def delete_by_stock_id(self, stock_id: int) -> None:
        async with TransactionManager(self._session):
            _LOG.debug("STOCK_INTRADAY_DELETING", stock_id=stock_id)
            await self._repository.delete_by_stock_id(stock_id)
            _LOG.debug("STOCK_INTRADAY_DELETED", stock_id=stock_id)
