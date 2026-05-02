from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_affiliation.application.company_affiliation_query_service import (
    CompanyAffiliationQueryService,
)
from app.modules.company_affiliation.domain.company_affiliation_repository import CompanyAffiliationRepository
from app.modules.company_affiliation.infrastructure.persistence.company_affiliation_repository_impl import (
    CompanyAffiliationRepositoryImpl,
)


def get_company_affiliation_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompanyAffiliationRepository:
    return CompanyAffiliationRepositoryImpl(session)


def get_company_affiliation_query_service(
    company_affiliation_repository: Annotated[
        CompanyAffiliationRepository, Depends(get_company_affiliation_repository)
    ],
) -> CompanyAffiliationQueryService:
    return CompanyAffiliationQueryService(company_affiliation_repository)


CompanyAffiliationQueryServiceDep = Annotated[
    CompanyAffiliationQueryService, Depends(get_company_affiliation_query_service)
]
