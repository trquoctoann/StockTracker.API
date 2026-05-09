from abc import abstractmethod
from collections.abc import Sequence

from app.common.base_repository import RepositoryPort
from app.modules.stock_intraday.domain.stock_intraday_entity import StockIntradayEntity


class StockIntradayRepository(RepositoryPort[StockIntradayEntity]):
    @abstractmethod
    async def bulk_upsert(self, entities: Sequence[StockIntradayEntity]) -> None:
        pass

    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass
