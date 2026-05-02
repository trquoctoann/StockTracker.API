from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_affiliation.application.company_affiliation_domain_service import (
    CompanyAffiliationDomainService,
)
from app.modules.company_affiliation.company_affiliation_query_dependency import (
    CompanyAffiliationQueryServiceDep,
    get_company_affiliation_repository,
)
from app.modules.company_affiliation.domain.company_affiliation_repository import CompanyAffiliationRepository
from app.modules.stock.stock_query_dependency import StockQueryServiceDep


def get_company_affiliation_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    company_affiliation_repository: Annotated[
        CompanyAffiliationRepository, Depends(get_company_affiliation_repository)
    ],
    query_service: CompanyAffiliationQueryServiceDep,
    stock_query_service: StockQueryServiceDep,
) -> CompanyAffiliationDomainService:
    return CompanyAffiliationDomainService(session, company_affiliation_repository, query_service, stock_query_service)


CompanyAffiliationDomainServiceDep = Annotated[
    CompanyAffiliationDomainService, Depends(get_company_affiliation_domain_service)
]
