from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.company_profile.application.query.company_profile_query import (
    CompanyProfileFilterField,
    CompanyProfileFilterParameter,
)
from app.modules.company_profile.domain.company_profile_entity import CompanyProfileEntity
from app.modules.company_profile.domain.company_profile_repository import CompanyProfileRepository
from app.modules.company_profile.infrastructure.persistence.company_profile_model import CompanyProfileModel
from app.modules.company_profile.mapper.company_profile_mapper import CompanyProfileMapper

K = TypeVar("K")
V = TypeVar("V")


class CompanyProfileRepositoryImpl(CompanyProfileRepository):
    def __init__(self, session: AsyncSession, mapper: CompanyProfileMapper | None = None) -> None:
        self._executor = SQLExecutor(CompanyProfileModel, session)
        self._mapper = mapper or CompanyProfileMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[CompanyProfileEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[CompanyProfileEntity], K],
        value_fn: Callable[[CompanyProfileEntity], V] | None = None,
    ) -> dict[K, list[V | CompanyProfileEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | CompanyProfileEntity]] = defaultdict[K, list[V | CompanyProfileEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | CompanyProfileEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | CompanyProfileEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[CompanyProfileEntity],
        *,
        id_attr: str = "id",
    ) -> list[CompanyProfileEntity]:
        models = self._mapper.to_model_list(list[CompanyProfileEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[CompanyProfileEntity], *, id_attr: str = "id"
    ) -> list[CompanyProfileEntity]:
        models = self._mapper.to_model_list(list[CompanyProfileEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._executor.bulk_delete(
            filter_param=CompanyProfileFilterParameter(eq={CompanyProfileFilterField.stock_id: stock_id})
        )
