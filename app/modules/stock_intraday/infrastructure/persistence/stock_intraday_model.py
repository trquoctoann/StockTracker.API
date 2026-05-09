from datetime import datetime
from typing import ClassVar

from sqlmodel import Field, Index, UniqueConstraint

from app.common.base_model import BaseNonAuditableSQLModelWithID
from app.common.enum import MatchType


class StockIntradayModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "stock_intraday"

    time: datetime = Field(nullable=False)
    price: float = Field(nullable=False)
    volume: float = Field(nullable=False, default=0.0)
    match_type: MatchType = Field(nullable=False)
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int = Field(nullable=False, foreign_key="stock.id")

    __table_args__ = (
        UniqueConstraint("stock_id", "time", "data_source_id", name="uix_stock_intraday_stock_time_source"),
        Index("ix_stock_intraday_stock_id_time", "stock_id", "time"),
    )
