from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache import CacheServiceDep
from app.core.database import get_session
from app.modules.stock_intraday.application.stock_intraday_query_service import StockIntradayQueryService
from app.modules.stock_intraday.domain.stock_intraday_repository import StockIntradayRepository
from app.modules.stock_intraday.infrastructure.persistence.stock_intraday_repository_impl import (
    StockIntradayRepositoryImpl,
)


def get_stock_intraday_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StockIntradayRepository:
    return StockIntradayRepositoryImpl(session)


def get_stock_intraday_query_service(
    repository: Annotated[StockIntradayRepository, Depends(get_stock_intraday_repository)],
    cache_service: CacheServiceDep,
) -> StockIntradayQueryService:
    return StockIntradayQueryService(repository, cache_service)


StockIntradayQueryServiceDep = Annotated[StockIntradayQueryService, Depends(get_stock_intraday_query_service)]
