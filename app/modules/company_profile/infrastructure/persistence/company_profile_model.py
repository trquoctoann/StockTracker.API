from datetime import date
from typing import ClassVar

from sqlmodel import Field, Index

from app.common.base_model import BaseNonAuditableSQLModelWithID


class CompanyProfileModel(BaseNonAuditableSQLModelWithID, table=True):
    __tablename__: ClassVar[str] = "company_profile"

    symbol: str = Field(nullable=False, max_length=50)
    business_code: str | None = Field(default=None, max_length=255)
    business_model: str | None = Field(default=None)
    founded_date: date | None = Field(default=None)
    charter_capital: float | None = Field(default=None)
    number_of_employees: int | None = Field(default=None)
    listing_date: date | None = Field(default=None)
    par_value: float | None = Field(default=None)
    listing_price: float | None = Field(default=None)
    listing_volume: float | None = Field(default=None)
    ceo_name: str | None = Field(default=None, max_length=255)
    ceo_position: str | None = Field(default=None, max_length=255)
    inspector_name: str | None = Field(default=None, max_length=255)
    inspector_position: str | None = Field(default=None, max_length=255)
    establishment_license: str | None = Field(default=None, max_length=255)
    tax_id: str | None = Field(default=None, max_length=255)
    auditor: str | None = Field(default=None, max_length=255)
    company_type: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=100)
    fax: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=255)
    branches: int | None = Field(default=None)
    history: str | None = Field(default=None)
    stock_id: int = Field(nullable=False, foreign_key="stock.id")

    __table_args__ = (Index("ix_company_profile_stock_id", "stock_id"),)
