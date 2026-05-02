from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.company_event.application.query.company_event_query import (
    CompanyEventFilterField,
    CompanyEventFilterParameter,
)
from app.modules.company_event.domain.company_event_entity import CompanyEventEntity
from app.modules.company_event.domain.company_event_repository import CompanyEventRepository
from app.modules.company_event.infrastructure.persistence.company_event_model import CompanyEventModel
from app.modules.company_event.mapper.company_event_mapper import CompanyEventMapper

K = TypeVar("K")
V = TypeVar("V")


class CompanyEventRepositoryImpl(CompanyEventRepository):
    def __init__(self, session: AsyncSession, mapper: CompanyEventMapper | None = None) -> None:
        self._executor = SQLExecutor(CompanyEventModel, session)
        self._mapper = mapper or CompanyEventMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[CompanyEventEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[CompanyEventEntity], K],
        value_fn: Callable[[CompanyEventEntity], V] | None = None,
    ) -> dict[K, list[V | CompanyEventEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | CompanyEventEntity]] = defaultdict[K, list[V | CompanyEventEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | CompanyEventEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | CompanyEventEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[CompanyEventEntity],
        *,
        id_attr: str = "id",
    ) -> list[CompanyEventEntity]:
        models = self._mapper.to_model_list(list[CompanyEventEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[CompanyEventEntity], *, id_attr: str = "id"
    ) -> list[CompanyEventEntity]:
        models = self._mapper.to_model_list(list[CompanyEventEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._executor.bulk_delete(
            filter_param=CompanyEventFilterParameter(eq={CompanyEventFilterField.stock_id: stock_id})
        )
