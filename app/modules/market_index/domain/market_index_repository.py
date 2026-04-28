from abc import ABC, abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.market_index.domain.market_index_entity import IndexCompositionEntity, MarketIndexEntity


class MarketIndexRepository(RepositoryPort[MarketIndexEntity]):
    pass


class IndexCompositionRepository(ABC):
    @abstractmethod
    async def delete_by_market_index_id(self, market_index_id: int) -> None:
        pass

    @abstractmethod
    async def delete_by_market_index_id_and_stock_ids(self, *, market_index_id: int, stock_ids: set[int]) -> None:
        pass

    @abstractmethod
    async def create_many_for_index(self, *, market_index_id: int, stock_ids: set[int]) -> None:
        pass

    @abstractmethod
    async def find_all_by_market_index_ids(self, market_index_ids: list[int]) -> list[IndexCompositionEntity]:
        pass
