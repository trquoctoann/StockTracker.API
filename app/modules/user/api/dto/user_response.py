import uuid
from datetime import datetime

from pydantic import EmailStr

from app.common.base_schema import BaseResponse
from app.common.enum import RecordStatus, RoleScope, UserStatus
from app.modules.role.api.dto.role_response import ResponseRole
from app.modules.tenant.api.dto.tenant_response import ResponseTenant


class ResponseUserRole(BaseResponse):
    id: int
    scope: RoleScope
    tenant_id: int | None
    role_ids: list[int]
    version: int

    tenant: ResponseTenant | None
    roles: list[ResponseRole] | None


class ResponseUser(BaseResponse):
    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str | None
    status: UserStatus
    record_status: RecordStatus
    version: int
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    user_roles: list[ResponseUserRole] | None
