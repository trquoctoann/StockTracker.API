from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.industry.domain.industry_entity import IndustryEntity
from app.modules.industry.domain.industry_repository import IndustryRepository
from app.modules.industry.infrastructure.persistence.industry_model import IndustryModel
from app.modules.industry.mapper.industry_mapper import IndustryMapper

K = TypeVar("K")
V = TypeVar("V")


class IndustryRepositoryImpl(IndustryRepository):
    def __init__(self, session: AsyncSession, mapper: IndustryMapper | None = None) -> None:
        self._executor = SQLExecutor(IndustryModel, session)
        self._mapper = mapper or IndustryMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[IndustryEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[IndustryEntity], K],
        value_fn: Callable[[IndustryEntity], V] | None = None,
    ) -> dict[K, list[V | IndustryEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | IndustryEntity]] = defaultdict[K, list[V | IndustryEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | IndustryEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | IndustryEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[IndustryEntity],
        *,
        id_attr: str = "id",
    ) -> list[IndustryEntity]:
        models = self._mapper.to_model_list(list[IndustryEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(self, entities: Sequence[IndustryEntity], *, id_attr: str = "id") -> list[IndustryEntity]:
        models = self._mapper.to_model_list(list[IndustryEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)
