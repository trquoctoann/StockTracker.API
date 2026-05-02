from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.company_news.application.query.company_news_query import (
    CompanyNewsFilterField,
    CompanyNewsFilterParameter,
)
from app.modules.company_news.domain.company_news_entity import CompanyNewsEntity
from app.modules.company_news.domain.company_news_repository import CompanyNewsRepository
from app.modules.company_news.infrastructure.persistence.company_news_model import CompanyNewsModel
from app.modules.company_news.mapper.company_news_mapper import CompanyNewsMapper

K = TypeVar("K")
V = TypeVar("V")


class CompanyNewsRepositoryImpl(CompanyNewsRepository):
    def __init__(self, session: AsyncSession, mapper: CompanyNewsMapper | None = None) -> None:
        self._executor = SQLExecutor(CompanyNewsModel, session)
        self._mapper = mapper or CompanyNewsMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[CompanyNewsEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[CompanyNewsEntity], K],
        value_fn: Callable[[CompanyNewsEntity], V] | None = None,
    ) -> dict[K, list[V | CompanyNewsEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | CompanyNewsEntity]] = defaultdict[K, list[V | CompanyNewsEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | CompanyNewsEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | CompanyNewsEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[CompanyNewsEntity],
        *,
        id_attr: str = "id",
    ) -> list[CompanyNewsEntity]:
        models = self._mapper.to_model_list(list[CompanyNewsEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[CompanyNewsEntity], *, id_attr: str = "id"
    ) -> list[CompanyNewsEntity]:
        models = self._mapper.to_model_list(list[CompanyNewsEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._executor.bulk_delete(
            filter_param=CompanyNewsFilterParameter(eq={CompanyNewsFilterField.stock_id: stock_id})
        )
