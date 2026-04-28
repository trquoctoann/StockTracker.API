from abc import ABC, abstractmethod

from app.common.base_repository import RepositoryPort
from app.modules.stock.domain.stock_entity import StockEntity, StockIndustryEntity


class StockRepository(RepositoryPort[StockEntity]):
    pass


class StockIndustryRepository(ABC):
    @abstractmethod
    async def delete_by_stock_id(self, stock_id: int) -> None:
        pass

    @abstractmethod
    async def delete_by_stock_id_and_industry_ids(self, *, stock_id: int, industry_ids: set[int]) -> None:
        pass

    @abstractmethod
    async def create_many_for_stock(self, *, stock_id: int, industry_ids: set[int]) -> None:
        pass

    @abstractmethod
    async def find_all_by_stock_ids(self, stock_ids: list[int]) -> list[StockIndustryEntity]:
        pass
