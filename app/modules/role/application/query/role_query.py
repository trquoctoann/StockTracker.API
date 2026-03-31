from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class RoleFilterField(StrEnum):
    id = "id"
    type = "type"
    scope = "scope"
    role_name = "name"
    description = "description"
    record_status = "record_status"
    version = "version"
    created_at = "created_at"
    updated_at = "updated_at"
    created_by = "created_by"
    updated_by = "updated_by"


class RoleFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in RoleFilterField)


class RolePaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in RoleFilterField)
