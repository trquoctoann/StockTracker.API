from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.stock_intraday.application.query.stock_intraday_query import (
    StockIntradayFilterField,
    StockIntradayFilterParameter,
)
from app.modules.stock_intraday.domain.stock_intraday_entity import StockIntradayEntity
from app.modules.stock_intraday.domain.stock_intraday_repository import StockIntradayRepository
from app.modules.stock_intraday.infrastructure.persistence.stock_intraday_model import StockIntradayModel
from app.modules.stock_intraday.mapper.stock_intraday_mapper import StockIntradayMapper

K = TypeVar("K")
V = TypeVar("V")

_UPSERT_CONSTRAINT = "uix_stock_intraday_stock_time_source"
_UPSERT_UPDATE_COLS = ["price", "volume", "match_type"]


class StockIntradayRepositoryImpl(StockIntradayRepository):
    def __init__(self, session: AsyncSession, mapper: StockIntradayMapper | None = None) -> None:
        self._executor = SQLExecutor(StockIntradayModel, session)
        self._mapper = mapper or StockIntradayMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[StockIntradayEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[StockIntradayEntity], K],
        value_fn: Callable[[StockIntradayEntity], V] | None = None,
    ) -> dict[K, list[V | StockIntradayEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | StockIntradayEntity]] = defaultdict(list)
        for entity in entities:
            key = key_fn(entity)
            value: V | StockIntradayEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict(out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[StockIntradayEntity],
        *,
        id_attr: str = "id",
    ) -> list[StockIntradayEntity]:
        models = self._mapper.to_model_list(list(entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[StockIntradayEntity], *, id_attr: str = "id"
    ) -> list[StockIntradayEntity]:
        models = self._mapper.to_model_list(list(entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)

    async def bulk_upsert(self, entities: Sequence[StockIntradayEntity]) -> None:
        models = self._mapper.to_model_list(list(entities))
        await self._executor.bulk_upsert(
            models,
            constraint_name=_UPSERT_CONSTRAINT,
            update_columns=_UPSERT_UPDATE_COLS,
        )

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._executor.bulk_delete(
            filter_param=StockIntradayFilterParameter(eq={StockIntradayFilterField.stock_id: stock_id})
        )
