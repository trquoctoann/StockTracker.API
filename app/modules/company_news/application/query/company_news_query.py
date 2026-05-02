from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class CompanyNewsFilterField(StrEnum):
    id = "id"
    news_title = "title"
    public_date = "public_date"
    language = "language"
    price_change_percent = "price_change_percent"
    stock_id = "stock_id"


class CompanyNewsFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in CompanyNewsFilterField)


class CompanyNewsPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in CompanyNewsFilterField)
