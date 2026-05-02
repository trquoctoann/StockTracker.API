from datetime import date
from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Index

from app.common.base_model import BaseNonAuditableSQLModelWithID


class CompanyShareholderModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "company_shareholder"

    name: str = Field(nullable=False, max_length=255)
    quantity: int | None = Field(default=None)
    ownership_percent: float | None = Field(default=None)
    updated_date: date | None = Field(default=None)
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int = Field(nullable=False, foreign_key="stock.id")

    __table_args__ = (
        Index("ix_company_shareholder_stock_id", "stock_id"),
        UniqueConstraint("stock_id", "data_source_id", name="uix_company_shareholder_stock_id_data_source_id"),
    )
