import math
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.common.cache import CacheService
from app.common.cache_version_keys import get_price_history_bars_cache_key
from app.common.enum import PriceInterval
from app.exception.exception import NotFoundException
from app.modules.stock_price_history.application.query.stock_price_history_query import (
    StockPriceHistoryFilterField,
    StockPriceHistoryFilterParameter,
    StockPriceHistoryPaginationParameter,
)
from app.modules.stock_price_history.domain.stock_price_history_entity import StockPriceHistoryEntity
from app.modules.stock_price_history.domain.stock_price_history_repository import StockPriceHistoryRepository


@dataclass(frozen=True, slots=True)
class StockPriceHistoryFetchSpec:
    pass


class StockPriceHistoryQueryService(QueryService[StockPriceHistoryEntity, StockPriceHistoryFetchSpec]):
    def __init__(
        self,
        stock_price_history_repository: StockPriceHistoryRepository,
        cache_service: CacheService,
    ) -> None:
        self._repository = stock_price_history_repository
        self._cache = cache_service

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: StockPriceHistoryFetchSpec | None = None
    ) -> StockPriceHistoryEntity | None:
        entities = await self._repository.find_all(
            filter_param=StockPriceHistoryFilterParameter(eq={StockPriceHistoryFilterField.id: id})
        )
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: StockPriceHistoryFetchSpec | None = None
    ) -> StockPriceHistoryEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.stock_price_history.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self,
        filter_params: StockPriceHistoryFilterParameter | None = None,
        *,
        fetch_spec: StockPriceHistoryFetchSpec | None = None,
    ) -> list[StockPriceHistoryEntity]:
        return await self._repository.find_all(filter_param=filter_params)

    async def find_page(
        self,
        filter_params: StockPriceHistoryFilterParameter | None,
        pagination_params: StockPriceHistoryPaginationParameter,
        *,
        fetch_spec: StockPriceHistoryFetchSpec | None = None,
    ) -> PaginatedResponse[StockPriceHistoryEntity]:
        items = await self._repository.find_all(filter_param=filter_params, pagination_param=pagination_params)
        total = await self._repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[StockPriceHistoryEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def find_bars(
        self, stock_id: int, interval: PriceInterval, *, limit: int = 60
    ) -> list[StockPriceHistoryEntity]:
        cache_key = get_price_history_bars_cache_key(stock_id, interval.value, limit)
        cached = await self._cache.get_many_model(cache_key, StockPriceHistoryEntity)
        if cached is not None:
            return cached

        pagination = StockPriceHistoryPaginationParameter(limit=limit, offset=0, order_by="-time")
        entities = await self._repository.find_all(
            filter_param=StockPriceHistoryFilterParameter(
                eq={
                    StockPriceHistoryFilterField.stock_id: stock_id,
                    StockPriceHistoryFilterField.interval: interval,
                }
            ),
            pagination_param=pagination,
        )

        if entities:
            await self._cache.set_many_model(cache_key, entities, StockPriceHistoryEntity, ttl=60)

        return entities

    async def count(self, filter_params: StockPriceHistoryFilterParameter) -> int:
        return await self._repository.count(filter_param=filter_params)

    async def exists(self, filter_params: StockPriceHistoryFilterParameter) -> bool:
        return await self._repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self,
        entities: Sequence[StockPriceHistoryEntity],
        fetch_spec: StockPriceHistoryFetchSpec | None = None,
    ) -> list[StockPriceHistoryEntity]:
        return list(entities)
