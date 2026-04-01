from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class TenantFilterField(StrEnum):
    id = "id"
    tenant_name = "name"
    path = "path"
    record_status = "record_status"
    parent_tenant_id = "parent_tenant_id"
    created_at = "created_at"
    updated_at = "updated_at"
    created_by = "created_by"
    updated_by = "updated_by"


class TenantFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in TenantFilterField)


class TenantPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in TenantFilterField)
