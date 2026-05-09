from datetime import datetime

from app.common.base_schema import BaseResponse
from app.common.enum import PriceInterval


class ResponseStockPriceHistory(BaseResponse):
    id: int
    time: datetime
    interval: PriceInterval
    open: float
    high: float
    low: float
    close: float
    volume: float
    stock_id: int
