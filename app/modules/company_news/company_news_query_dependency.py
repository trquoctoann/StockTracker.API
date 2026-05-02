from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_news.application.company_news_query_service import (
    CompanyNewsQueryService,
)
from app.modules.company_news.domain.company_news_repository import CompanyNewsRepository
from app.modules.company_news.infrastructure.persistence.company_news_repository_impl import (
    CompanyNewsRepositoryImpl,
)


def get_company_news_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompanyNewsRepository:
    return CompanyNewsRepositoryImpl(session)


def get_company_news_query_service(
    company_news_repository: Annotated[CompanyNewsRepository, Depends(get_company_news_repository)],
) -> CompanyNewsQueryService:
    return CompanyNewsQueryService(company_news_repository)


CompanyNewsQueryServiceDep = Annotated[CompanyNewsQueryService, Depends(get_company_news_query_service)]
