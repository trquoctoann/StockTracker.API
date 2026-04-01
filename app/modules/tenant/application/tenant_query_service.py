from __future__ import annotations

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.common.enum import RecordStatus
from app.exception.exception import NotFoundException
from app.modules.tenant.application.query.tenant_query import (
    TenantFilterField,
    TenantFilterParameter,
    TenantPaginationParameter,
)
from app.modules.tenant.domain.tenant_entity import TenantEntity
from app.modules.tenant.domain.tenant_repository import TenantRepository


@dataclass(frozen=True, slots=True)
class TenantFetchSpec:
    parent_tenant: bool = False
    children_tenants: bool = False


class TenantQueryService(QueryService[TenantEntity, TenantFetchSpec]):
    def __init__(self, tenant_repository: TenantRepository) -> None:
        self._tenant_repository = tenant_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: TenantFetchSpec | None = None
    ) -> TenantEntity | None:
        entities = await self._tenant_repository.find_all(
            filter_param=TenantFilterParameter(
                eq={TenantFilterField.id: id},
                neq={TenantFilterField.record_status: RecordStatus.DELETED},
            ),
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities[0] if entities else None

    async def get_by_id(self, id: uuid.UUID | int, *, fetch_spec: TenantFetchSpec | None = None) -> TenantEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.tenant.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self, filter_params: TenantFilterParameter | None = None, *, fetch_spec: TenantFetchSpec | None = None
    ) -> list[TenantEntity]:
        merge_filter = TenantFilterParameter.merge_ops(
            filter_params,
            neq={TenantFilterField.record_status: RecordStatus.DELETED},
        )
        entities = await self._tenant_repository.find_all(filter_param=merge_filter)
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities

    async def find_page(
        self,
        filter_params: TenantFilterParameter | None,
        pagination_params: TenantPaginationParameter,
        *,
        fetch_spec: TenantFetchSpec | None = None,
    ) -> PaginatedResponse[TenantEntity]:
        merge_filter = TenantFilterParameter.merge_ops(
            filter_params,
            neq={TenantFilterField.record_status: RecordStatus.DELETED},
        )
        items = await self._tenant_repository.find_all(
            filter_param=merge_filter,
            pagination_param=pagination_params,
        )
        if fetch_spec:
            items = await self._enrich_entities(items, fetch_spec)

        total = await self._tenant_repository.count(filter_param=merge_filter)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0
        return PaginatedResponse[TenantEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: TenantFilterParameter) -> int:
        return await self._tenant_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: TenantFilterParameter) -> bool:
        return await self._tenant_repository.exists(filter_param=filter_params)

    async def _enrich_entities(self, entities: list[TenantEntity], fetch_spec: TenantFetchSpec) -> list[TenantEntity]:
        if not entities:
            return entities

        if fetch_spec.parent_tenant:
            related_ids = set(e.parent_tenant_id for e in entities if e.parent_tenant_id is not None)
            if related_ids:
                related = await self.find_all(
                    TenantFilterParameter(in_={TenantFilterField.id: list(related_ids)}),  # pyright: ignore[reportCallIssue]
                )
                parent_map: dict[int, TenantEntity] = {t.id: t for t in related if t.id is not None}

            for entity in entities:
                if entity.parent_tenant_id is not None:
                    entity.parent_tenant = parent_map.get(entity.parent_tenant_id)

        if fetch_spec.children_tenants:
            children_map: dict[int, list[TenantEntity]] = defaultdict[int, list[TenantEntity]](list)

            all_tenants = await self.find_all(
                TenantFilterParameter(null={TenantFilterField.parent_tenant_id: False}),
            )
            for t in all_tenants:
                if t.parent_tenant_id is not None:
                    children_map[t.parent_tenant_id].append(t)

            for entity in entities:
                if entity.id is not None:
                    entity.children_tenants = children_map.get(entity.id, [])

        return entities

    async def find_all_by_ids(self, ids: list[int], *, fetch_spec: TenantFetchSpec | None = None) -> list[TenantEntity]:
        entities = await self._tenant_repository.find_all(
            filter_param=TenantFilterParameter(in_={TenantFilterField.id: list[int](set[int](ids))})  # pyright: ignore[reportCallIssue]
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities
