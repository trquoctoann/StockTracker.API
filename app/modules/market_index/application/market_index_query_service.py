from __future__ import annotations

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.common.enum import RecordStatus
from app.exception.exception import NotFoundException
from app.modules.market_index.application.query.market_index_query import (
    MarketIndexFilterField,
    MarketIndexFilterParameter,
    MarketIndexPaginationParameter,
)
from app.modules.market_index.domain.market_index_entity import MarketIndexEntity
from app.modules.market_index.domain.market_index_repository import IndexCompositionRepository, MarketIndexRepository
from app.modules.stock.application.stock_query_service import StockQueryService
from app.modules.stock.domain.stock_entity import StockEntity


@dataclass(frozen=True, slots=True)
class MarketIndexFetchSpec:
    stocks: bool = False


class MarketIndexQueryService(QueryService[MarketIndexEntity, MarketIndexFetchSpec]):
    def __init__(
        self,
        market_index_repository: MarketIndexRepository,
        index_composition_repository: IndexCompositionRepository,
        stock_query_service: StockQueryService,
    ) -> None:
        self._market_index_repository = market_index_repository
        self._index_composition_repository = index_composition_repository
        self._stock_query_service = stock_query_service

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: MarketIndexFetchSpec | None = None
    ) -> MarketIndexEntity | None:
        entities = await self._market_index_repository.find_all(
            filter_param=MarketIndexFilterParameter(
                eq={MarketIndexFilterField.id: id},
                neq={MarketIndexFilterField.record_status: RecordStatus.DELETED},
            ),
        )
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: MarketIndexFetchSpec | None = None
    ) -> MarketIndexEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.market_index.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self,
        filter_params: MarketIndexFilterParameter | None = None,
        *,
        fetch_spec: MarketIndexFetchSpec | None = None,
    ) -> list[MarketIndexEntity]:
        merge_filter = MarketIndexFilterParameter.merge_ops(
            filter_params,
            neq={MarketIndexFilterField.record_status: RecordStatus.DELETED},
        )
        entities = await self._market_index_repository.find_all(filter_param=merge_filter)
        if fetch_spec:
            entities = await self._enrich_entities(entities, fetch_spec)
        return entities

    async def find_page(
        self,
        filter_params: MarketIndexFilterParameter | None,
        pagination_params: MarketIndexPaginationParameter,
        *,
        fetch_spec: MarketIndexFetchSpec | None = None,
    ) -> PaginatedResponse[MarketIndexEntity]:
        merge_filter = MarketIndexFilterParameter.merge_ops(
            filter_params,
            neq={MarketIndexFilterField.record_status: RecordStatus.DELETED},
        )
        items = await self._market_index_repository.find_all(
            filter_param=merge_filter, pagination_param=pagination_params
        )
        if fetch_spec:
            items = await self._enrich_entities(items, fetch_spec)

        total = await self._market_index_repository.count(filter_param=merge_filter)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[MarketIndexEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: MarketIndexFilterParameter) -> int:
        return await self._market_index_repository.count(filter_param=filter_params)

    async def exists(self, filter_params: MarketIndexFilterParameter) -> bool:
        return await self._market_index_repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self, entities: list[MarketIndexEntity], fetch_spec: MarketIndexFetchSpec
    ) -> list[MarketIndexEntity]:
        if not entities:
            return entities

        if fetch_spec.stocks:
            index_ids = [e.id for e in entities if e.id is not None]
            if not index_ids:
                return entities

            compositions = await self._index_composition_repository.find_all_by_market_index_ids(index_ids)

            index_stock_map: dict[int, list[int]] = defaultdict(list)
            stock_ids: set[int] = set()
            for comp in compositions:
                index_stock_map[comp.market_index_id].append(comp.stock_id)
                stock_ids.add(comp.stock_id)

            stock_map: dict[int, StockEntity] = {}
            if stock_ids:
                stocks = await self._stock_query_service.find_all_by_ids(list(stock_ids))
                stock_map = {s.id: s for s in stocks if s.id is not None}

            for idx in entities:
                if idx.id is None:
                    continue
                stock_ids_for_index = index_stock_map.get(idx.id, [])
                idx.stocks = [stock_map[sid] for sid in stock_ids_for_index if sid in stock_map]

        return entities
