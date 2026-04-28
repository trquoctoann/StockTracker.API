from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class IndustryFilterField(StrEnum):
    id = "id"
    code = "code"
    industry_name = "name"
    level = "level"
    record_status = "record_status"
    created_at = "created_at"
    updated_at = "updated_at"
    created_by = "created_by"
    updated_by = "updated_by"


class IndustryFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in IndustryFilterField)


class IndustryPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in IndustryFilterField)
