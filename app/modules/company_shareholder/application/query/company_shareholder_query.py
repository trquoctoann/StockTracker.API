from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class CompanyShareholderFilterField(StrEnum):
    id = "id"
    shareholder_name = "name"
    quantity = "quantity"
    ownership_percent = "ownership_percent"
    updated_date = "updated_date"
    stock_id = "stock_id"


class CompanyShareholderFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in CompanyShareholderFilterField)


class CompanyShareholderPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in CompanyShareholderFilterField)
