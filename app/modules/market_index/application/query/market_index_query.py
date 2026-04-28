from enum import StrEnum
from typing import ClassVar

from app.common.base_schema import FilterQueryParameter, PaginationQueryParameter


class MarketIndexFilterField(StrEnum):
    id = "id"
    symbol = "symbol"
    market_index_name = "name"
    group = "group"
    record_status = "record_status"
    created_at = "created_at"
    updated_at = "updated_at"
    created_by = "created_by"
    updated_by = "updated_by"


class MarketIndexFilterParameter(FilterQueryParameter):
    filterable_fields: ClassVar[set[str]] = set(c.value for c in MarketIndexFilterField)


class MarketIndexPaginationParameter(PaginationQueryParameter):
    orderable_fields: ClassVar[set[str]] = set(c.value for c in MarketIndexFilterField)
