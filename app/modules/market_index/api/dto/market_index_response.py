from datetime import datetime

from app.common.base_schema import BaseResponse
from app.common.enum import RecordStatus, StockExchange, StockType


class ResponseStock(BaseResponse):
    id: int
    symbol: str
    name: str
    short_name: str | None
    exchange: StockExchange
    type: StockType


class ResponseMarketIndex(BaseResponse):
    id: int
    symbol: str
    name: str
    description: str | None
    group: str | None
    record_status: RecordStatus
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    stocks: list[ResponseStock] | None
