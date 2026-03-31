from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class PermissionFilterField(StrEnum):
    id = "id"
    scope = "scope"
    code = "code"


class PermissionFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in PermissionFilterField)


class PermissionPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in PermissionFilterField)
