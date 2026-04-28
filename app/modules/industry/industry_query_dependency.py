from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.industry.application.industry_query_service import IndustryQueryService
from app.modules.industry.domain.industry_repository import IndustryRepository
from app.modules.industry.infrastructure.persistence.industry_repository_impl import IndustryRepositoryImpl


def get_industry_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> IndustryRepository:
    return IndustryRepositoryImpl(session)


def get_industry_query_service(
    industry_repository: Annotated[IndustryRepository, Depends(get_industry_repository)],
) -> IndustryQueryService:
    return IndustryQueryService(industry_repository)


IndustryQueryServiceDep = Annotated[IndustryQueryService, Depends(get_industry_query_service)]
