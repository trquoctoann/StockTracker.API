from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.role.role_query_dependency import RoleQueryServiceDep
from app.modules.tenant.tenant_query_dependency import TenantQueryServiceDep
from app.modules.user.application.user_query_service import UserQueryService
from app.modules.user.domain.user_repository import UserRepository, UserRoleRepository
from app.modules.user.infrastructure.persistence.user_repository_impl import UserRepositoryImpl, UserRoleRepositoryImpl


async def get_user_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> UserRepository:
    return UserRepositoryImpl(session)


def get_user_role_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> UserRoleRepository:
    return UserRoleRepositoryImpl(session)


def get_user_query_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    user_role_repository: Annotated[UserRoleRepository, Depends(get_user_role_repository)],
    tenant_query_service: TenantQueryServiceDep,
    role_query_service: RoleQueryServiceDep,
) -> UserQueryService:
    return UserQueryService(user_repository, user_role_repository, tenant_query_service, role_query_service)


UserQueryServiceDep = Annotated[UserQueryService, Depends(get_user_query_service)]
