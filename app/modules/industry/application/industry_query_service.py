from __future__ import annotations

import math
import uuid
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.common.enum import RecordStatus
from app.exception.exception import NotFoundException
from app.modules.industry.application.query.industry_query import (
    IndustryFilterField,
    IndustryFilterParameter,
    IndustryPaginationParameter,
)
from app.modules.industry.domain.industry_entity import IndustryEntity
from app.modules.industry.domain.industry_repository import IndustryRepository


@dataclass(frozen=True, slots=True)
class IndustryFetchSpec:
    pass


class IndustryQueryService(QueryService[IndustryEntity, IndustryFetchSpec]):
    def __init__(self, industry_repository: IndustryRepository) -> None:
        self._industry_repository = industry_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: IndustryFetchSpec | None = None
    ) -> IndustryEntity | None:
        entities = await self._industry_repository.find_all(
            filter_param=IndustryFilterParameter(
                eq={IndustryFilterField.id: id},
                neq={IndustryFilterField.record_status: RecordStatus.DELETED},
            ),
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities[0] if entities else None

    async def get_by_id(self, id: uuid.UUID | int, *, fetch_spec: IndustryFetchSpec | None = None) -> IndustryEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.industry.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self, filter_params: IndustryFilterParameter | None = None, *, fetch_spec: IndustryFetchSpec | None = None
    ) -> list[IndustryEntity]:
        merge_filter = IndustryFilterParameter.merge_ops(
            filter_params,
            neq={IndustryFilterField.record_status: RecordStatus.DELETED},
        )
        entities = await self._industry_repository.find_all(filter_param=merge_filter)
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities

    async def find_page(
        self,
        filter_params: IndustryFilterParameter | None,
        pagination_params: IndustryPaginationParameter,
        *,
        fetch_spec: IndustryFetchSpec | None = None,
    ) -> PaginatedResponse[IndustryEntity]:
        merge_filter = IndustryFilterParameter.merge_ops(
            filter_params,
            neq={IndustryFilterField.record_status: RecordStatus.DELETED},
        )
        items = await self._industry_repository.find_all(filter_param=merge_filter, pagination_param=pagination_params)
        if fetch_spec:
            items = await self._enrich_entities(items, fetch_spec)

        total = await self._industry_repository.count(filter_param=merge_filter)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[IndustryEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: IndustryFilterParameter) -> int:
        return await self._industry_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: IndustryFilterParameter) -> bool:
        return await self._industry_repository.exists(filter_param=filter_params)

    async def find_all_by_ids(self, ids: list[int]) -> list[IndustryEntity]:
        return await self._industry_repository.find_all(
            filter_param=IndustryFilterParameter(
                in_={IndustryFilterField.id: list[int](set[int](ids))},  # pyright: ignore[reportCallIssue]
                neq={IndustryFilterField.record_status: RecordStatus.DELETED},
            ),
        )

    async def _enrich_entities(
        self, entities: list[IndustryEntity], fetch_spec: IndustryFetchSpec
    ) -> list[IndustryEntity]:
        return entities
