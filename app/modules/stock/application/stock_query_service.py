from __future__ import annotations

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.common.enum import RecordStatus
from app.exception.exception import NotFoundException
from app.modules.industry.application.industry_query_service import IndustryQueryService
from app.modules.industry.domain.industry_entity import IndustryEntity
from app.modules.stock.application.query.stock_query import (
    StockFilterField,
    StockFilterParameter,
    StockPaginationParameter,
)
from app.modules.stock.domain.stock_entity import StockEntity
from app.modules.stock.domain.stock_repository import StockIndustryRepository, StockRepository


@dataclass(frozen=True, slots=True)
class StockFetchSpec:
    industries: bool = False


class StockQueryService(QueryService[StockEntity, StockFetchSpec]):
    def __init__(
        self,
        stock_repository: StockRepository,
        stock_industry_repository: StockIndustryRepository,
        industry_query_service: IndustryQueryService,
    ) -> None:
        self._stock_repository = stock_repository
        self._stock_industry_repository = stock_industry_repository
        self._industry_query_service = industry_query_service

    async def find_by_id(self, id: uuid.UUID | int, *, fetch_spec: StockFetchSpec | None = None) -> StockEntity | None:
        entities = await self._stock_repository.find_all(
            filter_param=StockFilterParameter(
                eq={StockFilterField.id: id},
                neq={StockFilterField.record_status: RecordStatus.DELETED},
            ),
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities[0] if entities else None

    async def get_by_id(self, id: uuid.UUID | int, *, fetch_spec: StockFetchSpec | None = None) -> StockEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.stock.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self, filter_params: StockFilterParameter | None = None, *, fetch_spec: StockFetchSpec | None = None
    ) -> list[StockEntity]:
        merge_filter = StockFilterParameter.merge_ops(
            filter_params,
            neq={StockFilterField.record_status: RecordStatus.DELETED},
        )
        entities = await self._stock_repository.find_all(filter_param=merge_filter)
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities

    async def find_page(
        self,
        filter_params: StockFilterParameter | None,
        pagination_params: StockPaginationParameter,
        *,
        fetch_spec: StockFetchSpec | None = None,
    ) -> PaginatedResponse[StockEntity]:
        merge_filter = StockFilterParameter.merge_ops(
            filter_params,
            neq={StockFilterField.record_status: RecordStatus.DELETED},
        )
        items = await self._stock_repository.find_all(filter_param=merge_filter, pagination_param=pagination_params)
        if fetch_spec:
            items = await self._enrich_entities(items, fetch_spec)

        total = await self._stock_repository.count(filter_param=merge_filter)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[StockEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: StockFilterParameter) -> int:
        return await self._stock_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: StockFilterParameter) -> bool:
        return await self._stock_repository.exists(filter_param=filter_params)

    async def find_all_by_ids(self, ids: list[int], *, fetch_spec: StockFetchSpec | None = None) -> list[StockEntity]:
        entities = await self._stock_repository.find_all(
            filter_param=StockFilterParameter(
                in_={StockFilterField.id: list[int](set[int](ids))},  # pyright: ignore[reportCallIssue]
                neq={StockFilterField.record_status: RecordStatus.DELETED},
            ),
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities

    async def _enrich_entities(self, entities: list[StockEntity], fetch_spec: StockFetchSpec) -> list[StockEntity]:
        if not entities:
            return entities

        if fetch_spec.industries:
            stock_ids = [e.id for e in entities if e.id is not None]
            if not stock_ids:
                return entities

            stock_industries = await self._stock_industry_repository.find_all_by_stock_ids(stock_ids)

            stock_industry_map: dict[int, list[int]] = defaultdict(list)
            industry_ids: set[int] = set()
            for si in stock_industries:
                stock_industry_map[si.stock_id].append(si.industry_id)
                industry_ids.add(si.industry_id)

            industry_map: dict[int, IndustryEntity] = {}
            if industry_ids:
                industries = await self._industry_query_service.find_all_by_ids(list(industry_ids))
                industry_map = {i.id: i for i in industries if i.id is not None}

            for stock in entities:
                if stock.id is None:
                    continue
                industry_ids_for_stock = stock_industry_map.get(stock.id, [])
                stock.industries = [industry_map[iid] for iid in industry_ids_for_stock if iid in industry_map]

        return entities
