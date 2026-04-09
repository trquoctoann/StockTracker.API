from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.permission.permission_dependency import PermissionQueryServiceDep
from app.modules.role.application.role_domain_service import RoleDomainService
from app.modules.role.application.role_query_service import RoleQueryService
from app.modules.role.domain.role_repository import RoleRepository
from app.modules.role.infrastructure.persistence.role_repository_impl import RolePermissionRepository
from app.modules.role.role_query_dependency import (
    get_role_permission_repository,
    get_role_query_service,
    get_role_repository,
)


def get_role_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    role_repository: Annotated[RoleRepository, Depends(get_role_repository)],
    role_permission_repository: Annotated[RolePermissionRepository, Depends(get_role_permission_repository)],
    query_service: Annotated[RoleQueryService, Depends(get_role_query_service)],
    permission_query_service: PermissionQueryServiceDep,
) -> RoleDomainService:
    return RoleDomainService(
        session,
        role_repository,
        role_permission_repository,
        query_service,
        permission_query_service,
    )


RoleDomainServiceDep = Annotated[RoleDomainService, Depends(get_role_domain_service)]
