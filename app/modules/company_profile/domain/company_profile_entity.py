from datetime import date

from pydantic import BaseModel


class CompanyProfileEntity(BaseModel):
    id: int | None = None
    symbol: str
    business_code: str | None = None
    business_model: str | None = None
    founded_date: date | None = None
    charter_capital: float | None = None
    number_of_employees: int | None = None
    listing_date: date | None = None
    par_value: float | None = None
    listing_price: float | None = None
    listing_volume: float | None = None
    ceo_name: str | None = None
    ceo_position: str | None = None
    inspector_name: str | None = None
    inspector_position: str | None = None
    establishment_license: str | None = None
    tax_id: str | None = None
    auditor: str | None = None
    company_type: str | None = None
    address: str | None = None
    phone: str | None = None
    fax: str | None = None
    email: str | None = None
    website: str | None = None
    branches: int | None = None
    history: str | None = None
    stock_id: int
