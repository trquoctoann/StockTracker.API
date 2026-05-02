import math
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.exception.exception import NotFoundException
from app.modules.company_event.application.query.company_event_query import (
    CompanyEventFilterField,
    CompanyEventFilterParameter,
    CompanyEventPaginationParameter,
)
from app.modules.company_event.domain.company_event_entity import CompanyEventEntity
from app.modules.company_event.domain.company_event_repository import CompanyEventRepository


@dataclass(frozen=True, slots=True)
class CompanyEventFetchSpec:
    pass


class CompanyEventQueryService(QueryService[CompanyEventEntity, CompanyEventFetchSpec]):
    def __init__(self, company_event_repository: CompanyEventRepository) -> None:
        self._company_event_repository = company_event_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyEventFetchSpec | None = None
    ) -> CompanyEventEntity | None:
        entities = await self._company_event_repository.find_all(
            filter_param=CompanyEventFilterParameter(eq={CompanyEventFilterField.id: id})
        )
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyEventFetchSpec | None = None
    ) -> CompanyEventEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.company_event.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self,
        filter_params: CompanyEventFilterParameter | None = None,
        *,
        fetch_spec: CompanyEventFetchSpec | None = None,
    ) -> list[CompanyEventEntity]:
        return await self._company_event_repository.find_all(filter_param=filter_params)

    async def find_all_by_stock_id(self, stock_id: int) -> list[CompanyEventEntity]:
        return await self._company_event_repository.find_all(
            filter_param=CompanyEventFilterParameter(eq={CompanyEventFilterField.stock_id: stock_id})
        )

    async def find_page(
        self,
        filter_params: CompanyEventFilterParameter | None,
        pagination_params: CompanyEventPaginationParameter,
        *,
        fetch_spec: CompanyEventFetchSpec | None = None,
    ) -> PaginatedResponse[CompanyEventEntity]:
        items = await self._company_event_repository.find_all(
            filter_param=filter_params, pagination_param=pagination_params
        )

        total = await self._company_event_repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[CompanyEventEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: CompanyEventFilterParameter) -> int:
        return await self._company_event_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: CompanyEventFilterParameter) -> bool:
        return await self._company_event_repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self, entities: Sequence[CompanyEventEntity], fetch_spec: CompanyEventFetchSpec | None = None
    ) -> list[CompanyEventEntity]:
        return list(entities)
