from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class StockIntradayFilterField(StrEnum):
    id = "id"
    time = "time"
    price = "price"
    volume = "volume"
    match_type = "match_type"
    data_source_id = "data_source_id"
    stock_id = "stock_id"


class StockIntradayFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in StockIntradayFilterField)


class StockIntradayPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[frozenset[str]] = frozenset(c.value for c in StockIntradayFilterField)
