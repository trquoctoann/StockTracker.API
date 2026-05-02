from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_news.application.company_news_domain_service import (
    CompanyNewsDomainService,
)
from app.modules.company_news.company_news_query_dependency import (
    CompanyNewsQueryServiceDep,
    get_company_news_repository,
)
from app.modules.company_news.domain.company_news_repository import CompanyNewsRepository
from app.modules.stock.stock_query_dependency import StockQueryServiceDep


def get_company_news_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    company_news_repository: Annotated[CompanyNewsRepository, Depends(get_company_news_repository)],
    query_service: CompanyNewsQueryServiceDep,
    stock_query_service: StockQueryServiceDep,
) -> CompanyNewsDomainService:
    return CompanyNewsDomainService(session, company_news_repository, query_service, stock_query_service)


CompanyNewsDomainServiceDep = Annotated[CompanyNewsDomainService, Depends(get_company_news_domain_service)]
