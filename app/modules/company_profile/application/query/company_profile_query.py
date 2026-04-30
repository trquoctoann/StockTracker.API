from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class CompanyProfileFilterField(StrEnum):
    id = "id"
    symbol = "symbol"
    business_code = "business_code"
    business_model = "business_model"
    founded_date = "founded_date"
    charter_capital = "charter_capital"
    number_of_employees = "number_of_employees"
    listing_date = "listing_date"
    par_value = "par_value"
    listing_price = "listing_price"
    listing_volume = "listing_volume"
    ceo_name = "ceo_name"
    ceo_position = "ceo_position"
    inspector_name = "inspector_name"
    inspector_position = "inspector_position"
    establishment_license = "establishment_license"
    tax_id = "tax_id"
    auditor = "auditor"
    company_type = "company_type"
    address = "address"
    phone = "phone"
    fax = "fax"
    email = "email"
    website = "website"
    branches = "branches"
    history = "history"
    stock_id = "stock_id"


class CompanyProfileFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in CompanyProfileFilterField)


class CompanyProfilePaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in CompanyProfileFilterField)
