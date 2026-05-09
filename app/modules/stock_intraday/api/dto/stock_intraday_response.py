from datetime import datetime

from app.common.base_schema import BaseResponse
from app.common.enum import MatchType


class ResponseStockIntraday(BaseResponse):
    id: int
    time: datetime
    price: float
    volume: float
    match_type: MatchType
    data_source_id: str | None
    stock_id: int
