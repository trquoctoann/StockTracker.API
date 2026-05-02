from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.company_officer.application.query.company_officer_query import (
    CompanyOfficerFilterField,
    CompanyOfficerFilterParameter,
)
from app.modules.company_officer.domain.company_officer_entity import CompanyOfficerEntity
from app.modules.company_officer.domain.company_officer_repository import CompanyOfficerRepository
from app.modules.company_officer.infrastructure.persistence.company_officer_model import CompanyOfficerModel
from app.modules.company_officer.mapper.company_officer_mapper import CompanyOfficerMapper

K = TypeVar("K")
V = TypeVar("V")


class CompanyOfficerRepositoryImpl(CompanyOfficerRepository):
    def __init__(self, session: AsyncSession, mapper: CompanyOfficerMapper | None = None) -> None:
        self._executor = SQLExecutor(CompanyOfficerModel, session)
        self._mapper = mapper or CompanyOfficerMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[CompanyOfficerEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[CompanyOfficerEntity], K],
        value_fn: Callable[[CompanyOfficerEntity], V] | None = None,
    ) -> dict[K, list[V | CompanyOfficerEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | CompanyOfficerEntity]] = defaultdict[K, list[V | CompanyOfficerEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | CompanyOfficerEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | CompanyOfficerEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[CompanyOfficerEntity],
        *,
        id_attr: str = "id",
    ) -> list[CompanyOfficerEntity]:
        models = self._mapper.to_model_list(list[CompanyOfficerEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[CompanyOfficerEntity], *, id_attr: str = "id"
    ) -> list[CompanyOfficerEntity]:
        models = self._mapper.to_model_list(list[CompanyOfficerEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._executor.bulk_delete(
            filter_param=CompanyOfficerFilterParameter(eq={CompanyOfficerFilterField.stock_id: stock_id})
        )
