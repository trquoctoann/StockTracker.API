from abc import abstractmethod
from collections.abc import Sequence

from app.common.base_repository import RepositoryPort
from app.modules.stock_price_history.domain.stock_price_history_entity import StockPriceHistoryEntity


class StockPriceHistoryRepository(RepositoryPort[StockPriceHistoryEntity]):
    @abstractmethod
    async def bulk_upsert(self, entities: Sequence[StockPriceHistoryEntity]) -> None:
        pass

    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass
