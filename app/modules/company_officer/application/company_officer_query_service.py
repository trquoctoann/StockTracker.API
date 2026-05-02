import math
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.exception.exception import NotFoundException
from app.modules.company_officer.application.query.company_officer_query import (
    CompanyOfficerFilterField,
    CompanyOfficerFilterParameter,
    CompanyOfficerPaginationParameter,
)
from app.modules.company_officer.domain.company_officer_entity import CompanyOfficerEntity
from app.modules.company_officer.domain.company_officer_repository import CompanyOfficerRepository


@dataclass(frozen=True, slots=True)
class CompanyOfficerFetchSpec:
    pass


class CompanyOfficerQueryService(QueryService[CompanyOfficerEntity, CompanyOfficerFetchSpec]):
    def __init__(self, company_officer_repository: CompanyOfficerRepository) -> None:
        self._company_officer_repository = company_officer_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyOfficerFetchSpec | None = None
    ) -> CompanyOfficerEntity | None:
        entities = await self._company_officer_repository.find_all(
            filter_param=CompanyOfficerFilterParameter(eq={CompanyOfficerFilterField.id: id})
        )
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyOfficerFetchSpec | None = None
    ) -> CompanyOfficerEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.company_officer.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self,
        filter_params: CompanyOfficerFilterParameter | None = None,
        *,
        fetch_spec: CompanyOfficerFetchSpec | None = None,
    ) -> list[CompanyOfficerEntity]:
        return await self._company_officer_repository.find_all(filter_param=filter_params)

    async def find_all_by_stock_id(self, stock_id: int) -> list[CompanyOfficerEntity]:
        return await self._company_officer_repository.find_all(
            filter_param=CompanyOfficerFilterParameter(eq={CompanyOfficerFilterField.stock_id: stock_id})
        )

    async def find_page(
        self,
        filter_params: CompanyOfficerFilterParameter | None,
        pagination_params: CompanyOfficerPaginationParameter,
        *,
        fetch_spec: CompanyOfficerFetchSpec | None = None,
    ) -> PaginatedResponse[CompanyOfficerEntity]:
        items = await self._company_officer_repository.find_all(
            filter_param=filter_params, pagination_param=pagination_params
        )

        total = await self._company_officer_repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[CompanyOfficerEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: CompanyOfficerFilterParameter) -> int:
        return await self._company_officer_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: CompanyOfficerFilterParameter) -> bool:
        return await self._company_officer_repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self, entities: Sequence[CompanyOfficerEntity], fetch_spec: CompanyOfficerFetchSpec | None = None
    ) -> list[CompanyOfficerEntity]:
        return list(entities)
