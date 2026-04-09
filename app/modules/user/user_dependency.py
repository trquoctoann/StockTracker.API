from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.cache import CacheServiceDep
from app.core.config import settings
from app.core.database import get_session
from app.modules.role.role_query_dependency import RoleQueryServiceDep
from app.modules.tenant.tenant_query_dependency import TenantQueryServiceDep
from app.modules.user.application.user_domain_service import UserDomainService
from app.modules.user.application.user_query_service import UserQueryService
from app.modules.user.domain.identity_provider import IdentityProvider
from app.modules.user.domain.user_repository import UserRepository, UserRoleRepository
from app.modules.user.infrastructure.external.keycloak_identity_provider import KeycloakIdentityProvider
from app.modules.user.user_query_dependency import get_user_query_service, get_user_repository, get_user_role_repository


def get_identity_provider() -> IdentityProvider:
    return KeycloakIdentityProvider.build(
        server_url=settings.OIDC_KEYCLOAK_SERVER_URL,
        realm_name=settings.OIDC_KEYCLOAK_REALM,
        username=settings.OIDC_KEYCLOAK_ADMIN_USERNAME,
        password=settings.OIDC_KEYCLOAK_ADMIN_PASSWORD,
        client_id=settings.OIDC_KEYCLOAK_CLIENT_ID,
        client_secret_key=settings.OIDC_KEYCLOAK_CLIENT_SECRET,
        verify=settings.OIDC_KEYCLOAK_VERIFY_TLS,
    )


def get_user_domain_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    user_role_repository: Annotated[UserRoleRepository, Depends(get_user_role_repository)],
    query_service: Annotated[UserQueryService, Depends(get_user_query_service)],
    tenant_query_service: TenantQueryServiceDep,
    role_query_service: RoleQueryServiceDep,
    identity_provider: Annotated[IdentityProvider, Depends(get_identity_provider)],
    cache: CacheServiceDep,
) -> UserDomainService:
    return UserDomainService(
        session,
        user_repository,
        user_role_repository,
        query_service,
        tenant_query_service,
        role_query_service,
        identity_provider,
        cache,
    )


UserDomainServiceDep = Annotated[UserDomainService, Depends(get_user_domain_service)]
