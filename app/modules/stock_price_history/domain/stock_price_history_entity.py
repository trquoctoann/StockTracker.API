from datetime import datetime

from pydantic import BaseModel

from app.common.enum import PriceInterval


class StockPriceHistoryEntity(BaseModel):
    id: int | None = None
    time: datetime
    interval: PriceInterval
    open: float
    high: float
    low: float
    close: float
    volume: float
    stock_id: int
