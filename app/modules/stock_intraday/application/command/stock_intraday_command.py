from datetime import datetime

from pydantic import Field

from app.common.base_schema import BaseCommand
from app.common.enum import MatchType


class UpsertStockIntradayCommand(BaseCommand):
    time: datetime
    price: float
    volume: float = Field(default=0.0, ge=0)
    match_type: MatchType
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int
