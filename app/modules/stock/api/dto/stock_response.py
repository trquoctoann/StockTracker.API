from datetime import datetime

from app.common.base_schema import BaseResponse
from app.common.enum import RecordStatus, StockExchange, StockType


class ResponseIndustry(BaseResponse):
    id: int
    code: str
    name: str
    level: int


class ResponseStock(BaseResponse):
    id: int
    symbol: str
    name: str
    short_name: str | None
    exchange: StockExchange
    type: StockType
    record_status: RecordStatus
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    industries: list[ResponseIndustry] | None
