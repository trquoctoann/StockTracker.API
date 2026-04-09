from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.tenant.application.tenant_query_service import TenantQueryService
from app.modules.tenant.domain.tenant_repository import TenantRepository
from app.modules.tenant.infrastructure.persistence.tenant_repository_impl import TenantRepositoryImpl


def get_tenant_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> TenantRepository:
    return TenantRepositoryImpl(session)


def get_tenant_query_service(
    tenant_repository: Annotated[TenantRepository, Depends(get_tenant_repository)],
) -> TenantQueryService:
    return TenantQueryService(tenant_repository)


TenantQueryServiceDep = Annotated[TenantQueryService, Depends(get_tenant_query_service)]
