from __future__ import annotations

import uuid
from datetime import datetime

from app.common.auth.principals import ContextPrincipal, IdentityPrincipal
from app.common.enum import RecordStatus, RoleScope, RoleType, StockExchange, StockType, UserStatus
from app.modules.company_profile.domain.company_profile_entity import CompanyProfileEntity
from app.modules.industry.domain.industry_entity import IndustryEntity
from app.modules.market_index.domain.market_index_entity import MarketIndexEntity
from app.modules.permission.domain.permission_entity import PermissionEntity
from app.modules.role.domain.role_entity import RoleEntity
from app.modules.stock.domain.stock_entity import StockEntity
from app.modules.tenant.domain.tenant_entity import TenantEntity
from app.modules.user.domain.user_entity import UserEntity, UserRoleEntity

_NOW = datetime(2025, 1, 15, 12, 0, 0, tzinfo=None)

DEFAULT_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEFAULT_USER_ID_STR = str(DEFAULT_USER_ID)


def make_user(
    *,
    id: uuid.UUID | None = None,
    username: str = "testuser",
    email: str = "test@example.com",
    first_name: str = "Test",
    last_name: str | None = "User",
    status: UserStatus = UserStatus.ACTIVE,
    record_status: RecordStatus = RecordStatus.ENABLED,
    version: int = 1,
    user_roles: list[UserRoleEntity] | None = None,
) -> UserEntity:
    return UserEntity(
        id=id or DEFAULT_USER_ID,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        status=status,
        record_status=record_status,
        version=version,
        created_at=_NOW,
        created_by="system",
        updated_at=_NOW,
        updated_by="system",
        user_roles=user_roles,
    )


def make_user_role(
    *,
    id: int = 1,
    scope: RoleScope = RoleScope.ADMIN,
    user_id: uuid.UUID | None = None,
    tenant_id: int | None = None,
    role_ids: list[int] | None = None,
    version: int = 1,
) -> UserRoleEntity:
    return UserRoleEntity(
        id=id,
        scope=scope,
        user_id=user_id or DEFAULT_USER_ID,
        tenant_id=tenant_id,
        role_ids=role_ids or [1],
        version=version,
    )


def make_role(
    *,
    id: int = 1,
    type: RoleType = RoleType.CUSTOM,
    scope: RoleScope = RoleScope.ADMIN,
    name: str = "Admin Role",
    description: str | None = "Test role",
    record_status: RecordStatus = RecordStatus.ENABLED,
    version: int = 1,
    permissions: list[PermissionEntity] | None = None,
) -> RoleEntity:
    return RoleEntity(
        id=id,
        type=type,
        scope=scope,
        name=name,
        description=description,
        record_status=record_status,
        version=version,
        created_at=_NOW,
        created_by="system",
        updated_at=_NOW,
        updated_by="system",
        permissions=permissions,
    )


def make_tenant(
    *,
    id: int = 1,
    name: str = "Test Tenant",
    path: str = "1.",
    record_status: RecordStatus = RecordStatus.ENABLED,
    parent_tenant_id: int | None = None,
) -> TenantEntity:
    return TenantEntity(
        id=id,
        name=name,
        path=path,
        record_status=record_status,
        parent_tenant_id=parent_tenant_id,
        created_at=_NOW,
        created_by="system",
        updated_at=_NOW,
        updated_by="system",
    )


def make_permission(
    *,
    id: int = 1,
    scope: RoleScope = RoleScope.ADMIN,
    code: str = "USER_READ",
) -> PermissionEntity:
    return PermissionEntity(id=id, scope=scope, code=code)


def make_context_principal(
    *,
    subject: str | None = None,
    scope: RoleScope = RoleScope.ADMIN,
    tenant_id: int | None = None,
    user_version: int = 1,
    user_roles_version: int = 1,
    role_versions: dict[int, int] | None = None,
    permissions_bitmap: int = (1 << 50) - 1,
) -> ContextPrincipal:
    return ContextPrincipal(
        subject=subject or DEFAULT_USER_ID_STR,
        scope=scope,
        tenant_id=tenant_id,
        user_version=user_version,
        user_roles_version=user_roles_version,
        role_versions=role_versions or {1: 1},
        permissions_bitmap=permissions_bitmap,
    )


def make_identity_principal(
    *,
    subject: str | None = None,
    username: str = "testuser",
    email: str = "test@example.com",
) -> IdentityPrincipal:
    return IdentityPrincipal(
        subject=subject or DEFAULT_USER_ID_STR,
        username=username,
        email=email,
    )


def make_industry(
    *,
    id: int = 1,
    code: str = "IND_001",
    name: str = "Technology",
    level: int = 1,
    record_status: RecordStatus = RecordStatus.ENABLED,
) -> IndustryEntity:
    return IndustryEntity(
        id=id,
        code=code,
        name=name,
        level=level,
        record_status=record_status,
        created_at=_NOW,
        created_by="system",
        updated_at=_NOW,
        updated_by="system",
    )


def make_stock(
    *,
    id: int = 1,
    symbol: str = "FPT",
    name: str = "FPT Corporation",
    short_name: str | None = "FPT",
    exchange: StockExchange = StockExchange.HSX,
    type: StockType = StockType.STOCK,
    record_status: RecordStatus = RecordStatus.ENABLED,
    industries: list[IndustryEntity] | None = None,
) -> StockEntity:
    return StockEntity(
        id=id,
        symbol=symbol,
        name=name,
        short_name=short_name,
        exchange=exchange,
        type=type,
        record_status=record_status,
        industries=industries,
        created_at=_NOW,
        created_by="system",
        updated_at=_NOW,
        updated_by="system",
    )


def make_market_index(
    *,
    id: int = 1,
    symbol: str = "VNINDEX",
    name: str = "VN-Index",
    description: str | None = "Vietnam Ho Chi Minh Index",
    group: str | None = "HOSE",
    record_status: RecordStatus = RecordStatus.ENABLED,
    stocks: list[StockEntity] | None = None,
) -> MarketIndexEntity:
    return MarketIndexEntity(
        id=id,
        symbol=symbol,
        name=name,
        description=description,
        group=group,
        record_status=record_status,
        stocks=stocks,
        created_at=_NOW,
        created_by="system",
        updated_at=_NOW,
        updated_by="system",
    )


def make_company_profile(
    *,
    id: int = 1,
    symbol: str = "FPT",
    stock_id: int = 1,
) -> CompanyProfileEntity:
    return CompanyProfileEntity(
        id=id,
        symbol=symbol,
        stock_id=stock_id,
    )
