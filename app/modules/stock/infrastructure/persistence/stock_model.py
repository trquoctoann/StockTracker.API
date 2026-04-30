from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Index

from app.common.base_model import BaseNonAuditableSQLModelWithID, BaseSQLModelWithID
from app.common.enum import RecordStatus, StockExchange, StockType


class StockModel(BaseSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "stock"

    symbol: str = Field(nullable=False, max_length=20)
    name: str = Field(nullable=False, max_length=500)
    short_name: str | None = Field(default=None, max_length=255)
    exchange: StockExchange = Field(nullable=False)
    type: StockType = Field(nullable=False)
    record_status: RecordStatus = Field(default=RecordStatus.ENABLED, nullable=False)

    __table_args__ = (
        Index("ix_stock_exchange", "exchange"),
        Index("ix_stock_type", "type"),
        UniqueConstraint("symbol", name="uix_stock_symbol"),
    )


class StockIndustryModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "stock_industry"

    stock_id: int = Field(nullable=False, foreign_key="stock.id")
    industry_id: int = Field(nullable=False, foreign_key="industry.id")

    __table_args__ = (
        Index("ix_stock_industry_stock_id", "stock_id"),
        Index("ix_stock_industry_industry_id", "industry_id"),
    )
