from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class CompanyEventFilterField(StrEnum):
    id = "id"
    event_title = "title"
    public_date = "public_date"
    issue_date = "issue_date"
    record_date = "record_date"
    exright_date = "exright_date"
    stock_id = "stock_id"


class CompanyEventFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in CompanyEventFilterField)


class CompanyEventPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in CompanyEventFilterField)
