from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache import CacheServiceDep
from app.core.database import get_session
from app.modules.stock.stock_query_dependency import StockQueryServiceDep
from app.modules.stock_price_history.application.stock_price_history_domain_service import (
    StockPriceHistoryDomainService,
)
from app.modules.stock_price_history.domain.stock_price_history_repository import StockPriceHistoryRepository
from app.modules.stock_price_history.stock_price_history_query_dependency import (
    get_stock_price_history_repository,
)


def get_stock_price_history_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[StockPriceHistoryRepository, Depends(get_stock_price_history_repository)],
    stock_query_service: StockQueryServiceDep,
    cache_service: CacheServiceDep,
) -> StockPriceHistoryDomainService:
    return StockPriceHistoryDomainService(session, repository, stock_query_service, cache_service)


StockPriceHistoryDomainServiceDep = Annotated[
    StockPriceHistoryDomainService, Depends(get_stock_price_history_domain_service)
]
