from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_profile.application.company_profile_domain_service import CompanyProfileDomainService
from app.modules.company_profile.application.company_profile_query_service import CompanyProfileQueryService
from app.modules.company_profile.company_profile_query_dependency import (
    get_company_profile_query_service,
    get_company_profile_repository,
)
from app.modules.company_profile.domain.company_profile_repository import CompanyProfileRepository
from app.modules.stock.stock_query_dependency import StockQueryServiceDep


def get_company_profile_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    company_profile_repository: Annotated[CompanyProfileRepository, Depends(get_company_profile_repository)],
    query_service: Annotated[CompanyProfileQueryService, Depends(get_company_profile_query_service)],
    stock_query_service: StockQueryServiceDep,
) -> CompanyProfileDomainService:
    return CompanyProfileDomainService(session, company_profile_repository, query_service, stock_query_service)


CompanyProfileDomainServiceDep = Annotated[CompanyProfileDomainService, Depends(get_company_profile_domain_service)]
