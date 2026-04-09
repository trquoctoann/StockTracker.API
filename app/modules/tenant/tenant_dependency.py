from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.tenant.application.tenant_domain_service import TenantDomainService
from app.modules.tenant.application.tenant_query_service import TenantQueryService
from app.modules.tenant.domain.tenant_repository import TenantRepository
from app.modules.tenant.tenant_query_dependency import (
    get_tenant_query_service,
    get_tenant_repository,
)
from app.modules.user.user_dependency import UserDomainServiceDep


def get_tenant_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_repository: Annotated[TenantRepository, Depends(get_tenant_repository)],
    query_service: Annotated[TenantQueryService, Depends(get_tenant_query_service)],
    user_domain_service: UserDomainServiceDep,
) -> TenantDomainService:
    return TenantDomainService(session, tenant_repository, query_service, user_domain_service)


TenantDomainServiceDep = Annotated[TenantDomainService, Depends(get_tenant_domain_service)]
