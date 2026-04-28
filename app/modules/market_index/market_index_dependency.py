from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.market_index.application.market_index_domain_service import MarketIndexDomainService
from app.modules.market_index.application.market_index_query_service import MarketIndexQueryService
from app.modules.market_index.domain.market_index_repository import IndexCompositionRepository, MarketIndexRepository
from app.modules.market_index.market_index_query_dependency import (
    get_index_composition_repository,
    get_market_index_query_service,
    get_market_index_repository,
)


def get_market_index_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    market_index_repository: Annotated[MarketIndexRepository, Depends(get_market_index_repository)],
    index_composition_repository: Annotated[IndexCompositionRepository, Depends(get_index_composition_repository)],
    query_service: Annotated[MarketIndexQueryService, Depends(get_market_index_query_service)],
) -> MarketIndexDomainService:
    return MarketIndexDomainService(session, market_index_repository, index_composition_repository, query_service)


MarketIndexDomainServiceDep = Annotated[MarketIndexDomainService, Depends(get_market_index_domain_service)]
