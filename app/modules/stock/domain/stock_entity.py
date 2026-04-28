from datetime import datetime

from pydantic import BaseModel

from app.common.enum import RecordStatus, StockExchange, StockType
from app.modules.industry.domain.industry_entity import IndustryEntity


class StockIndustryEntity(BaseModel):
    id: int | None = None
    stock_id: int
    industry_id: int


class StockEntity(BaseModel):
    id: int | None = None
    symbol: str
    name: str
    short_name: str | None = None
    exchange: StockExchange
    type: StockType
    record_status: RecordStatus
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    industries: list[IndustryEntity] | None = None
