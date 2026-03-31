from datetime import datetime

from app.common.base_schema import BaseResponse
from app.common.enum import RecordStatus, RoleScope, RoleType


class ResponsePermission(BaseResponse):
    id: int
    scope: RoleScope
    code: str


class ResponseRole(BaseResponse):
    id: int
    type: RoleType
    scope: RoleScope
    name: str
    description: str | None
    record_status: RecordStatus
    version: int
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    permissions: list[ResponsePermission] | None
