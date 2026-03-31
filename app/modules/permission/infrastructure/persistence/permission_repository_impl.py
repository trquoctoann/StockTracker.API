from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.permission.domain.permission_entity import PermissionEntity
from app.modules.permission.domain.permission_repository import PermissionRepository
from app.modules.permission.infrastructure.persistence.permission_model import PermissionModel
from app.modules.permission.mapper.permission_mapper import PermissionMapper

K = TypeVar("K")
V = TypeVar("V")


class PermissionRepositoryImpl(PermissionRepository):
    def __init__(self, session: AsyncSession, mapper: PermissionMapper | None = None) -> None:
        self._executor = SQLExecutor(PermissionModel, session)
        self._mapper = mapper or PermissionMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[PermissionEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param,
            pagination_param=pagination_param,
            id_attr=id_attr,
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[PermissionEntity], K],
        value_fn: Callable[[PermissionEntity], V] | None = None,
    ) -> dict[K, list[V | PermissionEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | PermissionEntity]] = defaultdict[K, list[V | PermissionEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | PermissionEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | PermissionEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[PermissionEntity],
        *,
        id_attr: str = "id",
    ) -> list[PermissionEntity]:
        models = self._mapper.to_model_list(list[PermissionEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(self, entities: Sequence[PermissionEntity], *, id_attr: str = "id") -> list[PermissionEntity]:
        models = self._mapper.to_model_list(list[PermissionEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)
