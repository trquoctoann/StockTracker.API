from datetime import datetime

from pydantic import BaseModel

from app.common.enum import RecordStatus, RoleScope, RoleType
from app.modules.permission.domain.permission_entity import PermissionEntity


class RolePermissionEntity(BaseModel):
    id: int | None = None
    role_id: int
    permission_id: int


class RoleEntity(BaseModel):
    id: int | None = None
    type: RoleType
    scope: RoleScope
    name: str
    description: str | None = None
    record_status: RecordStatus
    version: int
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    permissions: list[PermissionEntity] | None = None
