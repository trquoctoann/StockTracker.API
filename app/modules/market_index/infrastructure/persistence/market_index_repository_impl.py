from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlalchemy import delete
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.market_index.domain.market_index_entity import IndexCompositionEntity, MarketIndexEntity
from app.modules.market_index.domain.market_index_repository import IndexCompositionRepository, MarketIndexRepository
from app.modules.market_index.infrastructure.persistence.market_index_model import (
    IndexCompositionModel,
    MarketIndexModel,
)
from app.modules.market_index.mapper.market_index_mapper import IndexCompositionMapper, MarketIndexMapper

K = TypeVar("K")
V = TypeVar("V")


class MarketIndexRepositoryImpl(MarketIndexRepository):
    def __init__(self, session: AsyncSession, mapper: MarketIndexMapper | None = None) -> None:
        self._executor = SQLExecutor(MarketIndexModel, session)
        self._mapper = mapper or MarketIndexMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[MarketIndexEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[MarketIndexEntity], K],
        value_fn: Callable[[MarketIndexEntity], V] | None = None,
    ) -> dict[K, list[V | MarketIndexEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | MarketIndexEntity]] = defaultdict[K, list[V | MarketIndexEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | MarketIndexEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | MarketIndexEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[MarketIndexEntity],
        *,
        id_attr: str = "id",
    ) -> list[MarketIndexEntity]:
        models = self._mapper.to_model_list(list[MarketIndexEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[MarketIndexEntity], *, id_attr: str = "id"
    ) -> list[MarketIndexEntity]:
        models = self._mapper.to_model_list(list[MarketIndexEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)


class IndexCompositionRepositoryImpl(IndexCompositionRepository):
    def __init__(self, session: AsyncSession, mapper: IndexCompositionMapper | None = None) -> None:
        self._session = session
        self._mapper = mapper or IndexCompositionMapper()

    async def delete_by_market_index_id(self, market_index_id: int) -> None:
        await self._session.exec(
            delete(IndexCompositionModel).where(col(IndexCompositionModel.market_index_id) == market_index_id)
        )

    async def delete_by_market_index_id_and_stock_ids(self, *, market_index_id: int, stock_ids: set[int]) -> None:
        if not stock_ids:
            return
        statement = delete(IndexCompositionModel).where(
            col(IndexCompositionModel.market_index_id) == market_index_id,
            col(IndexCompositionModel.stock_id).in_(stock_ids),
        )
        await self._session.exec(statement)

    async def create_many_for_index(self, *, market_index_id: int, stock_ids: set[int]) -> None:
        if not stock_ids:
            return
        compositions = [IndexCompositionModel(market_index_id=market_index_id, stock_id=sid) for sid in stock_ids]
        self._session.add_all(compositions)
        await self._session.flush()

    async def find_all_by_market_index_ids(self, market_index_ids: list[int]) -> list[IndexCompositionEntity]:
        if not market_index_ids:
            return []
        result = await self._session.exec(
            select(IndexCompositionModel).where(col(IndexCompositionModel.market_index_id).in_(market_index_ids))
        )
        return self._mapper.to_entity_list(list[IndexCompositionModel](result.all()))
