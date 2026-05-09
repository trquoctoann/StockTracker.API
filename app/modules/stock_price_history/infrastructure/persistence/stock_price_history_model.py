from datetime import datetime
from typing import ClassVar

from sqlmodel import Field, Index, UniqueConstraint

from app.common.base_model import BaseNonAuditableSQLModelWithID
from app.common.enum import PriceInterval


class StockPriceHistoryModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "stock_price_history"

    time: datetime = Field(nullable=False)
    interval: PriceInterval = Field(nullable=False)
    open: float = Field(nullable=False)
    high: float = Field(nullable=False)
    low: float = Field(nullable=False)
    close: float = Field(nullable=False)
    volume: float = Field(nullable=False, default=0.0)
    stock_id: int = Field(nullable=False, foreign_key="stock.id")

    __table_args__ = (
        UniqueConstraint("stock_id", "time", "interval", name="uix_stock_price_history_stock_time_interval"),
        Index("ix_stock_price_history_stock_interval_time", "stock_id", "interval", "time"),
    )
