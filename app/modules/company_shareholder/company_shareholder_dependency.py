from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_shareholder.application.company_shareholder_domain_service import (
    CompanyShareholderDomainService,
)
from app.modules.company_shareholder.company_shareholder_query_dependency import (
    CompanyShareholderQueryServiceDep,
    get_company_shareholder_repository,
)
from app.modules.company_shareholder.domain.company_shareholder_repository import CompanyShareholderRepository
from app.modules.stock.stock_query_dependency import StockQueryServiceDep


def get_company_shareholder_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    company_shareholder_repository: Annotated[
        CompanyShareholderRepository, Depends(get_company_shareholder_repository)
    ],
    query_service: CompanyShareholderQueryServiceDep,
    stock_query_service: StockQueryServiceDep,
) -> CompanyShareholderDomainService:
    return CompanyShareholderDomainService(
        session=session,
        company_shareholder_repository=company_shareholder_repository,
        query_service=query_service,
        stock_query_service=stock_query_service,
    )


CompanyShareholderDomainServiceDep = Annotated[
    CompanyShareholderDomainService, Depends(get_company_shareholder_domain_service)
]
