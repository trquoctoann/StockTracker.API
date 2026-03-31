from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.permission.application.permission_query_service import PermissionQueryService
from app.modules.permission.domain.permission_repository import PermissionRepository
from app.modules.permission.infrastructure.persistence.permission_repository_impl import PermissionRepositoryImpl


async def get_permission_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> PermissionRepository:
    return PermissionRepositoryImpl(session)


def get_permission_query_service(
    permission_repository: Annotated[PermissionRepository, Depends(get_permission_repository)],
) -> PermissionQueryService:
    return PermissionQueryService(permission_repository)


PermissionQueryServiceDep = Annotated[PermissionQueryService, Depends(get_permission_query_service)]
