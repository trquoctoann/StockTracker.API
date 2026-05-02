import math
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.exception.exception import NotFoundException
from app.modules.company_news.application.query.company_news_query import (
    CompanyNewsFilterField,
    CompanyNewsFilterParameter,
    CompanyNewsPaginationParameter,
)
from app.modules.company_news.domain.company_news_entity import CompanyNewsEntity
from app.modules.company_news.domain.company_news_repository import CompanyNewsRepository


@dataclass(frozen=True, slots=True)
class CompanyNewsFetchSpec:
    pass


class CompanyNewsQueryService(QueryService[CompanyNewsEntity, CompanyNewsFetchSpec]):
    def __init__(self, company_news_repository: CompanyNewsRepository) -> None:
        self._company_news_repository = company_news_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyNewsFetchSpec | None = None
    ) -> CompanyNewsEntity | None:
        entities = await self._company_news_repository.find_all(
            filter_param=CompanyNewsFilterParameter(eq={CompanyNewsFilterField.id: id})
        )
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyNewsFetchSpec | None = None
    ) -> CompanyNewsEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.company_news.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self,
        filter_params: CompanyNewsFilterParameter | None = None,
        *,
        fetch_spec: CompanyNewsFetchSpec | None = None,
    ) -> list[CompanyNewsEntity]:
        return await self._company_news_repository.find_all(filter_param=filter_params)

    async def find_all_by_stock_id(self, stock_id: int) -> list[CompanyNewsEntity]:
        return await self._company_news_repository.find_all(
            filter_param=CompanyNewsFilterParameter(eq={CompanyNewsFilterField.stock_id: stock_id})
        )

    async def find_page(
        self,
        filter_params: CompanyNewsFilterParameter | None,
        pagination_params: CompanyNewsPaginationParameter,
        *,
        fetch_spec: CompanyNewsFetchSpec | None = None,
    ) -> PaginatedResponse[CompanyNewsEntity]:
        items = await self._company_news_repository.find_all(
            filter_param=filter_params, pagination_param=pagination_params
        )

        total = await self._company_news_repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[CompanyNewsEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: CompanyNewsFilterParameter) -> int:
        return await self._company_news_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: CompanyNewsFilterParameter) -> bool:
        return await self._company_news_repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self, entities: Sequence[CompanyNewsEntity], fetch_spec: CompanyNewsFetchSpec | None = None
    ) -> list[CompanyNewsEntity]:
        return list(entities)
