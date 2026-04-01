from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.tenant.domain.tenant_entity import TenantEntity
from app.modules.tenant.domain.tenant_repository import TenantRepository
from app.modules.tenant.infrastructure.persistence.tenant_model import TenantModel
from app.modules.tenant.mapper.tenant_mapper import TenantMapper

K = TypeVar("K")
V = TypeVar("V")


class TenantRepositoryImpl(TenantRepository):
    def __init__(self, session: AsyncSession, mapper: TenantMapper | None = None) -> None:
        self._executor = SQLExecutor(TenantModel, session)
        self._mapper = mapper or TenantMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[TenantEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[TenantEntity], K],
        value_fn: Callable[[TenantEntity], V] | None = None,
    ) -> dict[K, list[V | TenantEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | TenantEntity]] = defaultdict[K, list[V | TenantEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | TenantEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | TenantEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[TenantEntity],
        *,
        id_attr: str = "id",
    ) -> list[TenantEntity]:
        models = self._mapper.to_model_list(list[TenantEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(self, entities: Sequence[TenantEntity], *, id_attr: str = "id") -> list[TenantEntity]:
        models = self._mapper.to_model_list(list[TenantEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)
