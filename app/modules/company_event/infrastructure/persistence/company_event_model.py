from datetime import date
from typing import ClassVar

from sqlmodel import Field, Index, UniqueConstraint

from app.common.base_model import BaseNonAuditableSQLModelWithID


class CompanyEventModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "company_event"

    title: str = Field(nullable=False, max_length=500)
    public_date: date | None = Field(default=None)
    issue_date: date | None = Field(default=None)
    source_url: str | None = Field(default=None, max_length=500)
    record_date: date | None = Field(default=None)
    exright_date: date | None = Field(default=None)
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int = Field(nullable=False, foreign_key="stock.id")

    __table_args__ = (
        Index("ix_company_event_stock_id", "stock_id"),
        UniqueConstraint("stock_id", "data_source_id", name="uix_company_event_stock_id_data_source_id"),
    )
