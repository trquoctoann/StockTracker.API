from __future__ import annotations

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.common.cache import CacheService
from app.common.cache_version_keys import (
    get_user_cache_key,
    get_user_role_version_cache_key,
    get_user_version_cache_key,
)
from app.common.enum import RecordStatus
from app.exception.exception import NotFoundException
from app.modules.role.application.role_query_service import RoleQueryService
from app.modules.role.domain.role_entity import RoleEntity
from app.modules.tenant.application.tenant_query_service import TenantQueryService
from app.modules.tenant.domain.tenant_entity import TenantEntity
from app.modules.user.application.query.user_query import UserFilterField, UserFilterParameter, UserPaginationParameter
from app.modules.user.domain.user_entity import UserEntity, UserRoleEntity
from app.modules.user.domain.user_repository import UserRepository, UserRoleRepository


@dataclass(frozen=True, slots=True)
class UserFetchSpec:
    user_roles: bool = False


class UserQueryService(QueryService[UserEntity, UserFetchSpec]):
    def __init__(
        self,
        user_repository: UserRepository,
        user_role_repository: UserRoleRepository,
        tenant_query_service: TenantQueryService,
        role_query_service: RoleQueryService,
        cache: CacheService,
    ) -> None:
        self._user_repository = user_repository
        self._user_role_repository = user_role_repository
        self._tenant_query_service = tenant_query_service
        self._role_query_service = role_query_service
        self._cache = cache

    async def find_by_id(self, id: uuid.UUID | int, *, fetch_spec: UserFetchSpec | None = None) -> UserEntity | None:
        cache_key = get_user_cache_key(str(id))
        entity = await self._cache.get_model(cache_key, UserEntity)

        if entity is None:
            entities = await self._user_repository.find_all(
                filter_param=UserFilterParameter(
                    eq={UserFilterField.id: id}, neq={UserFilterField.record_status: RecordStatus.DELETED}
                ),
            )
            entity = entities[0] if entities else None
            if entity is not None:
                await self._cache.set_model(cache_key, entity)
                await self._cache.set_int(get_user_version_cache_key(str(id)), entity.version)

        if entity is not None and fetch_spec:
            enriched = await self._enrich_entities([entity], fetch_spec)
            entity = enriched[0] if enriched else entity

        return entity

    async def get_by_id(self, id: uuid.UUID | int, *, fetch_spec: UserFetchSpec | None = None) -> UserEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.user.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self, filter_params: UserFilterParameter | None = None, *, fetch_spec: UserFetchSpec | None = None
    ) -> list[UserEntity]:
        merge_filter = UserFilterParameter.merge_ops(
            filter_params,
            neq={UserFilterField.record_status: RecordStatus.DELETED},
        )
        entities = await self._user_repository.find_all(filter_param=merge_filter)
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities

    async def find_page(
        self,
        filter_params: UserFilterParameter | None,
        pagination_params: UserPaginationParameter,
        *,
        fetch_spec: UserFetchSpec | None = None,
    ) -> PaginatedResponse[UserEntity]:
        merge_filter = UserFilterParameter.merge_ops(
            filter_params,
            neq={UserFilterField.record_status: RecordStatus.DELETED},
        )
        items = await self._user_repository.find_all(
            filter_param=merge_filter,
            pagination_param=pagination_params,
        )
        if fetch_spec:
            items = await self._enrich_entities(items, fetch_spec)

        total = await self._user_repository.count(filter_param=merge_filter)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0
        return PaginatedResponse[UserEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: UserFilterParameter) -> int:
        return await self._user_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: UserFilterParameter) -> bool:
        return await self._user_repository.exists(filter_param=filter_params)

    async def username_exists(self, username: str, *, exclude_id: uuid.UUID | None = None) -> bool:
        fp = (
            UserFilterParameter(
                eq={UserFilterField.username: username},
                neq={UserFilterField.id: exclude_id},
            )
            if exclude_id is not None
            else UserFilterParameter(eq={UserFilterField.username: username})
        )
        return await self._user_repository.exists(filter_param=fp)

    async def email_exists(self, email: str, *, exclude_id: uuid.UUID | None = None) -> bool:
        fp = (
            UserFilterParameter(
                eq={UserFilterField.email: email},
                neq={UserFilterField.id: exclude_id},
            )
            if exclude_id is not None
            else UserFilterParameter(eq={UserFilterField.email: email})
        )
        return await self._user_repository.exists(filter_param=fp)

    async def _enrich_entities(self, entities: list[UserEntity], fetch_spec: UserFetchSpec) -> list[UserEntity]:
        if not entities:
            return entities

        if fetch_spec.user_roles:
            user_ids = [u.id for u in entities]
            user_roles = await self._user_role_repository.find_all_by_user_ids(user_ids)

            version_mapping: dict[str, str] = {}
            for ur in user_roles:
                version_mapping[get_user_role_version_cache_key(ur.user_id, ur.scope.value, ur.tenant_id)] = str(
                    ur.version
                )
            if version_mapping:
                await self._cache.set_many(version_mapping)

            by_user: dict[uuid.UUID, list[UserRoleEntity]] = defaultdict[UUID, list[UserRoleEntity]](list)
            for user_role in user_roles:
                by_user[user_role.user_id].append(user_role)

            tenant_ids: set[int] = set()
            role_ids: set[int] = set()
            for user_role in user_roles:
                if user_role.tenant_id is not None:
                    tenant_ids.add(user_role.tenant_id)
                role_ids.update(user_role.role_ids)

            tenants = await self._tenant_query_service.find_all_by_ids(list[int](tenant_ids))
            tenant_map: dict[int, TenantEntity] = {t.id: t for t in tenants if t.id is not None}

            roles = await self._role_query_service.find_all_by_ids(list[int](role_ids))
            role_map: dict[int, RoleEntity] = {r.id: r for r in roles if r.id is not None}

            for user in entities:
                user_roles = by_user.get(user.id, [])
                for user_role in user_roles:
                    if user_role.tenant_id is not None:
                        user_role.tenant = tenant_map.get(user_role.tenant_id)
                    user_role.roles = [role_map[role_id] for role_id in user_role.role_ids if role_id in role_map]
                user.user_roles = user_roles
        return entities
