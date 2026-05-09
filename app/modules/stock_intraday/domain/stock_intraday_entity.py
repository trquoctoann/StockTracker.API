from datetime import datetime

from pydantic import BaseModel

from app.common.enum import MatchType


class StockIntradayEntity(BaseModel):
    id: int | None = None
    time: datetime
    price: float
    volume: float
    match_type: MatchType
    data_source_id: str | None = None
    stock_id: int
