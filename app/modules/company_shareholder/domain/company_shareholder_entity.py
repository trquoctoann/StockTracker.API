from datetime import date

from pydantic import BaseModel


class CompanyShareholderEntity(BaseModel):
    id: int | None = None
    name: str
    quantity: int | None = None
    ownership_percent: float | None = None
    updated_date: date | None = None
    data_source_id: str | None = None
    stock_id: int
