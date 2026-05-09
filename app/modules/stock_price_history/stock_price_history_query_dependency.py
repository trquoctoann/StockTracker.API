from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache import CacheServiceDep
from app.core.database import get_session
from app.modules.stock_price_history.application.stock_price_history_query_service import (
    StockPriceHistoryQueryService,
)
from app.modules.stock_price_history.domain.stock_price_history_repository import StockPriceHistoryRepository
from app.modules.stock_price_history.infrastructure.persistence.stock_price_history_repository_impl import (
    StockPriceHistoryRepositoryImpl,
)


def get_stock_price_history_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StockPriceHistoryRepository:
    return StockPriceHistoryRepositoryImpl(session)


def get_stock_price_history_query_service(
    repository: Annotated[StockPriceHistoryRepository, Depends(get_stock_price_history_repository)],
    cache_service: CacheServiceDep,
) -> StockPriceHistoryQueryService:
    return StockPriceHistoryQueryService(repository, cache_service)


StockPriceHistoryQueryServiceDep = Annotated[
    StockPriceHistoryQueryService, Depends(get_stock_price_history_query_service)
]
