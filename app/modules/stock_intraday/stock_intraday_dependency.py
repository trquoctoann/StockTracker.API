from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache import CacheServiceDep
from app.core.database import get_session
from app.modules.stock.stock_query_dependency import StockQueryServiceDep
from app.modules.stock_intraday.application.stock_intraday_domain_service import StockIntradayDomainService
from app.modules.stock_intraday.domain.stock_intraday_repository import StockIntradayRepository
from app.modules.stock_intraday.stock_intraday_query_dependency import get_stock_intraday_repository


def get_stock_intraday_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    repository: Annotated[StockIntradayRepository, Depends(get_stock_intraday_repository)],
    stock_query_service: StockQueryServiceDep,
    cache_service: CacheServiceDep,
) -> StockIntradayDomainService:
    return StockIntradayDomainService(session, repository, stock_query_service, cache_service)


StockIntradayDomainServiceDep = Annotated[StockIntradayDomainService, Depends(get_stock_intraday_domain_service)]
