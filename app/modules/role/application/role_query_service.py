from __future__ import annotations

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.common.enum import RecordStatus
from app.exception.exception import NotFoundException
from app.modules.permission.application.permission_query_service import PermissionQueryService
from app.modules.permission.domain.permission_entity import PermissionEntity
from app.modules.role.application.query.role_query import RoleFilterField, RoleFilterParameter, RolePaginationParameter
from app.modules.role.domain.role_entity import RoleEntity
from app.modules.role.domain.role_repository import RoleRepository
from app.modules.role.infrastructure.persistence.role_repository_impl import RolePermissionRepository


@dataclass(frozen=True, slots=True)
class RoleFetchSpec:
    permissions: bool = False


class RoleQueryService(QueryService[RoleEntity, RoleFetchSpec]):
    def __init__(
        self,
        role_repository: RoleRepository,
        role_permission_repository: RolePermissionRepository,
        permission_query_service: PermissionQueryService,
    ) -> None:
        self._role_repository = role_repository
        self._role_permission_repository = role_permission_repository
        self._permission_query_service = permission_query_service

    async def find_by_id(self, id: uuid.UUID | int, *, fetch_spec: RoleFetchSpec | None = None) -> RoleEntity | None:
        entities = await self._role_repository.find_all(
            filter_param=RoleFilterParameter(
                eq={RoleFilterField.id: id}, neq={RoleFilterField.record_status: RecordStatus.DELETED}
            ),
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities[0] if entities else None

    async def get_by_id(self, id: uuid.UUID | int, *, fetch_spec: RoleFetchSpec | None = None) -> RoleEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.role.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self, filter_params: RoleFilterParameter | None = None, *, fetch_spec: RoleFetchSpec | None = None
    ) -> list[RoleEntity]:
        merge_filter = RoleFilterParameter.merge_ops(
            filter_params,
            neq={RoleFilterField.record_status: RecordStatus.DELETED},
        )
        entities = await self._role_repository.find_all(filter_param=merge_filter)
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities

    async def find_page(
        self,
        filter_params: RoleFilterParameter | None,
        pagination_params: RolePaginationParameter,
        *,
        fetch_spec: RoleFetchSpec | None = None,
    ) -> PaginatedResponse[RoleEntity]:
        merge_filter = RoleFilterParameter.merge_ops(
            filter_params,
            neq={RoleFilterField.record_status: RecordStatus.DELETED},
        )
        items = await self._role_repository.find_all(filter_param=merge_filter, pagination_param=pagination_params)
        if fetch_spec:
            items = await self._enrich_entities(items, fetch_spec)

        total = await self._role_repository.count(filter_param=merge_filter)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[RoleEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: RoleFilterParameter) -> int:
        return await self._role_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: RoleFilterParameter) -> bool:
        return await self._role_repository.exists(filter_param=filter_params)

    async def _enrich_entities(self, entities: list[RoleEntity], fetch_spec: RoleFetchSpec) -> list[RoleEntity]:
        if not entities:
            return entities

        if fetch_spec.permissions:
            role_ids = [e.id for e in entities if e.id is not None]
            if not role_ids:
                return entities

            role_permissions = await self._role_permission_repository.find_all_by_role_ids(role_ids)

            role_permission_map: dict[int, list[int]] = defaultdict(list)
            permission_ids: set[int] = set()
            for role_permission in role_permissions:
                role_permission_map[role_permission.role_id].append(role_permission.permission_id)
                permission_ids.add(role_permission.permission_id)

            permission_map: dict[int, PermissionEntity] = {}
            if permission_ids:
                permissions = await self._permission_query_service.find_all_by_ids(list(permission_ids))
                permission_map = {p.id: p for p in permissions if p.id is not None}

            for role in entities:
                if role.id is None:
                    continue
                role_permission_ids_for_role = role_permission_map.get(role.id, [])
                role.permissions = [
                    permission_map[pid] for pid in role_permission_ids_for_role if pid in permission_map
                ]
        return entities

    async def find_all_by_ids(self, ids: list[int], *, fetch_spec: RoleFetchSpec | None = None) -> list[RoleEntity]:
        entities = await self._role_repository.find_all(
            filter_param=RoleFilterParameter(in_={RoleFilterField.id: list[int](set[int](ids))})  # pyright: ignore[reportCallIssue]
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities
