from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlalchemy import delete
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.stock.domain.stock_entity import StockEntity, StockIndustryEntity
from app.modules.stock.domain.stock_repository import StockIndustryRepository, StockRepository
from app.modules.stock.infrastructure.persistence.stock_model import StockIndustryModel, StockModel
from app.modules.stock.mapper.stock_mapper import StockIndustryMapper, StockMapper

K = TypeVar("K")
V = TypeVar("V")


class StockRepositoryImpl(StockRepository):
    def __init__(self, session: AsyncSession, mapper: StockMapper | None = None) -> None:
        self._executor = SQLExecutor(StockModel, session)
        self._mapper = mapper or StockMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[StockEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[StockEntity], K],
        value_fn: Callable[[StockEntity], V] | None = None,
    ) -> dict[K, list[V | StockEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | StockEntity]] = defaultdict[K, list[V | StockEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | StockEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | StockEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[StockEntity],
        *,
        id_attr: str = "id",
    ) -> list[StockEntity]:
        models = self._mapper.to_model_list(list[StockEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(self, entities: Sequence[StockEntity], *, id_attr: str = "id") -> list[StockEntity]:
        models = self._mapper.to_model_list(list[StockEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)


class StockIndustryRepositoryImpl(StockIndustryRepository):
    def __init__(self, session: AsyncSession, mapper: StockIndustryMapper | None = None) -> None:
        self._session = session
        self._mapper = mapper or StockIndustryMapper()

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._session.exec(delete(StockIndustryModel).where(col(StockIndustryModel.stock_id) == stock_id))

    async def delete_by_stock_id_and_industry_ids(self, *, stock_id: int, industry_ids: set[int]) -> None:
        if not industry_ids:
            return
        statement = delete(StockIndustryModel).where(
            col(StockIndustryModel.stock_id) == stock_id, col(StockIndustryModel.industry_id).in_(industry_ids)
        )
        await self._session.exec(statement)

    async def create_many_for_stock(self, *, stock_id: int, industry_ids: set[int]) -> None:
        if not industry_ids:
            return
        stock_industries = [StockIndustryModel(stock_id=stock_id, industry_id=iid) for iid in industry_ids]
        self._session.add_all(stock_industries)
        await self._session.flush()

    async def find_all_by_stock_ids(self, stock_ids: list[int]) -> list[StockIndustryEntity]:
        if not stock_ids:
            return []
        result = await self._session.exec(
            select(StockIndustryModel).where(col(StockIndustryModel.stock_id).in_(stock_ids))
        )
        return self._mapper.to_entity_list(list[StockIndustryModel](result.all()))
