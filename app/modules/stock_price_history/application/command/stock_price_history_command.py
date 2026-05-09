from datetime import datetime

from pydantic import Field

from app.common.base_schema import BaseCommand
from app.common.enum import PriceInterval


class UpsertStockPriceHistoryCommand(BaseCommand):
    time: datetime
    interval: PriceInterval
    open: float
    high: float
    low: float
    close: float
    volume: float = Field(default=0.0, ge=0)
    stock_id: int
