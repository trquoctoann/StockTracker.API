from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_event.application.company_event_domain_service import (
    CompanyEventDomainService,
)
from app.modules.company_event.company_event_query_dependency import (
    CompanyEventQueryServiceDep,
    get_company_event_repository,
)
from app.modules.company_event.domain.company_event_repository import CompanyEventRepository
from app.modules.stock.stock_query_dependency import StockQueryServiceDep


def get_company_event_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    company_event_repository: Annotated[CompanyEventRepository, Depends(get_company_event_repository)],
    query_service: CompanyEventQueryServiceDep,
    stock_query_service: StockQueryServiceDep,
) -> CompanyEventDomainService:
    return CompanyEventDomainService(session, company_event_repository, query_service, stock_query_service)


CompanyEventDomainServiceDep = Annotated[CompanyEventDomainService, Depends(get_company_event_domain_service)]
