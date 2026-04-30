import math
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.exception.exception import NotFoundException
from app.modules.company_profile.application.query.company_profile_query import (
    CompanyProfileFilterField,
    CompanyProfileFilterParameter,
    CompanyProfilePaginationParameter,
)
from app.modules.company_profile.domain.company_profile_entity import CompanyProfileEntity
from app.modules.company_profile.domain.company_profile_repository import CompanyProfileRepository


@dataclass(frozen=True, slots=True)
class CompanyProfileFetchSpec:
    pass


class CompanyProfileQueryService(QueryService[CompanyProfileEntity, CompanyProfileFetchSpec]):
    def __init__(self, company_profile_repository: CompanyProfileRepository) -> None:
        self._company_profile_repository = company_profile_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyProfileFetchSpec | None = None
    ) -> CompanyProfileEntity | None:
        entities = await self._company_profile_repository.find_all(
            filter_param=CompanyProfileFilterParameter(eq={CompanyProfileFilterField.id: id})
        )
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyProfileFetchSpec | None = None
    ) -> CompanyProfileEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.company_profile.not_found", params={"id": str(id)})
        return entity

    async def find_by_stock_id(self, stock_id: int) -> CompanyProfileEntity | None:
        entities = await self._company_profile_repository.find_all(
            filter_param=CompanyProfileFilterParameter(eq={CompanyProfileFilterField.stock_id: stock_id})
        )
        return entities[0] if entities else None

    async def find_all(
        self,
        filter_params: CompanyProfileFilterParameter | None = None,
        *,
        fetch_spec: CompanyProfileFetchSpec | None = None,
    ) -> list[CompanyProfileEntity]:
        return await self._company_profile_repository.find_all(filter_param=filter_params)

    async def find_page(
        self,
        filter_params: CompanyProfileFilterParameter | None,
        pagination_params: CompanyProfilePaginationParameter,
        *,
        fetch_spec: CompanyProfileFetchSpec | None = None,
    ) -> PaginatedResponse[CompanyProfileEntity]:
        items = await self._company_profile_repository.find_all(
            filter_param=filter_params, pagination_param=pagination_params
        )

        total = await self._company_profile_repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[CompanyProfileEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: CompanyProfileFilterParameter) -> int:
        return await self._company_profile_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: CompanyProfileFilterParameter) -> bool:
        return await self._company_profile_repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self, entities: Sequence[CompanyProfileEntity], fetch_spec: CompanyProfileFetchSpec | None = None
    ) -> list[CompanyProfileEntity]:
        return list(entities)
