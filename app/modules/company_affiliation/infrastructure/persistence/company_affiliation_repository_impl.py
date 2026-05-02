from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.company_affiliation.application.query.company_affiliation_query import (
    CompanyAffiliationFilterField,
    CompanyAffiliationFilterParameter,
)
from app.modules.company_affiliation.domain.company_affiliation_entity import CompanyAffiliationEntity
from app.modules.company_affiliation.domain.company_affiliation_repository import CompanyAffiliationRepository
from app.modules.company_affiliation.infrastructure.persistence.company_affiliation_model import (
    CompanyAffiliationModel,
)
from app.modules.company_affiliation.mapper.company_affiliation_mapper import CompanyAffiliationMapper

K = TypeVar("K")
V = TypeVar("V")


class CompanyAffiliationRepositoryImpl(CompanyAffiliationRepository):
    def __init__(self, session: AsyncSession, mapper: CompanyAffiliationMapper | None = None) -> None:
        self._executor = SQLExecutor(CompanyAffiliationModel, session)
        self._mapper = mapper or CompanyAffiliationMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[CompanyAffiliationEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[CompanyAffiliationEntity], K],
        value_fn: Callable[[CompanyAffiliationEntity], V] | None = None,
    ) -> dict[K, list[V | CompanyAffiliationEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | CompanyAffiliationEntity]] = defaultdict[K, list[V | CompanyAffiliationEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | CompanyAffiliationEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | CompanyAffiliationEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[CompanyAffiliationEntity],
        *,
        id_attr: str = "id",
    ) -> list[CompanyAffiliationEntity]:
        models = self._mapper.to_model_list(list[CompanyAffiliationEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[CompanyAffiliationEntity], *, id_attr: str = "id"
    ) -> list[CompanyAffiliationEntity]:
        models = self._mapper.to_model_list(list[CompanyAffiliationEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._executor.bulk_delete(
            filter_param=CompanyAffiliationFilterParameter(eq={CompanyAffiliationFilterField.stock_id: stock_id})
        )
