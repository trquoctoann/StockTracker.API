from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_event.application.company_event_query_service import (
    CompanyEventQueryService,
)
from app.modules.company_event.domain.company_event_repository import CompanyEventRepository
from app.modules.company_event.infrastructure.persistence.company_event_repository_impl import (
    CompanyEventRepositoryImpl,
)


def get_company_event_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompanyEventRepository:
    return CompanyEventRepositoryImpl(session)


def get_company_event_query_service(
    company_event_repository: Annotated[CompanyEventRepository, Depends(get_company_event_repository)],
) -> CompanyEventQueryService:
    return CompanyEventQueryService(company_event_repository)


CompanyEventQueryServiceDep = Annotated[CompanyEventQueryService, Depends(get_company_event_query_service)]
