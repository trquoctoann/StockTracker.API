from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.company_shareholder.application.query.company_shareholder_query import (
    CompanyShareholderFilterField,
    CompanyShareholderFilterParameter,
)
from app.modules.company_shareholder.domain.company_shareholder_entity import CompanyShareholderEntity
from app.modules.company_shareholder.domain.company_shareholder_repository import CompanyShareholderRepository
from app.modules.company_shareholder.infrastructure.persistence.company_shareholder_model import (
    CompanyShareholderModel,
)
from app.modules.company_shareholder.mapper.company_shareholder_mapper import CompanyShareholderMapper

K = TypeVar("K")
V = TypeVar("V")


class CompanyShareholderRepositoryImpl(CompanyShareholderRepository):
    def __init__(self, session: AsyncSession, mapper: CompanyShareholderMapper | None = None) -> None:
        self._executor = SQLExecutor(CompanyShareholderModel, session)
        self._mapper = mapper or CompanyShareholderMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[CompanyShareholderEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[CompanyShareholderEntity], K],
        value_fn: Callable[[CompanyShareholderEntity], V] | None = None,
    ) -> dict[K, list[V | CompanyShareholderEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | CompanyShareholderEntity]] = defaultdict[K, list[V | CompanyShareholderEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | CompanyShareholderEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | CompanyShareholderEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[CompanyShareholderEntity],
        *,
        id_attr: str = "id",
    ) -> list[CompanyShareholderEntity]:
        models = self._mapper.to_model_list(list[CompanyShareholderEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(
        self, entities: Sequence[CompanyShareholderEntity], *, id_attr: str = "id"
    ) -> list[CompanyShareholderEntity]:
        models = self._mapper.to_model_list(list[CompanyShareholderEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)

    async def delete_by_stock_id(self, stock_id: int) -> None:
        await self._executor.bulk_delete(
            filter_param=CompanyShareholderFilterParameter(eq={CompanyShareholderFilterField.stock_id: stock_id})
        )
