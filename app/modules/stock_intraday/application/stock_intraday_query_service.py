import math
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from app.common.base_schema import PaginatedResponse
from app.common.base_service import QueryService
from app.common.cache import CacheService
from app.exception.exception import NotFoundException
from app.modules.stock_intraday.application.query.stock_intraday_query import (
    StockIntradayFilterField,
    StockIntradayFilterParameter,
    StockIntradayPaginationParameter,
)
from app.modules.stock_intraday.domain.stock_intraday_entity import StockIntradayEntity
from app.modules.stock_intraday.domain.stock_intraday_repository import StockIntradayRepository


@dataclass(frozen=True, slots=True)
class StockIntradayFetchSpec:
    pass


class StockIntradayQueryService(QueryService[StockIntradayEntity, StockIntradayFetchSpec]):
    def __init__(
        self,
        stock_intraday_repository: StockIntradayRepository,
        cache_service: CacheService,
    ) -> None:
        self._repository = stock_intraday_repository
        self._cache = cache_service

    async def find_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: StockIntradayFetchSpec | None = None
    ) -> StockIntradayEntity | None:
        entities = await self._repository.find_all(
            filter_param=StockIntradayFilterParameter(eq={StockIntradayFilterField.id: id})
        )
        return entities[0] if entities else None

    async def get_by_id(
        self, id: uuid.UUID | int, *, fetch_spec: StockIntradayFetchSpec | None = None
    ) -> StockIntradayEntity:
        entity = await self.find_by_id(id, fetch_spec=fetch_spec)
        if not entity:
            raise NotFoundException(message_key="errors.business.stock_intraday.not_found", params={"id": str(id)})
        return entity

    async def find_all(
        self,
        filter_params: StockIntradayFilterParameter | None = None,
        *,
        fetch_spec: StockIntradayFetchSpec | None = None,
    ) -> list[StockIntradayEntity]:
        return await self._repository.find_all(filter_param=filter_params)

    async def find_page(
        self,
        filter_params: StockIntradayFilterParameter | None,
        pagination_params: StockIntradayPaginationParameter,
        *,
        fetch_spec: StockIntradayFetchSpec | None = None,
    ) -> PaginatedResponse[StockIntradayEntity]:
        items = await self._repository.find_all(filter_param=filter_params, pagination_param=pagination_params)
        total = await self._repository.count(filter_param=filter_params)
        limit = pagination_params.limit
        page = pagination_params.offset // limit + 1 if limit else 1
        total_pages = math.ceil(total / limit) if limit else 0

        return PaginatedResponse[StockIntradayEntity](
            items=items,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    async def count(self, filter_params: StockIntradayFilterParameter) -> int:
        return await self._repository.count(filter_param=filter_params)

    async def exists(self, filter_params: StockIntradayFilterParameter) -> bool:
        return await self._repository.exists(filter_param=filter_params)

    async def _enrich_entities(
        self,
        entities: Sequence[StockIntradayEntity],
        fetch_spec: StockIntradayFetchSpec | None = None,
    ) -> list[StockIntradayEntity]:
        return list(entities)
