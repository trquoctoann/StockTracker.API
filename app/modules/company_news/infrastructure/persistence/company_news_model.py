from datetime import date
from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Index

from app.common.base_model import BaseNonAuditableSQLModelWithID


class CompanyNewsModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "company_news"

    title: str = Field(nullable=False, max_length=500)
    image_url: str | None = Field(default=None, max_length=500)
    source_url: str | None = Field(default=None, max_length=500)
    public_date: date | None = Field(default=None)
    language: str | None = Field(default=None, max_length=50)
    price_change_percent: float | None = Field(default=None)
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int = Field(nullable=False, foreign_key="stock.id")

    __table_args__ = (
        Index("ix_company_news_stock_id", "stock_id"),
        UniqueConstraint("stock_id", "data_source_id", name="uix_company_news_stock_id_data_source_id"),
    )
