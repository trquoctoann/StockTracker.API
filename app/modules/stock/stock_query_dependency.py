from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.industry.industry_query_dependency import IndustryQueryServiceDep
from app.modules.stock.application.stock_query_service import StockQueryService
from app.modules.stock.domain.stock_repository import StockIndustryRepository, StockRepository
from app.modules.stock.infrastructure.persistence.stock_repository_impl import (
    StockIndustryRepositoryImpl,
    StockRepositoryImpl,
)


def get_stock_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> StockRepository:
    return StockRepositoryImpl(session)


def get_stock_industry_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> StockIndustryRepository:
    return StockIndustryRepositoryImpl(session)


def get_stock_query_service(
    stock_repository: Annotated[StockRepository, Depends(get_stock_repository)],
    stock_industry_repository: Annotated[StockIndustryRepository, Depends(get_stock_industry_repository)],
    industry_query_service: IndustryQueryServiceDep,
) -> StockQueryService:
    return StockQueryService(stock_repository, stock_industry_repository, industry_query_service)


StockQueryServiceDep = Annotated[StockQueryService, Depends(get_stock_query_service)]
