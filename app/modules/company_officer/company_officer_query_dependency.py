from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_officer.application.company_officer_query_service import CompanyOfficerQueryService
from app.modules.company_officer.domain.company_officer_repository import CompanyOfficerRepository
from app.modules.company_officer.infrastructure.persistence.company_officer_repository_impl import (
    CompanyOfficerRepositoryImpl,
)


def get_company_officer_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompanyOfficerRepository:
    return CompanyOfficerRepositoryImpl(session)


def get_company_officer_query_service(
    company_officer_repository: Annotated[CompanyOfficerRepository, Depends(get_company_officer_repository)],
) -> CompanyOfficerQueryService:
    return CompanyOfficerQueryService(company_officer_repository)


CompanyOfficerQueryServiceDep = Annotated[CompanyOfficerQueryService, Depends(get_company_officer_query_service)]
