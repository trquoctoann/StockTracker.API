from __future__ import annotations

import math
import uuid

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.exception.exception import NotFoundException
from app.modules.permission.application.query.permission_query import (
    PermissionFilterField,
    PermissionFilterParameter,
    PermissionPaginationParameter,
)
from app.modules.permission.domain.permission_entity import PermissionEntity
from app.modules.permission.domain.permission_repository import PermissionRepository


class PermissionFetchSpec:
    pass


class PermissionQueryService(QueryService[PermissionEntity, PermissionFetchSpec]):
    def __init__(self, permission_repository: PermissionRepository) -> None:
        self._permission_repository = permission_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: PermissionFetchSpec | None = None
    ) -> PermissionEntity | None:
        entities = await self._permission_repository.find_all(
            filter_param=PermissionFilterParameter(eq={PermissionFilterField.id: id}),
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: PermissionFetchSpec | None = None
    ) -> PermissionEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.permission.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self, filter_params: PermissionFilterParameter | None = None, *, fetch_spec: PermissionFetchSpec | None = None
    ) -> list[PermissionEntity]:
        entities = await self._permission_repository.find_all(filter_param=filter_params)
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities

    async def find_page(
        self,
        filter_params: PermissionFilterParameter | None,
        pagination_params: PermissionPaginationParameter,
        *,
        fetch_spec: PermissionFetchSpec | None = None,
    ) -> PaginatedResponse[PermissionEntity]:
        items = await self._permission_repository.find_all(
            filter_param=filter_params,
            pagination_param=pagination_params,
        )
        if fetch_spec:
            items = await self._enrich_entities(items, fetch_spec)

        total = await self._permission_repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0
        return PaginatedResponse[PermissionEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: PermissionFilterParameter) -> int:
        return await self._permission_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: PermissionFilterParameter) -> bool:
        return await self._permission_repository.exists(filter_param=filter_params)

    async def code_exists(self, code: str, *, exclude_id: int | None = None) -> bool:
        fp = (
            PermissionFilterParameter(
                eq={PermissionFilterField.code: code},
                neq={PermissionFilterField.id: exclude_id},
            )
            if exclude_id is not None
            else PermissionFilterParameter(eq={PermissionFilterField.code: code})
        )
        return await self._permission_repository.exists(filter_param=fp)

    async def _enrich_entities(
        self, entities: list[PermissionEntity], fetch_spec: PermissionFetchSpec
    ) -> list[PermissionEntity]:
        return entities

    async def find_all_by_ids(
        self, ids: list[int], *, fetch_spec: PermissionFetchSpec | None = None
    ) -> list[PermissionEntity]:
        entities = await self._permission_repository.find_all(
            filter_param=PermissionFilterParameter(in_={PermissionFilterField.id: list[int](set[int](ids))})  # pyright: ignore[reportCallIssue]
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities
