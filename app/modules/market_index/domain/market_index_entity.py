from datetime import datetime

from pydantic import BaseModel

from app.common.enum import RecordStatus
from app.modules.stock.domain.stock_entity import StockEntity


class IndexCompositionEntity(BaseModel):
    id: int | None = None
    market_index_id: int
    stock_id: int


class MarketIndexEntity(BaseModel):
    id: int | None = None
    symbol: str
    name: str
    description: str | None = None
    group: str | None = None
    record_status: RecordStatus
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    stocks: list[StockEntity] | None = None
