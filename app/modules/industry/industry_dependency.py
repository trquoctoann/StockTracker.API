from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.industry.application.industry_domain_service import IndustryDomainService
from app.modules.industry.application.industry_query_service import IndustryQueryService
from app.modules.industry.domain.industry_repository import IndustryRepository
from app.modules.industry.industry_query_dependency import get_industry_query_service, get_industry_repository


def get_industry_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    industry_repository: Annotated[IndustryRepository, Depends(get_industry_repository)],
    query_service: Annotated[IndustryQueryService, Depends(get_industry_query_service)],
) -> IndustryDomainService:
    return IndustryDomainService(session, industry_repository, query_service)


IndustryDomainServiceDep = Annotated[IndustryDomainService, Depends(get_industry_domain_service)]
