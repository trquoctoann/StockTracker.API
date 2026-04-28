from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.common.auth.context_token_codec import ContextTokenCodecImpl, ContextTokenPayload
from app.common.cache import get_cache_service
from app.common.enum import RoleScope
from app.core.database import get_session
from app.main import create_app
from app.modules.industry.application.industry_domain_service import IndustryDomainService
from app.modules.industry.application.industry_query_service import IndustryQueryService
from app.modules.industry.industry_dependency import get_industry_domain_service
from app.modules.industry.industry_query_dependency import get_industry_query_service, get_industry_repository
from app.modules.market_index.application.market_index_domain_service import MarketIndexDomainService
from app.modules.market_index.application.market_index_query_service import MarketIndexQueryService
from app.modules.market_index.market_index_dependency import get_market_index_domain_service
from app.modules.market_index.market_index_query_dependency import (
    get_index_composition_repository,
    get_market_index_query_service,
    get_market_index_repository,
)
from app.modules.permission.application.permission_query_service import PermissionQueryService
from app.modules.permission.permission_dependency import get_permission_query_service, get_permission_repository
from app.modules.role.application.role_domain_service import RoleDomainService
from app.modules.role.application.role_query_service import RoleQueryService
from app.modules.role.infrastructure.persistence.role_repository_impl import RolePermissionRepository
from app.modules.role.role_dependency import get_role_domain_service
from app.modules.role.role_query_dependency import (
    get_role_permission_repository,
    get_role_query_service,
    get_role_repository,
)
from app.modules.stock.application.stock_domain_service import StockDomainService
from app.modules.stock.application.stock_query_service import StockQueryService
from app.modules.stock.stock_dependency import get_stock_domain_service
from app.modules.stock.stock_query_dependency import (
    get_stock_industry_repository,
    get_stock_query_service,
    get_stock_repository,
)
from app.modules.tenant.application.tenant_domain_service import TenantDomainService
from app.modules.tenant.application.tenant_query_service import TenantQueryService
from app.modules.tenant.tenant_dependency import get_tenant_domain_service
from app.modules.tenant.tenant_query_dependency import get_tenant_query_service, get_tenant_repository
from app.modules.user.application.user_domain_service import UserDomainService
from app.modules.user.application.user_query_service import UserQueryService
from app.modules.user.user_dependency import get_identity_provider, get_user_domain_service
from app.modules.user.user_query_dependency import get_user_query_service, get_user_repository, get_user_role_repository
from tests.support.factories import (
    DEFAULT_USER_ID,
)
from tests.support.fakes import FakeCacheService, FakeIdentityProvider


@pytest.fixture()
def mock_session():
    return AsyncMock()


@pytest.fixture()
def fake_cache():
    return FakeCacheService()


@pytest.fixture()
def fake_identity_provider():
    return FakeIdentityProvider(fixed_user_id=str(DEFAULT_USER_ID))


@pytest.fixture()
def mock_user_repository():
    return AsyncMock()


@pytest.fixture()
def mock_user_role_repository():
    return AsyncMock()


@pytest.fixture()
def mock_user_query_service():
    return AsyncMock(spec=UserQueryService)


@pytest.fixture()
def mock_user_domain_service():
    return AsyncMock(spec=UserDomainService)


@pytest.fixture()
def mock_role_repository():
    return AsyncMock()


@pytest.fixture()
def mock_role_permission_repository():
    return AsyncMock(spec=RolePermissionRepository)


@pytest.fixture()
def mock_role_query_service():
    return AsyncMock(spec=RoleQueryService)


@pytest.fixture()
def mock_role_domain_service():
    return AsyncMock(spec=RoleDomainService)


@pytest.fixture()
def mock_tenant_repository():
    return AsyncMock()


@pytest.fixture()
def mock_tenant_query_service():
    return AsyncMock(spec=TenantQueryService)


@pytest.fixture()
def mock_tenant_domain_service():
    return AsyncMock(spec=TenantDomainService)


@pytest.fixture()
def mock_permission_repository():
    return AsyncMock()


@pytest.fixture()
def mock_permission_query_service():
    return AsyncMock(spec=PermissionQueryService)


@pytest.fixture()
def mock_industry_repository():
    return AsyncMock()


@pytest.fixture()
def mock_industry_query_service():
    return AsyncMock(spec=IndustryQueryService)


@pytest.fixture()
def mock_industry_domain_service():
    return AsyncMock(spec=IndustryDomainService)


@pytest.fixture()
def mock_stock_repository():
    return AsyncMock()


@pytest.fixture()
def mock_stock_industry_repository():
    return AsyncMock()


@pytest.fixture()
def mock_stock_query_service():
    return AsyncMock(spec=StockQueryService)


@pytest.fixture()
def mock_stock_domain_service():
    return AsyncMock(spec=StockDomainService)


@pytest.fixture()
def mock_market_index_repository():
    return AsyncMock()


@pytest.fixture()
def mock_index_composition_repository():
    return AsyncMock()


@pytest.fixture()
def mock_market_index_query_service():
    return AsyncMock(spec=MarketIndexQueryService)


@pytest.fixture()
def mock_market_index_domain_service():
    return AsyncMock(spec=MarketIndexDomainService)


def _build_context_token(
    *,
    scope: RoleScope = RoleScope.ADMIN,
    tenant_id: int | None = None,
    permissions_bitmap: int = (1 << 50) - 1,
) -> str:
    codec = ContextTokenCodecImpl()
    token, _ = codec.encode(
        ContextTokenPayload(
            subject=str(DEFAULT_USER_ID),
            scope=scope,
            tenant_id=tenant_id,
            user_version=1,
            user_roles_version=1,
            role_versions={1: 1},
            permissions_bitmap=permissions_bitmap,
        )
    )
    return token


@pytest.fixture()
def admin_token() -> str:
    return _build_context_token()


@pytest.fixture()
def admin_auth_header(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
async def app_client(
    mock_session,
    fake_cache,
    fake_identity_provider,
    mock_user_repository,
    mock_user_role_repository,
    mock_user_query_service,
    mock_user_domain_service,
    mock_role_repository,
    mock_role_permission_repository,
    mock_role_query_service,
    mock_role_domain_service,
    mock_tenant_repository,
    mock_tenant_query_service,
    mock_tenant_domain_service,
    mock_permission_repository,
    mock_permission_query_service,
    mock_industry_repository,
    mock_industry_query_service,
    mock_industry_domain_service,
    mock_market_index_repository,
    mock_index_composition_repository,
    mock_market_index_query_service,
    mock_market_index_domain_service,
    mock_stock_repository,
    mock_stock_industry_repository,
    mock_stock_query_service,
    mock_stock_domain_service,
) -> AsyncIterator[AsyncClient]:
    from app.common.cache_version_keys import (
        get_role_version_cache_key,
        get_user_role_version_cache_key,
        get_user_version_cache_key,
    )

    await fake_cache.set(get_user_version_cache_key(str(DEFAULT_USER_ID)), "1")
    await fake_cache.set(get_user_role_version_cache_key(DEFAULT_USER_ID, RoleScope.ADMIN.value, None), "1")
    await fake_cache.set(get_role_version_cache_key(1), "1")

    app = create_app()

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_cache_service] = lambda: fake_cache
    app.dependency_overrides[get_identity_provider] = lambda: fake_identity_provider
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repository
    app.dependency_overrides[get_user_role_repository] = lambda: mock_user_role_repository
    app.dependency_overrides[get_user_query_service] = lambda: mock_user_query_service
    app.dependency_overrides[get_user_domain_service] = lambda: mock_user_domain_service
    app.dependency_overrides[get_role_repository] = lambda: mock_role_repository
    app.dependency_overrides[get_role_permission_repository] = lambda: mock_role_permission_repository
    app.dependency_overrides[get_role_query_service] = lambda: mock_role_query_service
    app.dependency_overrides[get_role_domain_service] = lambda: mock_role_domain_service
    app.dependency_overrides[get_tenant_repository] = lambda: mock_tenant_repository
    app.dependency_overrides[get_tenant_query_service] = lambda: mock_tenant_query_service
    app.dependency_overrides[get_tenant_domain_service] = lambda: mock_tenant_domain_service
    app.dependency_overrides[get_permission_repository] = lambda: mock_permission_repository
    app.dependency_overrides[get_permission_query_service] = lambda: mock_permission_query_service
    app.dependency_overrides[get_industry_repository] = lambda: mock_industry_repository
    app.dependency_overrides[get_industry_query_service] = lambda: mock_industry_query_service
    app.dependency_overrides[get_industry_domain_service] = lambda: mock_industry_domain_service
    app.dependency_overrides[get_stock_repository] = lambda: mock_stock_repository
    app.dependency_overrides[get_stock_industry_repository] = lambda: mock_stock_industry_repository
    app.dependency_overrides[get_stock_query_service] = lambda: mock_stock_query_service
    app.dependency_overrides[get_stock_domain_service] = lambda: mock_stock_domain_service
    app.dependency_overrides[get_market_index_repository] = lambda: mock_market_index_repository
    app.dependency_overrides[get_index_composition_repository] = lambda: mock_index_composition_repository
    app.dependency_overrides[get_market_index_query_service] = lambda: mock_market_index_query_service
    app.dependency_overrides[get_market_index_domain_service] = lambda: mock_market_index_domain_service

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
