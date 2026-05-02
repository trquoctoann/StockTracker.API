from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_officer.application.company_officer_domain_service import CompanyOfficerDomainService
from app.modules.company_officer.company_officer_query_dependency import (
    CompanyOfficerQueryServiceDep,
    get_company_officer_repository,
)
from app.modules.company_officer.domain.company_officer_repository import CompanyOfficerRepository
from app.modules.stock.stock_query_dependency import StockQueryServiceDep


def get_company_officer_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    company_officer_repository: Annotated[CompanyOfficerRepository, Depends(get_company_officer_repository)],
    query_service: CompanyOfficerQueryServiceDep,
    stock_query_service: StockQueryServiceDep,
) -> CompanyOfficerDomainService:
    return CompanyOfficerDomainService(session, company_officer_repository, query_service, stock_query_service)


CompanyOfficerDomainServiceDep = Annotated[CompanyOfficerDomainService, Depends(get_company_officer_domain_service)]
