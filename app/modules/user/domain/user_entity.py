import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.common.enum import RecordStatus, RoleScope, UserStatus
from app.modules.role.domain.role_entity import RoleEntity
from app.modules.tenant.domain.tenant_entity import TenantEntity


class UserRoleEntity(BaseModel):
    id: int | None = None
    scope: RoleScope
    user_id: uuid.UUID
    tenant_id: int | None = None
    role_ids: list[int]
    version: int

    tenant: TenantEntity | None = None
    roles: list[RoleEntity] | None = None


class UserEntity(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str | None = None
    status: UserStatus
    record_status: RecordStatus
    version: int
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    user_roles: list[UserRoleEntity] | None = None
