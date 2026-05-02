from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.company_shareholder.application.company_shareholder_query_service import (
    CompanyShareholderQueryService,
)
from app.modules.company_shareholder.domain.company_shareholder_repository import CompanyShareholderRepository
from app.modules.company_shareholder.infrastructure.persistence.company_shareholder_repository_impl import (
    CompanyShareholderRepositoryImpl,
)


def get_company_shareholder_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CompanyShareholderRepository:
    return CompanyShareholderRepositoryImpl(session)


def get_company_shareholder_query_service(
    company_shareholder_repository: Annotated[
        CompanyShareholderRepository, Depends(get_company_shareholder_repository)
    ],
) -> CompanyShareholderQueryService:
    return CompanyShareholderQueryService(company_shareholder_repository)


CompanyShareholderQueryServiceDep = Annotated[
    CompanyShareholderQueryService, Depends(get_company_shareholder_query_service)
]
