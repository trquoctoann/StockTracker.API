from datetime import date

from pydantic import BaseModel


class CompanyNewsEntity(BaseModel):
    id: int | None = None
    title: str
    image_url: str | None = None
    source_url: str | None = None
    public_date: date | None = None
    language: str | None = None
    price_change_percent: float | None = None
    data_source_id: str | None = None
    stock_id: int
