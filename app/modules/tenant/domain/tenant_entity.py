from datetime import datetime
from typing import Union

from pydantic import BaseModel

from app.common.enum import RecordStatus


class TenantEntity(BaseModel):
    id: int | None = None
    name: str
    path: str
    record_status: RecordStatus
    parent_tenant_id: int | None = None
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    parent_tenant: Union["TenantEntity", None] = None
    children_tenants: list["TenantEntity"] | None = None
