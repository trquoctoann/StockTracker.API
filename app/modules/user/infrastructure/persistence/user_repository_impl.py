import uuid
from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import TypeVar, cast

from sqlalchemy import ColumnElement, delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_repository import SQLExecutor
from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter
from app.common.enum import RoleScope
from app.exception.exception import InternalException
from app.modules.user.domain.user_entity import UserEntity, UserRoleEntity
from app.modules.user.domain.user_repository import UserRepository, UserRoleRepository
from app.modules.user.infrastructure.persistence.user_model import UserModel, UserRoleModel
from app.modules.user.mapper.user_mapper import UserMapper, UserRoleMapper

K = TypeVar("K")
V = TypeVar("V")


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._executor = SQLExecutor(UserModel, session)
        self._mapper = UserMapper()

    async def find_all(
        self,
        *,
        filter_param: FilterQueryParameter | None = None,
        pagination_param: PaginationQueryParameter | None = None,
        id_attr: str = "id",
    ) -> list[UserEntity]:
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
        key_fn: Callable[[UserEntity], K],
        value_fn: Callable[[UserEntity], V] | None = None,
    ) -> dict[K, list[V | UserEntity]]:
        entities = await self.find_all(filter_param=filter_param)
        out: dict[K, list[V | UserEntity]] = defaultdict[K, list[V | UserEntity]](list)
        for entity in entities:
            key = key_fn(entity)
            value: V | UserEntity = entity if value_fn is None else value_fn(entity)
            out[key].append(value)
        return dict[K, list[V | UserEntity]](out)

    async def count(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> int:
        return await self._executor.count(filter_param=filter_param, id_attr=id_attr)

    async def exists(self, *, filter_param: FilterQueryParameter | None = None, id_attr: str = "id") -> bool:
        return await self._executor.exists(filter_param=filter_param, id_attr=id_attr)

    async def bulk_create(
        self,
        entities: Sequence[UserEntity],
        *,
        id_attr: str = "id",
    ) -> list[UserEntity]:
        models = self._mapper.to_model_list(list[UserEntity](entities))
        created_models = await self._executor.bulk_create(models, id_attr=id_attr)
        return self._mapper.to_entity_list(created_models)

    async def bulk_update(self, entities: Sequence[UserEntity], *, id_attr: str = "id") -> list[UserEntity]:
        models = self._mapper.to_model_list(list[UserEntity](entities))
        updated_models = await self._executor.bulk_update(models, id_attr=id_attr)
        return self._mapper.to_entity_list(updated_models)

    async def bulk_delete(self, *, filter_param: FilterQueryParameter | None = None) -> None:
        await self._executor.bulk_delete(filter_param=filter_param)


class UserRoleRepositoryImpl(UserRoleRepository):
    def __init__(self, session: AsyncSession, mapper: UserRoleMapper | None = None) -> None:
        self._session = session
        self._mapper = mapper or UserRoleMapper()

    async def find_all_by_user_ids(self, user_ids: list[uuid.UUID]) -> list[UserRoleEntity]:
        if not user_ids:
            return []
        result = await self._session.exec(
            select(UserRoleModel).where(cast(ColumnElement[uuid.UUID], UserRoleModel.user_id).in_(user_ids))  # type: ignore[arg-type]
        )
        return self._mapper.to_entity_list(list[UserRoleModel](result.all()))

    async def delete_by_user_id(self, *, user_id: uuid.UUID, scope: RoleScope, tenant_id: int | None) -> None:
        statement = delete(UserRoleModel).where(cast(ColumnElement[uuid.UUID], UserRoleModel.user_id) == user_id)
        statement = statement.where(cast(ColumnElement[RoleScope], UserRoleModel.scope) == scope)
        if tenant_id is None:
            statement = statement.where(cast(ColumnElement[int], UserRoleModel.tenant_id).is_(None))
        else:
            statement = statement.where(cast(ColumnElement[int], UserRoleModel.tenant_id) == tenant_id)
        await self._session.exec(statement)

    async def upsert_user_roles(
        self, *, user_id: uuid.UUID, scope: RoleScope, tenant_id: int | None, role_ids: set[int]
    ) -> UserRoleEntity:
        statement = select(UserRoleModel).where(cast(ColumnElement[uuid.UUID], UserRoleModel.user_id) == user_id)
        statement = statement.where(cast(ColumnElement[RoleScope], UserRoleModel.scope) == scope)
        if tenant_id is None:
            statement = statement.where(cast(ColumnElement[int], UserRoleModel.tenant_id).is_(None))
        else:
            statement = statement.where(cast(ColumnElement[int], UserRoleModel.tenant_id) == tenant_id)
        result = await self._session.exec(statement)

        existing = result.first()
        if existing:
            next_role_ids = sorted(role_ids)
            if existing.role_ids != next_role_ids:
                existing.role_ids = next_role_ids
                existing.version += 1

                self._session.add(existing)
                await self._session.flush()

            entity = self._mapper.to_entity(existing)
            if entity.id is None:
                raise InternalException(developer_message="UserRole ID must exist for updated row")
            return entity

        model = UserRoleModel(
            user_id=user_id,
            scope=scope,
            tenant_id=tenant_id,
            role_ids=sorted(role_ids),
            version=1,
        )
        self._session.add(model)
        await self._session.flush()

        entity = self._mapper.to_entity(model)
        if entity.id is None:
            raise InternalException(developer_message="UserRole ID must be generated after creating")
        return entity
