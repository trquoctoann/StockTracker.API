from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.stock.application.stock_domain_service import StockDomainService
from app.modules.stock.application.stock_query_service import StockQueryService
from app.modules.stock.domain.stock_repository import StockIndustryRepository, StockRepository
from app.modules.stock.stock_query_dependency import (
    get_stock_industry_repository,
    get_stock_query_service,
    get_stock_repository,
)


def get_stock_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    stock_repository: Annotated[StockRepository, Depends(get_stock_repository)],
    stock_industry_repository: Annotated[StockIndustryRepository, Depends(get_stock_industry_repository)],
    query_service: Annotated[StockQueryService, Depends(get_stock_query_service)],
) -> StockDomainService:
    return StockDomainService(session, stock_repository, stock_industry_repository, query_service)


StockDomainServiceDep = Annotated[StockDomainService, Depends(get_stock_domain_service)]
