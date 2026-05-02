import math
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.exception.exception import NotFoundException
from app.modules.company_affiliation.application.query.company_affiliation_query import (
    CompanyAffiliationFilterField,
    CompanyAffiliationFilterParameter,
    CompanyAffiliationPaginationParameter,
)
from app.modules.company_affiliation.domain.company_affiliation_entity import CompanyAffiliationEntity
from app.modules.company_affiliation.domain.company_affiliation_repository import CompanyAffiliationRepository


@dataclass(frozen=True, slots=True)
class CompanyAffiliationFetchSpec:
    pass


class CompanyAffiliationQueryService(QueryService[CompanyAffiliationEntity, CompanyAffiliationFetchSpec]):
    def __init__(self, company_affiliation_repository: CompanyAffiliationRepository) -> None:
        self._company_affiliation_repository = company_affiliation_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyAffiliationFetchSpec | None = None
    ) -> CompanyAffiliationEntity | None:
        entities = await self._company_affiliation_repository.find_all(
            filter_param=CompanyAffiliationFilterParameter(eq={CompanyAffiliationFilterField.id: id})
        )
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyAffiliationFetchSpec | None = None
    ) -> CompanyAffiliationEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.company_affiliation.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self,
        filter_params: CompanyAffiliationFilterParameter | None = None,
        *,
        fetch_spec: CompanyAffiliationFetchSpec | None = None,
    ) -> list[CompanyAffiliationEntity]:
        return await self._company_affiliation_repository.find_all(filter_param=filter_params)

    async def find_all_by_stock_id(self, stock_id: int) -> list[CompanyAffiliationEntity]:
        return await self._company_affiliation_repository.find_all(
            filter_param=CompanyAffiliationFilterParameter(eq={CompanyAffiliationFilterField.stock_id: stock_id})
        )

    async def find_page(
        self,
        filter_params: CompanyAffiliationFilterParameter | None,
        pagination_params: CompanyAffiliationPaginationParameter,
        *,
        fetch_spec: CompanyAffiliationFetchSpec | None = None,
    ) -> PaginatedResponse[CompanyAffiliationEntity]:
        items = await self._company_affiliation_repository.find_all(
            filter_param=filter_params, pagination_param=pagination_params
        )

        total = await self._company_affiliation_repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[CompanyAffiliationEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: CompanyAffiliationFilterParameter) -> int:
        return await self._company_affiliation_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: CompanyAffiliationFilterParameter) -> bool:
        return await self._company_affiliation_repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self, entities: Sequence[CompanyAffiliationEntity], fetch_spec: CompanyAffiliationFetchSpec | None = None
    ) -> list[CompanyAffiliationEntity]:
        return list(entities)
