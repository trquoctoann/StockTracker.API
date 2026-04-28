from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.market_index.application.market_index_query_service import MarketIndexQueryService
from app.modules.market_index.domain.market_index_repository import IndexCompositionRepository, MarketIndexRepository
from app.modules.market_index.infrastructure.persistence.market_index_repository_impl import (
    IndexCompositionRepositoryImpl,
    MarketIndexRepositoryImpl,
)
from app.modules.stock.stock_query_dependency import StockQueryServiceDep


def get_market_index_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> MarketIndexRepository:
    return MarketIndexRepositoryImpl(session)


def get_index_composition_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IndexCompositionRepository:
    return IndexCompositionRepositoryImpl(session)


def get_market_index_query_service(
    market_index_repository: Annotated[MarketIndexRepository, Depends(get_market_index_repository)],
    index_composition_repository: Annotated[IndexCompositionRepository, Depends(get_index_composition_repository)],
    stock_query_service: StockQueryServiceDep,
) -> MarketIndexQueryService:
    return MarketIndexQueryService(market_index_repository, index_composition_repository, stock_query_service)


MarketIndexQueryServiceDep = Annotated[MarketIndexQueryService, Depends(get_market_index_query_service)]
