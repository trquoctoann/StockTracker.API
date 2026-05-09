from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.stock_price_history.application.query.stock_price_history_query import (
    StockPriceHistoryFilterField,
    StockPriceHistoryFilterParameter,
)
from app.modules.stock_price_history.domain.stock_price_history_entity import StockPriceHistoryEntity
from app.modules.stock_price_history.domain.stock_price_history_repository import StockPriceHistoryRepository
from app.modules.stock_price_history.infrastructure.persistence.stock_price_history_model import (
    StockPriceHistoryModel,
)
from app.modules.stock_price_history.mapper.stock_price_history_mapper import StockPriceHistoryMapper

K = TypeVar("K")
V = TypeVar("V")

_UPSERT_CONSTRAINT = "uix_stock_price_history_stock_time_interval"
_UPSERT_UPDATE_COLS = ["open", "high", "low", "close", "volume"]


class StockPriceHistoryRepositoryImpl(StockPriceHistoryRepository):
    def __init__(self, session: AsyncSession, mapper: StockPriceHistoryMapper | None = None) -> None:
        self._executor = SQLExecutor(StockPriceHistoryModel, session)
        self._mapper = mapper or StockPriceHistoryMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[StockPriceHistoryEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[StockPriceHistoryEntity], K],
        value_fn: Callable[[StockPriceHistoryEntity], V] | None = None,
    ) -> dict[K, list[V | StockPriceHistoryEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | StockPriceHistoryEntity]] = defaultdict(list)
        for entity in entities:
            key = key_fn(entity)
            value: V | StockPriceHistoryEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict(out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[StockPriceHistoryEntity],
        *,
        id_attr: str = "id",
    ) -> list[StockPriceHistoryEntity]:
        models = self._mapper.to_model_list(list(entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[StockPriceHistoryEntity], *, id_attr: str = "id"
    ) -> list[StockPriceHistoryEntity]:
        models = self._mapper.to_model_list(list(entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)

    async def bulk_upsert(self, entities: Sequence[StockPriceHistoryEntity]) -> None:
        models = self._mapper.to_model_list(list(entities))
        await self._executor.bulk_upsert(
            models,
            constraint_name=_UPSERT_CONSTRAINT,
            update_columns=_UPSERT_UPDATE_COLS,
        )

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._executor.bulk_delete(
            filter_param=StockPriceHistoryFilterParameter(eq={StockPriceHistoryFilterField.stock_id: stock_id})
        )
