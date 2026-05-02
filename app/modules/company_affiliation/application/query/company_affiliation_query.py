from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class CompanyAffiliationFilterField(StrEnum):
    id = "id"
    company_affiliation_name = "name"
    code = "code"
    type = "type"
    ownership_percent = "ownership_percent"
    stock_id = "stock_id"


class CompanyAffiliationFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in CompanyAffiliationFilterField)


class CompanyAffiliationPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in CompanyAffiliationFilterField)
