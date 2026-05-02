from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class CompanyOfficerFilterField(StrEnum):
    id = "id"
    officer_name = "name"
    position = "position"
    ownership_percent = "ownership_percent"
    quantity = "quantity"
    updated_date = "updated_date"
    stock_id = "stock_id"


class CompanyOfficerFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in CompanyOfficerFilterField)


class CompanyOfficerPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in CompanyOfficerFilterField)
