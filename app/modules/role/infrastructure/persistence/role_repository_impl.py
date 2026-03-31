from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar, cast

from sqlalchemy import ColumnElement, delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.modules.role.domain.role_entity import RoleEntity, RolePermissionEntity
from app.modules.role.domain.role_repository import RolePermissionRepository, RoleRepository
from app.modules.role.infrastructure.persistence.role_model import RoleModel, RolePermissionModel
from app.modules.role.mapper.role_mapper import RoleMapper, RolePermissionMapper

K = TypeVar("K")
V = TypeVar("V")


class RoleRepositoryImpl(RoleRepository):
    def __init__(self, session: AsyncSession, mapper: RoleMapper | None = None) -> None:
        self._executor = SQLExecutor(RoleModel, session)
        self._mapper = mapper or RoleMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[RoleEntity]:
        rows = await self._executor.find_all(
            filter_param=filter_param, pagination_param=pagination_param, id_attr=id_attr
        )
        return self._mapper.to_entity_list(rows)

    async def find_all_and_group(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        key_fn: Callable[[RoleEntity], K],
        value_fn: Callable[[RoleEntity], V] | None = None,
    ) -> dict[K, list[V | RoleEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | RoleEntity]] = defaultdict[K, list[V | RoleEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | RoleEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | RoleEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[RoleEntity],
        *,
        id_attr: str = "id",
    ) -> list[RoleEntity]:
        models = self._mapper.to_model_list(list[RoleEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(self, entities: Sequence[RoleEntity], *, id_attr: str = "id") -> list[RoleEntity]:
        models = self._mapper.to_model_list(list[RoleEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)


class RolePermissionRepositoryImpl(RolePermissionRepository):
    def __init__(self, session: AsyncSession, mapper: RolePermissionMapper | None = None) -> None:
        self._session = session
        self._mapper = mapper or RolePermissionMapper()

    async def delete_by_role_id(self, role_id: int) -> None:
        await self._session.exec(
            delete(RolePermissionModel).where(cast(ColumnElement[int], RolePermissionModel.role_id) == role_id)
        )

    async def create_many_for_role(self, *, role_id: int, permission_ids: set[int]) -> None:
        if not permission_ids:
            return
        role_permissions = [RolePermissionModel(role_id=role_id, permission_id=pid) for pid in permission_ids]
        self._session.add_all(role_permissions)
        await self._session.flush()

    async def find_all_by_role_ids(self, role_ids: list[int]) -> list[RolePermissionEntity]:
        if not role_ids:
            return []

        result = await self._session.exec(
            select(RolePermissionModel).where(
                cast(ColumnElement[int], RolePermissionModel.role_id).in_(role_ids)  # type: ignore[arg-type]
            )
        )
        return self._mapper.to_entity_list(list[RolePermissionModel](result.all()))
