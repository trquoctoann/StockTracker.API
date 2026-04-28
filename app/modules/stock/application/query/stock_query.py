from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class StockFilterField(StrEnum):
    id = "id"
    symbol = "symbol"
    stock_name = "name"
    short_name = "short_name"
    exchange = "exchange"
    type = "type"
    record_status = "record_status"
    created_at = "created_at"
    updated_at = "updated_at"
    created_by = "created_by"
    updated_by = "updated_by"


class StockFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in StockFilterField)


class StockPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in StockFilterField)
