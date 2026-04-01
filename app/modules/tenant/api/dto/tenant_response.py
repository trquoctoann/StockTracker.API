from datetime import datetime
from typing import Union

from app.common.base_schema import BaseResponse
from app.common.enum import RecordStatus


class ResponseTenant(BaseResponse):
    id: int
    name: str
    path: str
    record_status: RecordStatus
    parent_tenant_id: int | None
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    parent_tenant: Union["ResponseTenant", None] = None
    children_tenants: list["ResponseTenant"] | None = None
