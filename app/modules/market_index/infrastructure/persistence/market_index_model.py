from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Index

from app.common.base_model import BaseNonAuditableSQLModelWithID, BaseSQLModelWithID
from app.common.enum import RecordStatus


class MarketIndexModel(BaseSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "market_index"

    symbol: str = Field(nullable=False, max_length=50)
    name: str = Field(nullable=False, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    group: str | None = Field(default=None, max_length=100)
    record_status: RecordStatus = Field(default=RecordStatus.ENABLED, nullable=False)

    __table_args__ = (
        Index("ix_market_index_group", "group"),
        UniqueConstraint("symbol", name="uix_market_index_symbol"),
    )


class IndexCompositionModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "index_composition"

    market_index_id: int = Field(nullable=False, foreign_key="market_index.id")
    stock_id: int = Field(nullable=False, foreign_key="stock.id")

    __table_args__ = (
        Index("ix_index_composition_market_index_id", "market_index_id"),
        Index("ix_index_composition_stock_id", "stock_id"),
    )
