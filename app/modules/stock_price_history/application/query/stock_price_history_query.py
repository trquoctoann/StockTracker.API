from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class StockPriceHistoryFilterField(StrEnum):
    id = "id"
    time = "time"
    interval = "interval"
    open = "open"
    high = "high"
    low = "low"
    close = "close"
    volume = "volume"
    stock_id = "stock_id"


class StockPriceHistoryFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in StockPriceHistoryFilterField)


class StockPriceHistoryPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[frozenset[str]] = frozenset(c.value for c in StockPriceHistoryFilterField)
