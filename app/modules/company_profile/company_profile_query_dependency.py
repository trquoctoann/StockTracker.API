from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_profile.application.company_profile_query_service import CompanyProfileQueryService
from app.modules.company_profile.domain.company_profile_repository import CompanyProfileRepository
from app.modules.company_profile.infrastructure.persistence.company_profile_repository_impl import (
    CompanyProfileRepositoryImpl,
)


def get_company_profile_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> CompanyProfileRepository:
    return CompanyProfileRepositoryImpl(session)


def get_company_profile_query_service(
    company_profile_repository: Annotated[CompanyProfileRepository, Depends(get_company_profile_repository)],
) -> CompanyProfileQueryService:
    return CompanyProfileQueryService(company_profile_repository)


CompanyProfileQueryServiceDep = Annotated[CompanyProfileQueryService, Depends(get_company_profile_query_service)]
