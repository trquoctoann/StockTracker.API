import math
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.exception.exception import NotFoundException
from app.modules.company_shareholder.application.query.company_shareholder_query import (
    CompanyShareholderFilterField,
    CompanyShareholderFilterParameter,
    CompanyShareholderPaginationParameter,
)
from app.modules.company_shareholder.domain.company_shareholder_entity import CompanyShareholderEntity
from app.modules.company_shareholder.domain.company_shareholder_repository import CompanyShareholderRepository


@dataclass(frozen=True, slots=True)
class CompanyShareholderFetchSpec:
    pass


class CompanyShareholderQueryService(QueryService[CompanyShareholderEntity, CompanyShareholderFetchSpec]):
    def __init__(self, company_shareholder_repository: CompanyShareholderRepository) -> None:
        self._company_shareholder_repository = company_shareholder_repository

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyShareholderFetchSpec | None = None
    ) -> CompanyShareholderEntity | None:
        entities = await self._company_shareholder_repository.find_all(
            filter_param=CompanyShareholderFilterParameter(eq={CompanyShareholderFilterField.id: id})
        )
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: CompanyShareholderFetchSpec | None = None
    ) -> CompanyShareholderEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.company_shareholder.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self,
        filter_params: CompanyShareholderFilterParameter | None = None,
        *,
        fetch_spec: CompanyShareholderFetchSpec | None = None,
    ) -> list[CompanyShareholderEntity]:
        return await self._company_shareholder_repository.find_all(filter_param=filter_params)

    async def find_all_by_stock_id(self, stock_id: int) -> list[CompanyShareholderEntity]:
        return await self._company_shareholder_repository.find_all(
            filter_param=CompanyShareholderFilterParameter(eq={CompanyShareholderFilterField.stock_id: stock_id})
        )

    async def find_page(
        self,
        filter_params: CompanyShareholderFilterParameter | None,
        pagination_params: CompanyShareholderPaginationParameter,
        *,
        fetch_spec: CompanyShareholderFetchSpec | None = None,
    ) -> PaginatedResponse[CompanyShareholderEntity]:
        items = await self._company_shareholder_repository.find_all(
            filter_param=filter_params, pagination_param=pagination_params
        )

        total = await self._company_shareholder_repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[CompanyShareholderEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: CompanyShareholderFilterParameter) -> int:
        return await self._company_shareholder_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: CompanyShareholderFilterParameter) -> bool:
        return await self._company_shareholder_repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self, entities: Sequence[CompanyShareholderEntity], fetch_spec: CompanyShareholderFetchSpec | None = None
    ) -> list[CompanyShareholderEntity]:
        return list(entities)
