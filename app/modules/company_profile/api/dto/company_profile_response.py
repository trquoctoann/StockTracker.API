from datetime import date

from app.common.base_schema import BaseResponse


class ResponseCompanyProfile(BaseResponse):
    id: int
    symbol: str
    business_code: str | None
    business_model: str | None
    founded_date: date | None
    charter_capital: float | None
    number_of_employees: int | None
    listing_date: date | None
    par_value: float | None
    listing_price: float | None
    listing_volume: float | None
    ceo_name: str | None
    ceo_position: str | None
    inspector_name: str | None
    inspector_position: str | None
    establishment_license: str | None
    tax_id: str | None
    auditor: str | None
    company_type: str | None
    address: str | None
    phone: str | None
    fax: str | None
    email: str | None
    website: str | None
    branches: int | None
    history: str | None
    stock_id: int
