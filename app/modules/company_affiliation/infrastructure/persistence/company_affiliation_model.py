from typing import ClassVar

from sqlmodel import Field, Index, UniqueConstraint

from app.common.base_model import BaseNonAuditableSQLModelWithID


class CompanyAffiliationModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "company_affiliation"

    code: str | None = Field(default=None, max_length=50)
    name: str = Field(nullable=False, max_length=255)
    type: str | None = Field(default=None, max_length=50)
    ownership_percent: float | None = Field(default=None)
    data_source_id: str | None = Field(default=None, max_length=255)
    stock_id: int = Field(nullable=False, foreign_key="stock.id")

    __table_args__ = (
        Index("ix_company_affiliation_stock_id", "stock_id"),
        UniqueConstraint("stock_id", "data_source_id", name="uix_company_affiliation_stock_id_data_source_id"),
    )
